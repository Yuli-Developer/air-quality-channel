"""
Visual Director AI — multi-tier image generation.
Tier 1: ComfyUI (local Flux Schnell / SDXL Turbo)
Tier 2: Pollinations.ai (free fallback)
Tier 3: Animated gradient (final fallback)
"""

import os
import time
import json
import random
import logging
import urllib.parse
import requests
from config.settings import (
    IMAGES_DIR, USE_COMFYUI, COMFYUI_URL, IMAGE_TIER, SCENES_PER_VIDEO
)

logger = logging.getLogger(__name__)

# ── Anime style (original) ──────────────────────────────────────────────────

SHOT_TYPES = [
    "wide establishing shot",
    "close-up extreme facial expression",
    "low angle dramatic perspective",
    "over-the-shoulder shot",
    "aerial bird's-eye view",
    "dutch angle tilted frame",
    "extreme close-up with motion lines",
]

ANIME_STYLE = (
    "black and white manga anime storyboard, rough pencil sketch with clean inked outlines, "
    "dynamic cinematic composition, dramatic lighting and deep shadows, "
    "motion speed lines, intense emotional expression, "
    "hand-drawn storyboard aesthetic, panel framing, "
    "professional Japanese anime production storyboard, monochrome pencil look, "
    "sakuga-style action keyframe, NO color, NO flat design, NO 3D render, pencil and ink only"
)

# ── Master Finance News Broadcast style ────────────────────────────────────

FINANCE_NEWS_BASE = (
    "ultra realistic cinematic TV news broadcast, "
    "professional financial news studio, "
    "high-end Bloomberg/CNBC visual aesthetic, "
    "photorealistic newsroom environment, "
    "drastic dramatic lighting with blue and red accents, "
    "large LED wall displaying financial charts, breaking news graphics and market tickers, "
    "lower third chyron banner, live breaking news overlay, "
    "hyper detailed textures, sharp focus, cinematic depth of field, "
    "realistic skin textures, subtle film grain, professional camera framing, "
    "8k UHD, volumetric lighting, global illumination, realistic reflections, "
    "high contrast newsroom atmosphere, modern trading floor aesthetic, "
    "viral social media thumbnail style, high emotional impact, "
    "studio quality broadcast composition"
)

FINANCE_NEWS_NEGATIVE = (
    "low quality, blurry, cartoon, anime, painting, illustration, cgi, fake, "
    "distorted anatomy, extra limbs, ugly face, deformed hands, duplicate people, "
    "cross eyes, unrealistic lighting, oversaturated, flat image, cheap render, "
    "plastic skin, text errors, watermark, logo, typo, poor composition, pixelated, "
    "low detail, jpeg artifacts, overprocessed, unrealistic reflections, weird shadows, "
    "incorrect body proportions, out of frame, cropped face, stock image quality, "
    "boring scene, static composition, childish, toy-like, low realism"
)

FINANCE_CAMERA_ANGLES = [
    "close-up dramatic face shot",
    "wide angle newsroom shot",
    "aerial view of financial district",
    "low angle power shot",
    "cinematic over-the-shoulder shot",
    "handheld breaking news realism",
    "zoomed-in emotional reaction shot",
    "ultra wide cinematic frame",
    "security camera perspective",
    "helicopter shot over stock exchange",
]

FINANCE_LIGHTING = [
    "dramatic studio lighting",
    "neon blue financial lighting",
    "emergency red alert lighting",
    "high contrast cinematic lighting",
    "stormy dark atmosphere",
    "moody trading floor lights",
    "television studio glow",
    "realistic daylight through skyscrapers",
    "nighttime cyber finance aesthetic",
    "volumetric smoke lighting",
]

FINANCE_MOODS = [
    "panic", "financial collapse", "market euphoria", "fear and greed",
    "worldwide chaos", "viral internet frenzy", "luxury corruption",
    "crypto madness", "apocalyptic economy", "breaking global scandal",
    "high tension", "massive speculation", "world changing event",
    "billionaire drama", "financial warfare",
]

