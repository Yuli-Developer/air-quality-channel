"""
Thumbnail Engine — Air Quality Channel.
Design: full-bleed city background, large AQI number centered,
colour-coded by pollution level, clean sans-serif layout.
No shaking, no speed lines, no other channel branding.
"""

import os
import math
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from config.settings import THUMB_DIR
from storage.database import save_thumbnail_scores

logger = logging.getLogger(__name__)

W, H = 1280, 720   # YouTube thumbnail dimensions


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _aqi_palette(aqi: int) -> dict:
    """Return colour palette based on AQI level."""
    if aqi <= 50:
        return {"bg": "#001a00", "accent": "#00C853", "text": "#FFFFFF", "glow": "#00E676"}
    if aqi <= 100:
        return {"bg": "#1a1500", "accent": "#FFD600", "text": "#FFFFFF", "glow": "#FFEA00"}
    if aqi <= 150:
        return {"bg": "#1a0a00", "accent": "#FF6D00", "text": "#FFFFFF", "glow": "#FF9100"}
    if aqi <= 200:
        return {"bg": "#1a0000", "accent": "#D50000", "text": "#FFFFFF", "glow": "#FF1744"}
    if aqi <= 300:
        return {"bg": "#120018", "accent": "#AA00FF", "text": "#FFFFFF", "glow": "#D500F9"}
    return {"bg": "#1a0005", "accent": "#880E1F", "text": "#FFFFFF", "glow": "#FF1744"}


def _draw_gauge(draw, cx, cy, r, aqi, accent_color):
    """Semicircular AQI gauge arc."""
    bb = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(bb, start=180, end=360, fill="#333333", width=18)
    fraction  = min(aqi / 500, 1.0)
    end_angle = 180 + fraction * 180
    draw.arc(bb, start=180, end=end_angle, fill=accent_color, width=18)
    # Needle tip
    ang = math.radians(180 + fraction * 180)
    nx = int(cx + (r - 9) * math.cos(ang))
    ny = int(cy + (r - 9) * math.sin(ang))
    draw.ellipse([nx-8, ny-8, nx+8, ny+8], fill="white")


def _fit_text(draw, text: str, max_w: int, sizes=(110, 90, 72, 58, 46)):
    """Return (text, font) that fits within max_w."""
    for size in sizes:
        font = _font(size)
        if draw.textlength(text, font=font) <= max_w:
            return text, font, size
    return text, _font(sizes[-1]), sizes[-1]


