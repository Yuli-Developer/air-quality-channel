"""
Visual Director — AQI channel.
Style: combination of Style 1 (NASA satellite/aerial) + Style 4 (NatGeo documentary ground level).
Alternates per scene: odd scenes = satellite view, even scenes = ground documentary.
"""

import os
import time
import logging
import urllib.parse
import requests
from config.settings import IMAGES_DIR, SHORTS_WIDTH, SHORTS_HEIGHT

logger = logging.getLogger(__name__)

W, H = SHORTS_WIDTH, SHORTS_HEIGHT   # 1080 x 1920

AQI_NEGATIVE = (
    "cartoon, anime, painting, illustration, people faces, human face, portrait, "
    "text, watermark, logo, low quality, blurry, distorted, ugly, bad anatomy"
)

# Sky/smog description per AQI level
_SKY_STYLE = {
    "Good":               "crystal clear blue sky, pristine clean air, golden sunlight, beautiful visibility",
    "Moderate":           "slightly hazy pale sky, light smog layer, soft diffused golden light",
    "Unhealthy for Some": "orange-tinted hazy sky, visible smog layer, reduced visibility, dusty atmosphere",
    "Unhealthy":          "thick orange-red smog, heavy pollution haze, dramatic reduced visibility, toxic air",
    "Very Unhealthy":     "dense toxic smog, dark orange-purple apocalyptic haze, barely visible skyline",
    "Hazardous":          "extreme dark red-brown toxic smog blanket, apocalyptic visibility near zero, emergency atmosphere",
}

# Style 1: NASA satellite / high aerial — dramatic smog from above
SATELLITE_BASE = (
    "NASA satellite photography style, aerial view from very high altitude, "
    "looking down at city from above clouds, thick brown-orange smog blanket clearly visible, "
    "earth observation satellite image, atmospheric pollution haze, "
    "photorealistic aerial photography, dramatic top-down perspective, "
    "pollution cloud visible from space altitude, cinematic scale, "
    "NO people, NO faces, environment only, "
    "VERTICAL 9:16 portrait composition"
)

# Style 4: National Geographic documentary ground level — silhouettes in smog
DOCUMENTARY_BASE = (
    "National Geographic environmental documentary photography, "
    "ground level street view, dramatic smoggy morning atmosphere, "
    "silhouette of city skyline barely visible through thick haze, "
    "orange toxic sun diffused through pollution layer, "
    "moody atmospheric photojournalism, award-winning environmental photography, "
    "NO faces visible, silhouettes and shadows only, "
    "cinematic film grain, dramatic chiaroscuro lighting, "
    "VERTICAL 9:16 portrait composition"
)


def _build_aqi_prompt(scene: dict) -> str:
    city     = scene.get("city", "city")
    category = scene.get("category", "Moderate")
    sky      = _SKY_STYLE.get(category, "hazy sky")
    aqi      = scene.get("aqi", 100)
    scene_num = scene.get("scene_number", 1)

    # Alternate styles: odd = satellite, even = documentary
    if scene_num % 2 == 1:
        base = SATELLITE_BASE
        style_note = f"satellite view over {city}, {sky}, thick pollution haze visible from above"
    else:
        base = DOCUMENTARY_BASE
        style_note = f"street scene of {city}, {sky}, dramatic pollution atmosphere"

    # Extra drama for high AQI
    if aqi > 200:
        drama = "emergency crisis atmosphere, apocalyptic scale, disaster photography, "
    elif aqi > 150:
        drama = "ominous threatening atmosphere, environmental crisis, "
    elif aqi <= 50:
        drama = "beautiful pristine environment, clean air celebration, hopeful atmosphere, "
    else:
        drama = ""

    return (
        f"{base}, "
        f"{style_note}, "
        f"{drama}"
        f"authentic {city} urban environment, "
        f"environmental documentary realism"
    )


def _pollinations_generate(prompt: str, path: str, width: int, height: int, seed: int) -> bool:
    encoded  = urllib.parse.quote(prompt)
    negative = urllib.parse.quote(AQI_NEGATIVE)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux"
        f"&seed={seed}&negative={negative}"
    )
    backoffs = [60, 90, 120]
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
    logger.warning(f"Used fallback for scene {scene.get('scene_number')}")


def generate_scene_image(scene: dict, run_id: str,
                          width: int = W, height: int = H) -> str:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    scene_num = scene["scene_number"]
    path      = os.path.join(IMAGES_DIR, f"{run_id}_scene_{scene_num:02d}.png")
    prompt    = _build_aqi_prompt(scene)
    seed      = scene_num * 137

    style_name = "satellite" if scene_num % 2 == 1 else "documentary"
    logger.info(f"Scene {scene_num} [{style_name}]: {scene.get('city')} AQI {scene.get('aqi')}")

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
        time.sleep(35)
    story["image_paths"] = image_paths
    logger.info(f"Generated {len(image_paths)} AQI scene images")
    return image_paths