FINANCE_BOOSTERS = [
    "Reuters photography style", "Bloomberg terminal aesthetic",
    "cinematic documentary realism", "AP news photography",
    "Netflix documentary look", "Sony FX6 cinema camera",
    "Canon EOS R5 realism", "shallow depth of field",
    "IMAX cinematic composition", "high frequency detail",
    "ultra detailed newsroom", "trading floor panic",
    "viral thumbnail composition", "photorealistic cinematic storytelling",
    "real-world lighting", "moody newsroom atmosphere",
    "high-end production quality", "award-winning news photography",
    "realistic crowd reactions", "professional broadcast graphics",
]


def _build_finance_prompt(scene: dict, characters: str, portrait: bool = False) -> str:
    """Build prompt using the master finance news template."""
    scene_num   = scene.get("scene_number", 1)
    desc        = scene.get("storyboard_description", scene.get("narration_segment", ""))
    narration   = scene.get("narration_segment", "")

    # Headline from narration (first sentence, max 60 chars)
    headline = narration.split(".")[0].strip().upper()
    if len(headline) > 60:
        headline = headline[:57] + "..."

    # Cycle camera angle, lighting, mood deterministically per scene
    camera  = FINANCE_CAMERA_ANGLES[(scene_num - 1) % len(FINANCE_CAMERA_ANGLES)]
    light   = FINANCE_LIGHTING[(scene_num - 1) % len(FINANCE_LIGHTING)]
    mood    = FINANCE_MOODS[(scene_num - 1) % len(FINANCE_MOODS)]

    # Sample 6 booster keywords (seeded for reproducibility)
    rng      = random.Random(scene_num * 7)
    boosters = ", ".join(rng.sample(FINANCE_BOOSTERS, 6))

    # Portrait-specific composition keywords for 9:16 Shorts
    composition = (
        "VERTICAL 9:16 PORTRAIT COMPOSITION, tall narrow frame, "
        "subject centered and dominant in frame, close-up or medium shot, "
        "optimized for mobile phone full screen vertical viewing, "
        "no important content in top or bottom 15% of frame, "
    ) if portrait else ""

    return (
        f"{FINANCE_NEWS_BASE}, "
        f"{composition}"
        f'BREAKING NEWS: "{headline}", '
        f"scene showing {desc}, "
        f"financial chaos and market panic atmosphere, people reacting emotionally, "
        f"traders shocked, stock market graphics collapsing or exploding, "
        f"news graphics floating on screens, viral internet news energy, "
        f"foreground details: {characters}, "
        f"camera angle: {camera}, "
        f"lighting: {light}, "
        f"mood: {mood}, "
        f"realistic facial expressions, photorealistic humans, cinematic realism, "
        f"hyper detailed environment, no text artifacts, "
        f"viral finance news thumbnail composition, "
        f"{boosters}"
    )


def _build_prompt(scene: dict, characters: str, shot_type: str,
                  style: str = "anime", portrait: bool = False) -> str:
    if style == "news_broadcast":
        return _build_finance_prompt(scene, characters, portrait=portrait)
    # Anime default
    desc = scene.get("storyboard_description", scene.get("narration_segment", ""))
    return (
        f"{ANIME_STYLE}, {shot_type}, "
        f"SCENE: {desc}, "
        f"CHARACTERS: {characters}, "
        f"dynamic foreshortening, fast-paced anime action, "
        f"cinematic anime keyframes, manga panel energy"
    )


VISUAL_STYLES = {
    "anime":          ANIME_STYLE,
    "news_broadcast": FINANCE_NEWS_BASE,
}


# ── Tier 1: ComfyUI ────────────────────────────────────────────────────────

