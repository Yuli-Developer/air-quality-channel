"""
Visual Director — AQI channel.
Generates city skyline images using Pollinations.ai (free Flux model).
Style: photorealistic smoggy/clear city skyline matching AQI level.
"""

import os
import time
import logging
import urllib.parse
import requests
from config.settings import IMAGES_DIR, SHORTS_WIDTH, SHORTS_HEIGHT

logger = logging.getLogger(__name__)

W, H = SHORTS_WIDTH, SHORTS_HEIGHT   # 1080 x 1920

_SKY_STYLE = {
    "Good":               "crystal clear blue sky, pristine air, golden sunlight",
    "Moderate":           "slightly hazy pale sky, soft diffused light",
    "Unhealthy for Some": "hazy orange-tinted sky, smog layer visible",
    "Unhealthy":          "heavy smog, orange-red hazy atmosphere, reduced visibility",
    "Very Unhealthy":     "thick toxic smog, dark orange purple haze, apocalyptic atmosphere",
    "Hazardous":          "extreme toxic smog, dark red brown sky, barely visible skyline, horror atmosphere",
}

AQI_STYLE_BASE = (
    "ultra realistic cinematic photography, "
    "city skyline aerial view, NO people, NO faces, "
    "photorealistic environment, dramatic atmospheric perspective, "
    "8k UHD, sharp focus, cinematic depth of field, "
    "VERTICAL 9:16 portrait composition, tall narrow frame"
)

AQI_NEGATIVE = (
    "cartoon, anime, painting, illustration, people, faces, human, "
    "text, watermark, logo, low quality, blurry, distorted"
)


def _build_aqi_prompt(scene: dict) -> str:
    city     = scene.get("city", "city")
    category = scene.get("category", "Moderate")
    sky      = _SKY_STYLE.get(category, "hazy sky")
    aqi      = scene.get("aqi", 100)
    drama = ""
    if aqi > 200:
        drama = "emergency atmosphere, hazard warning feeling, cinematic tension, "
    elif aqi > 150:
        drama = "ominous atmosphere, smog alert mood, "
    return (
        f"{AQI_STYLE_BASE}, "
        f"aerial view of {city} skyline, {sky}, "
        f"{drama}"
        f"authentic city architecture of {city}, "
        f"atmospheric air pollution visible, "
        f"environmental documentary photography style, "
        f"moody cinematic composition"
    )


def _pollinations_generate(prompt: str, path: str, width: int, height: int, seed: int) -> bool:
    encoded  = urllib.parse.quote(prompt)
    negative = urllib.parse.quote(AQI_NEGATIVE)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux"
        f"&seed={seed}&negative={negative}"
    )
    backoffs = [30, 60, 90]
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            if len(r.content) < 5000:
                raise ValueError(f"Too small ({len(r.content)} bytes)")
            with open(path, "wb") as f:
                f.write(r.content)
            return True
        except Exception as e:
            logger.warning(f"Pollinations attempt {attempt+1}/3: {e}")
            if attempt < 2:
                time.sleep(backoffs[attempt])
    return False


def _fallback_card(path: str, scene: dict, width: int, height: int):
    from PIL import Image, ImageDraw
    color = scene.get("color", "#333333")
    img   = Image.new("RGB", (width, height), color)
    draw  = ImageDraw.Draw(img)
    draw.text((width // 2, height // 2),
              f"{scene.get('city', 'City')}\nAQI {scene.get('aqi', '?')}",
              fill="white", anchor="mm")
    img.save(path)
    logger.warning(f"Used fallback card for scene {scene.get('scene_number')}")


def generate_scene_image(scene: dict, run_id: str,
                          width: int = W, height: int = H) -> str:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    scene_num = scene["scene_number"]
    path      = os.path.join(IMAGES_DIR, f"{run_id}_scene_{scene_num:02d}.png")
    prompt    = _build_aqi_prompt(scene)
    seed      = scene_num * 137
    logger.info(f"Generating image for {scene.get('city')} (AQI {scene.get('aqi')})")
    success = _pollinations_generate(prompt, path, width, height, seed)
    if not success:
        _fallback_card(path, scene, width, height)
    return path


def generate_all_images(story: dict, run_id: str,
                         width: int = W, height: int = H) -> list[str]:
    from rendering.aqi_card_renderer import render_aqi_card
    image_paths = []
    for scene in story.get("scenes", []):
        bg_path  = generate_scene_image(scene, run_id, width, height)
        card_out = bg_path.replace(".png", "_card.png")
        scene["date"] = story.get("date", "")
        render_aqi_card(bg_path, scene, card_out)
        image_paths.append(card_out)
        time.sleep(15)
    story["image_paths"] = image_paths
    logger.info(f"Generated {len(image_paths)} AQI scene images")
    return image_paths
