"""
AQI Card Renderer — generates a PIL-based data card overlay for each city scene.
"""

import os
import math
import logging
from PIL import Image, ImageDraw, ImageFont
from config.settings import IMAGES_DIR, SHORTS_WIDTH, SHORTS_HEIGHT

logger = logging.getLogger(__name__)

W, H = SHORTS_WIDTH, SHORTS_HEIGHT   # 1080 x 1920


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


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _draw_gauge_arc(draw, cx, cy, r, aqi, color):
    bb = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(bb, start=180, end=360, fill="#333333", width=28)
    fraction  = min(aqi / 500, 1.0)
    end_angle = 180 + fraction * 180
    rgb = _hex_to_rgb(color)
    draw.arc(bb, start=180, end=end_angle, fill=rgb, width=28)
    angle_rad = math.radians(180 + fraction * 180)
    nx = int(cx + (r - 14) * math.cos(angle_rad))
    ny = int(cy + (r - 14) * math.sin(angle_rad))
    draw.ellipse([nx-10, ny-10, nx+10, ny+10], fill="white")


def _fit_city_name(draw, city: str, max_w: int):
    """Return (lines, font) that fit within max_w."""
    city_upper = city.upper()
    for font_size in [100, 82, 66, 52, 42]:
        font = _font(font_size)
        # Try single line
        if draw.textlength(city_upper, font=font) <= max_w:
            return [city_upper], font, font_size
        # Try splitting at space
        if " " in city_upper:
            parts = city_upper.rsplit(" ", 1)
            if all(draw.textlength(p, font=font) <= max_w for p in parts):
                return parts, font, font_size
    # Last resort: smallest font, single line
    font = _font(42)
    return [city_upper], font, 42


def render_aqi_card(bg_path: str, scene: dict, out_path: str) -> str:
    city      = scene["city"]
    aqi       = scene["aqi"]
    category  = scene["category"]
    color     = scene["color"]
    advice    = scene.get("advice", "")
    rgb_color = _hex_to_rgb(color)

    # Background
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    else:
        img = Image.new("RGBA", (W, H), (10, 10, 30, 255))

    # Dark bottom gradient
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for row in range(H // 2, H):
        alpha = int(200 * (row - H // 2) / (H // 2))
        od.rectangle([0, row, W, row + 1], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # ── Channel badge ──────────────────────────────────────────────────────
    badge_font = _font(30)
    draw.rectangle([30, 50, 390, 96], fill=(*rgb_color, 220))
    draw.text((210, 73), "AQI DAILY", font=badge_font,
              fill="white", anchor="mm")

    # ── City name — auto-shrink & wrap ────────────────────────────────────
    lines, city_font, font_size = _fit_city_name(draw, city, W - 80)
    city_y = H // 2 - 260
    for line in lines:
        draw.text((W // 2, city_y), line, font=city_font, fill="white",
                  anchor="mm", stroke_width=5, stroke_fill="black")
        city_y += font_size + 10

    # ── Gauge arc ─────────────────────────────────────────────────────────
    cx, cy, r = W // 2, H // 2 + 30, 175
    _draw_gauge_arc(draw, cx, cy, r, aqi, color)

    # ── AQI number ────────────────────────────────────────────────────────
    num_font = _font(120)
    draw.text((cx, cy - 25), str(aqi),
              font=num_font, fill=color, anchor="mm",
              stroke_width=8, stroke_fill="black")
    label_font = _font(40)
    draw.text((cx, cy + 55), "AQI INDEX",
              font=label_font, fill="#AAAAAA", anchor="mm")

    # ── Category pill ─────────────────────────────────────────────────────
    cat_font = _font(46)
    cat_text = category.upper()
    cat_w    = draw.textlength(cat_text, font=cat_font) + 60
    cat_x    = (W - cat_w) // 2
    cat_y    = H // 2 + 230
    draw.rounded_rectangle([cat_x, cat_y, cat_x + cat_w, cat_y + 65],
                            radius=32, fill=(*rgb_color, 240))
    draw.text((W // 2, cat_y + 32), cat_text,
              font=cat_font, fill="white", anchor="mm")

    # ── Advice line ───────────────────────────────────────────────────────
    adv_font  = _font(34)
    max_chars = 54
    words, line_buf, advice_lines = advice.split(), [], []
    for w in words:
        if len(" ".join(line_buf + [w])) <= max_chars:
            line_buf.append(w)
        else:
            advice_lines.append(" ".join(line_buf))
            line_buf = [w]
    if line_buf:
        advice_lines.append(" ".join(line_buf))

    adv_y = H // 2 + 325
    for al in advice_lines[:2]:
        draw.text((W // 2, adv_y), al, font=adv_font,
                  fill="#DDDDDD", anchor="mm", stroke_width=3, stroke_fill="black")
        adv_y += 44

    # ── Subscribe bar ─────────────────────────────────────────────────────
    draw.rectangle([0, H - 75, W, H], fill=(*rgb_color, 230))
    sub_font = _font(28)
    draw.text((W // 2, H - 37),
              "AQI DAILY  •  FOLLOW FOR DAILY UPDATES",
              font=sub_font, fill="white", anchor="mm")

    # ── Date watermark ────────────────────────────────────────────────────
    date_str = scene.get("date", "")
    if date_str:
        dt_font = _font(26)
        draw.text((W - 28, H - 85), date_str,
                  font=dt_font, fill="#888888", anchor="rm")

    img.convert("RGB").save(out_path, "PNG")
    logger.info(f"AQI card saved: {out_path}")
    return out_path