def _render_thumbnail(image_paths: list, story: dict,
                      variant: int, run_id: str) -> str:
    os.makedirs(THUMB_DIR, exist_ok=True)
    path = os.path.join(THUMB_DIR, f"{run_id}_thumb_v{variant}.jpg")

    worst = story.get("worst_city", {})
    aqi   = worst.get("aqi", 100)
    city  = worst.get("city", "City")
    cat   = worst.get("category", "Moderate")
    pal   = _aqi_palette(aqi)

    # ── Background: best city image, darkened ─────────────────────────────
    preferred = [0, 2, 4, 1, 3]
    bg = None
    for idx in preferred:
        if idx < len(image_paths) and os.path.exists(image_paths[idx]):
            bg = Image.open(image_paths[idx]).convert("RGB")
            break
    if bg is None:
        bg = Image.new("RGB", (W, H), _hex_rgb(pal["bg"]))
    else:
        # Crop to 16:9
        iw, ih = bg.size
        target_ratio = W / H
        if iw / ih > target_ratio:
            new_w = int(ih * target_ratio)
            bg = bg.crop(((iw - new_w) // 2, 0, (iw - new_w) // 2 + new_w, ih))
        bg = bg.resize((W, H), Image.LANCZOS)
        # Darken + slight blur for readability
        bg = ImageEnhance.Brightness(bg).enhance(0.45)
        bg = ImageEnhance.Contrast(bg).enhance(1.3)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=1.5))

    # ── Coloured left stripe (1/3 width) overlay ──────────────────────────
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    accent_rgb = _hex_rgb(pal["accent"])
    # Left side gradient stripe
    for x in range(W // 3):
        alpha = int(200 * (1 - x / (W // 3)))
        sd.line([(x, 0), (x, H)], fill=(*accent_rgb, alpha), width=1)
    bg = Image.alpha_composite(bg.convert("RGBA"), stripe).convert("RGB")

    draw = ImageDraw.Draw(bg)

    # ── LEFT PANEL: AQI data ───────────────────────────────────────────────
    panel_cx = W // 6   # centre of left third

    # "AQI TODAY" label
    label_font = _font(28)
    draw.text((panel_cx, 60), "AQI TODAY", font=label_font,
              fill=pal["accent"], anchor="mm")

    # Gauge arc
    gauge_cx, gauge_cy, gauge_r = panel_cx, 230, 130
    _draw_gauge(draw, gauge_cx, gauge_cy, gauge_r, aqi, pal["accent"])

    # AQI number inside gauge
    num_font = _font(110)
    draw.text((gauge_cx, gauge_cy - 15), str(aqi),
              font=num_font, fill="white", anchor="mm",
              stroke_width=6, stroke_fill=pal["accent"])

    # Category pill
    cat_font = _font(30)
    cat_text = cat.upper()
    cat_w    = draw.textlength(cat_text, font=cat_font) + 40
    cat_x    = panel_cx - cat_w // 2
    cat_y    = gauge_cy + gauge_r - 10
    draw.rounded_rectangle([cat_x, cat_y, cat_x + cat_w, cat_y + 44],
                            radius=22, fill=pal["accent"])
    draw.text((panel_cx, cat_y + 22), cat_text,
              font=cat_font, fill="white", anchor="mm")

    # ── RIGHT PANEL: City name + subtitle ─────────────────────────────────
    right_x = W // 3 + 30   # start of right 2/3
    right_cx = (right_x + W) // 2

    # City name — auto-fit
    city_text, city_font, city_size = _fit_text(
        draw, city.upper(), W - right_x - 30,
        sizes=(130, 108, 88, 70, 56)
    )
    draw.text((right_cx, H // 2 - 60), city_text,
              font=city_font, fill="white", anchor="mm",
              stroke_width=8, stroke_fill="black")

    # "AIR QUALITY REPORT" subtitle
    sub_font = _font(34)
    draw.text((right_cx, H // 2 + city_size // 2 + 10),
              "AIR QUALITY REPORT",
              font=sub_font, fill=pal["accent"], anchor="mm")

    # Date
    date_str = story.get("date", "")
    if date_str:
        dt_font = _font(26)
        draw.text((W - 20, H - 20), date_str,
                  font=dt_font, fill="#AAAAAA", anchor="rm")

    # Bottom bar
    draw.rectangle([right_x, H - 50, W, H], fill=(*accent_rgb, 220))
    bar_font = _font(24)
    draw.text(((right_x + W) // 2, H - 25),
              "FOLLOW  •  AQI DAILY",
              font=bar_font, fill="white", anchor="mm")

    bg.save(path, "JPEG", quality=95)
    logger.info(f"Thumbnail v{variant}: {path}")
    return path


def generate_thumbnails(story: dict, run_id: str) -> tuple:
    image_paths = story.get("image_paths", [])
    thumbnails_meta = []

    for variant in range(1, 5):
        path = _render_thumbnail(image_paths, story, variant, run_id)
        thumbnails_meta.append({
            "variant":     variant,
            "path":        path,
            "title":       story.get("youtube_title", ""),
            "selected":    0,
            "total_score": 8.0,
        })

    # v1 is always best (uses worst city's scene — most dramatic)
    thumbnails_meta[0]["selected"] = 1
    story["thumbnail_path"] = thumbnails_meta[0]["path"]
    story["all_thumbnails"] = thumbnails_meta
    save_thumbnail_scores(run_id, thumbnails_meta)
    logger.info(f"Best thumbnail: v1")
    return thumbnails_meta[0]["path"], thumbnails_meta