def _comfyui_generate(prompt: str, path: str, width: int, height: int, seed: int) -> bool:
    """Submit workflow to local ComfyUI server."""
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed, "steps": 4, "cfg": 1.0,
                "sampler_name": "euler", "scheduler": "simple",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "flux1-schnell.safetensors"}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "ugly, blurry, bad anatomy", "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode",
              "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"images": ["8", 0], "filename_prefix": "bw_scene"}},
    }
    try:
        r = requests.post(f"{COMFYUI_URL}/prompt",
                          json={"prompt": workflow}, timeout=10)
        r.raise_for_status()
        prompt_id = r.json()["prompt_id"]

        # Poll for completion
        for _ in range(120):
            time.sleep(2)
            hist = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=5).json()
            if prompt_id in hist:
                outputs = hist[prompt_id]["outputs"]
                for node_id, node_out in outputs.items():
                    if "images" in node_out:
                        img_info = node_out["images"][0]
                        img_url = f"{COMFYUI_URL}/view?filename={img_info['filename']}"
                        data = requests.get(img_url, timeout=30).content
                        with open(path, "wb") as f:
                            f.write(data)
                        logger.info(f"ComfyUI: saved {path}")
                        return True
        logger.warning("ComfyUI timeout waiting for image")
        return False
    except Exception as e:
        logger.warning(f"ComfyUI failed: {e}")
        return False


# ── Tier 2: Pollinations ───────────────────────────────────────────────────

def _pollinations_generate(prompt: str, path: str, width: int, height: int, seed: int,
                            negative: str = "") -> bool:
    encoded = urllib.parse.quote(prompt)
    neg_param = f"&negative={urllib.parse.quote(negative)}" if negative else ""
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux&seed={seed}{neg_param}"
    )
    backoffs = [30, 60, 90]   # seconds — longer waits for 429 rate limits
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            if len(r.content) < 5000:
                raise ValueError(f"Response too small ({len(r.content)} bytes)")
            with open(path, "wb") as f:
                f.write(r.content)
            return True
        except requests.exceptions.HTTPError as e:
            wait = backoffs[attempt]
            logger.warning(f"Pollinations attempt {attempt+1}/3: {e} — waiting {wait}s")
            if attempt < 2:
                time.sleep(wait)
        except Exception as e:
            logger.warning(f"Pollinations attempt {attempt+1}/3: {e}")
            if attempt < 2:
                time.sleep(backoffs[attempt])
    return False


# ── Tier 3: Gradient fallback ──────────────────────────────────────────────

def _gradient_fallback(path: str, scene_num: int, width: int, height: int):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (width, height), "#0A0A0A")
    draw = ImageDraw.Draw(img)
    draw.text((width // 2, height // 2), f"Scene {scene_num}",
              fill="#444444", anchor="mm")
    img.save(path)
    logger.warning(f"Used gradient fallback for scene {scene_num}")


# ── Public API ─────────────────────────────────────────────────────────────

def generate_scene_image(scene: dict, run_id: str, characters: str = "",
                          width: int = 1792, height: int = 1024,
                          style: str = "anime", portrait: bool = False) -> str:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    scene_num = scene["scene_number"]
    path = os.path.join(IMAGES_DIR, f"{run_id}_scene_{scene_num:02d}.png")

    shot_type = SHOT_TYPES[(scene_num - 1) % len(SHOT_TYPES)]
    prompt    = _build_prompt(scene, characters, shot_type, style, portrait)
    seed      = scene_num * 42

    logger.info(f"Scene {scene_num}: {shot_type} {'[portrait]' if portrait else ''}")

    success  = False
    negative = FINANCE_NEWS_NEGATIVE if style == "news_broadcast" else ""

    if USE_COMFYUI or IMAGE_TIER == "comfyui":
        success = _comfyui_generate(prompt, path, width, height, seed)

    if not success:
        success = _pollinations_generate(prompt, path, width, height, seed, negative)

    if not success:
        _gradient_fallback(path, scene_num, width, height)

    return path


def generate_all_images(story: dict, run_id: str,
                         width: int = 1792, height: int = 1024) -> list[str]:
    characters   = story.get("characters", "")
    style        = story.get("visual_style", "anime")
    shorts_only  = story.get("shorts_only", False)

    # Shorts-only: generate portrait 9:16 images natively
    if shorts_only:
        width, height = 1080, 1920
        portrait = True
    else:
        portrait = False

    image_paths = []

    for scene in story["scenes"]:
        path = generate_scene_image(scene, run_id, characters, width, height, style, portrait)
        image_paths.append(path)
        time.sleep(15)   # avoid 429 rate limits on Pollinations free tier

    story["image_paths"] = image_paths
    logger.info(f"Generated {len(image_paths)} images")
    return image_paths
