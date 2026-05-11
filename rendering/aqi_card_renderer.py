"""
AQI Card Renderer — generates a PIL-based data card overlay for each city scene.
Renders: city name, AQI number, colour-coded gauge arc, category label, advice.
Output is a 1080x1920 PNG composited on top of the background city image.
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


def _draw_gauge_arc(draw: ImageDraw.Draw, cx: int, cy: int, r: int,
                    aqi: int, color: str):
    """Draw a semicircular gauge arc (180° sweep) representing AQI 0-500."""
    # Background arc (grey)
    bb = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(bb, start=180, end=360, fill="#333333", width=28)

    # Filled arc proportional to AQI (capped at 500)
    fraction  = min(aqi / 500, 1.0)
    end_angle = 180 + fraction * 180
    rgb       = _hex_to_rgb(color)
    draw.arc(bb, start=180, end=end_angle, fill=rgb, width=28)

    # Needle
    angle_rad  = math.radians(180 + fraction * 180)
    nx = int(cx + (r - 14) * math.cos(angle_rad))
    ny = int(cy + (r - 14) * math.sin(angle_rad))
    draw.ellipse([nx-10, ny-10, nx+10, ny+10], fill="white")


def render_aqi_card(bg_path: str, scene: dict, out_path: str) -> str:
    """
    Composite an AQI data card onto a background image.
    bg_path  — city skyline image (1080x1920)
    scene    — dict with city, aqi, category, color, advice
    out_path — destination path for final PNG
    """
    city     = scene["city"]
    aqi      = scene["aqi"]
    category = scene["category"]
    color    = scene["color"]
    advice   = scene.get("advice", "")
    rgb_color = _hex_to_rgb(color)

    # Load or create background
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    else:
        img = Image.new("RGBA", (W, H), (10, 10, 30, 255))

    # Dark overlay bottom half for readability
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for row in range(H // 2, H):
        alpha = int(200 * (row - H // 2) / (H // 2))
        od.rectangle([0, row, W, row + 1], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # ── Channel badge ──────────────────────────────────────────────────────
    badge_font = _font(32)
    draw.rectangle([30, 50, 400, 100], fill=(*rgb_color, 220))
    draw.text((215, 75), "DAILY AQI REPORT", font=badge_font,
              fill="white", anchor="mm")

    # ── City name ─────────────────────────────────────────────────────────
    city_font = _font(110)
    draw.text((W // 2, H // 2 - 220), city.upper(),
              font=city_font, fill="white", anchor="mm",
              stroke_width=6, stroke_fill="black")

    # ── Gauge arc ─────────────────────────────────────────────────────────
    cx, cy, r = W // 2, H // 2 + 20, 180
    _draw_gauge_arc(draw, cx, cy, r, aqi, color)

    # ── AQI number in centre of gauge ─────────────────────────────────────
    num_font = _font(130)
    draw.text((cx, cy - 30), str(aqi),
              font=num_font, fill=color, anchor="mm",
              stroke_width=8, stroke_fill="black")

    label_font = _font(42)
    draw.text((cx, cy + 60), "US AQI",
              font=label_font, fill="#AAAAAA", anchor="mm")

    # ── Category pill ─────────────────────────────────────────────────────
    cat_font = _font(52)
    cat_w    = draw.textlength(category.upper(), font=cat_font) + 60
    cat_x    = (W - cat_w) // 2
    cat_y    = H // 2 + 240
    draw.rounded_rectangle([cat_x, cat_y, cat_x + cat_w, cat_y + 70],
                            radius=35, fill=(*rgb_color, 240))
    draw.text((W // 2, cat_y + 35), category.upper(),
              font=cat_font, fill="white", anchor="mm")

    # ── Advice line ───────────────────────────────────────────────────────
    adv_font  = _font(36)
    max_chars = 52
    if len(advice) > max_chars:
        # simple word-wrap at 2 lines
        words, line, lines_out = advice.split(), [], []
        for w in words:
            if len(" ".join(line + [w])) <= max_chars:
                line.append(w)
            else:
                lines_out.append(" ".join(line))
                line = [w]
        if line:
            lines_out.append(" ".join(line))
        advice_lines = lines_out[:2]
    else:
        advice_lines = [advice]

    adv_y = H // 2 + 340
    for al in advice_lines:
        draw.text((W // 2, adv_y), al, font=adv_font,
                  fill="#DDDDDD", anchor="mm", stroke_width=3, stroke_fill="black")
        adv_y += 46

    # ── Subscribe bar ─────────────────────────────────────────────────────
    bar_color = (*rgb_color, 230)
    draw.rectangle([0, H - 80, W, H], fill=bar_color)
    sub_font = _font(30)
    draw.text((W // 2, H - 40),
              "FOLLOW  •  DAILY AIR QUALITY  •  STAY SAFE",
              font=sub_font, fill="white", anchor="mm")

    # ── Date watermark ────────────────────────────────────────────────────
    date_str = scene.get("date", "")
    if date_str:
        dt_font = _font(28)
        draw.text((W - 30, H - 90), date_str,
                  font=dt_font, fill="#888888", anchor="rm")

    img = img.convert("RGB")
    img.save(out_path, "PNG")
    logger.info(f"AQI card saved: {out_path}")
    return out_path
