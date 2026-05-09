"""
Thumbnail Engine — generates 4 variants, scores each with Gemini,
auto-selects the highest CTR thumbnail.
"""

import os
import re
import math
import random
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config.settings import THUMB_DIR
from storage.database import save_thumbnail_scores

logger = logging.getLogger(__name__)

W, H = 1280, 720

THEMES = [
    {"bg": "#0A0A0A", "accent": "#E50000", "text": "#FFE600"},   # dark red yellow
    {"bg": "#0D0D2B", "accent": "#7B2FFF", "text": "#FFFFFF"},   # dark purple white
    {"bg": "#0A1A0A", "accent": "#00CC44", "text": "#FFE600"},   # dark green yellow
    {"bg": "#1A0A0A", "accent": "#FF6600", "text": "#FFFFFF"},   # dark orange white
]


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


def _wrap(text: str, font, max_w: int, draw) -> list[str]:
    words, lines, line = text.split(), [], []
    for word in words:
        test = " ".join(line + [word])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    return lines[:3]


def _outlined_text(draw, pos, text, font, fill, outline, stroke=10, anchor="lt"):
    x, y = pos
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx*dx + dy*dy <= stroke*stroke:
                draw.text((x+dx, y+dy), text, font=font, fill=outline, anchor=anchor)
    draw.text(pos, text, font=font, fill=fill, anchor=anchor)


def _speed_lines(draw, cx, cy, n=80):
    for i in range(n):
        angle  = (2 * math.pi * i) / n + random.uniform(-0.02, 0.02)
        length = random.randint(400, 1200)
        gap    = random.randint(8, 25)
        x0 = cx + gap * math.cos(angle)
        y0 = cy + gap * math.sin(angle)
        x1 = cx + length * math.cos(angle)
        y1 = cy + length * math.sin(angle)
        alpha = random.randint(30, 80)
        draw.line([(x0, y0), (x1, y1)],
                  fill=(255, 255, 255, alpha),
                  width=random.choice([1, 1, 2]))


def _halftone(img: Image.Image, spacing: int = 16, max_r: int = 4) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d   = ImageDraw.Draw(overlay)
    arr = np.array(img.convert("L"))
    for y in range(0, H, spacing):
        for x in range(0, W, spacing):
            b = arr[min(y, arr.shape[0]-1), min(x, arr.shape[1]-1)]
            r = int(max_r * (1 - b / 255) * 0.6)
            if r > 0:
                d.ellipse([x-r, y-r, x+r, y+r], fill=(0, 0, 0, 40))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _render_thumbnail(image_paths: list, title_text: str,
                       subtitle_text: str, theme: dict,
                       variant: int, run_id: str) -> str:
    os.makedirs(THUMB_DIR, exist_ok=True)
    path = os.path.join(THUMB_DIR, f"{run_id}_thumb_v{variant}.jpg")

    # Pick scene image
    preferred = [3, 1, 4, 0, 2, 5, 6]
    bg_img    = None
    for idx in preferred:
        if idx < len(image_paths) and os.path.exists(image_paths[idx]):
            bg_img = Image.open(image_paths[idx]).convert("RGB")
            break
    if bg_img is None:
        bg_img = Image.new("RGB", (W, H), theme["bg"])
    else:
        iw, ih = bg_img.size
        ratio  = W / H
        if iw / ih > ratio:
            new_w = int(ih * ratio)
            bg_img = bg_img.crop(((iw - new_w) // 2, 0,
                                  (iw - new_w) // 2 + new_w, ih))
        bg_img = bg_img.resize((W, H), Image.LANCZOS)
        bg_img = ImageEnhance.Contrast(bg_img).enhance(1.6)
        bg_img = ImageEnhance.Sharpness(bg_img).enhance(2.0)
        bg_img = _halftone(bg_img)

    # Dark bottom gradient
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    grad_y = int(H * 0.40)
    for row in range(grad_y, H):
        alpha = int(210 * (row - grad_y) / (H - grad_y))
        od.rectangle([0, row, W, row+1], fill=(0, 0, 0, alpha))
    bg_img = Image.alpha_composite(bg_img.convert("RGBA"), overlay).convert("RGB")

    # Speed lines
    sl_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _speed_lines(ImageDraw.Draw(sl_overlay), cx=W-180, cy=100)
    bg_img = Image.alpha_composite(bg_img.convert("RGBA"), sl_overlay).convert("RGB")
    draw   = ImageDraw.Draw(bg_img)

    # Left edge bar
    draw.rectangle([0, 0, 12, H], fill=theme["accent"])

    # Channel badge
    bf = _font(28)
    draw.rectangle([20, 20, 230, 60], fill=theme["accent"])
    draw.text((125, 40), "BREAKING WEIRD", font=bf, fill="white", anchor="mm")

    # !! badge
    ef = _font(52)
    cx, cy, r = W - 60, 60, 50
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=theme["accent"])
    draw.ellipse([cx-r+3, cy-r+3, cx+r-3, cy+r-3],
                 outline="#FFE600", width=3)
    draw.text((cx, cy), "!!", font=ef, fill="#FFE600", anchor="mm")

    # Title text with dark backing
    tf    = _font(100)
    pad   = 22
    lines = _wrap(title_text.upper(), tf, W - pad*2 - 60, draw)
    lh    = 112
    total = len(lines) * lh
    y     = H - total - 58

    backing = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(backing)
    bd.rectangle([0, y - 10, W, y + total + 10], fill=(0, 0, 0, 180))
    bg_img = Image.alpha_composite(bg_img.convert("RGBA"), backing).convert("RGB")
    draw   = ImageDraw.Draw(bg_img)

    for i, line in enumerate(lines):
        _outlined_text(draw, (pad, y), line, tf,
                        fill=theme["text"], outline="#000000",
                        stroke=11, anchor="lt")
        bbox = draw.textbbox((pad, y), line, font=tf, anchor="lt")
        draw.rectangle([pad, bbox[3]+2, bbox[2], bbox[3]+8],
                        fill=theme["accent"])
        y += lh

    # Subtitle
    if subtitle_text:
        sf = _font(40)
        draw.text((pad, H - 52), subtitle_text,
                  font=sf, fill="#CCCCCC", anchor="lt")

    # Subscribe bar
    draw.rectangle([0, H-50, W, H], fill=theme["accent"])
    sbar_f = _font(24)
    draw.text((W//2, H-25),
              "SUBSCRIBE  •  NEW EPISODE DAILY  •  BREAKING WEIRD",
              font=sbar_f, fill="white", anchor="mm")

    # Corner marks
    corner, lw = 26, 4
    for cx2, cy2, dx, dy in [(0,0,1,1),(W-corner,0,-1,1),
                              (0,H-corner,1,-1),(W-corner,H-corner,-1,-1)]:
        draw.line([(cx2, cy2), (cx2+dx*corner, cy2)], fill="#FFE600", width=lw)
        draw.line([(cx2, cy2), (cx2, cy2+dy*corner)], fill="#FFE600", width=lw)

    bg_img.save(path, "JPEG", quality=95)
    return path


_CTR_KEYWORDS = [
    "%", "million", "billion", "crashed", "surged", "record", "accidentally",
    "shocked", "insane", "wild", "bizarre", "broke", "fortune", "overnight",
    "all-time", "nobody", "secret", "revealed", "you won't", "how",
]

_EMOTION_KEYWORDS = {
    "shock":     ["shocked", "unbelievable", "impossible", "nobody expected", "crashed"],
    "curiosity": ["why", "how", "secret", "hidden", "nobody knew", "turns out"],
    "anger":     ["ceo", "bonus", "billionaire", "fraud", "scam", "while workers"],
    "laughter":  ["potato", "accidentally", "wrong", "glitch", "duck", "squirrel"],
}

# Theme performance weights — red/yellow (v1) historically highest CTR
_THEME_BOOST = [0.8, 0.4, 0.6, 0.5]


def _score_title(title: str) -> dict:
    """Rule-based thumbnail scoring — no API calls."""
    title_lower = title.lower()

    # CTR score: keyword hits + number presence + ideal length
    ctr_hits  = sum(1 for kw in _CTR_KEYWORDS if kw in title_lower)
    has_num   = bool(re.search(r'\d', title))
    length_ok = 4 <= len(title.split()) <= 8   # ideal title word count
    ctr_score = min(10.0, 6.0 + ctr_hits * 0.8 + (1.0 if has_num else 0) + (0.5 if length_ok else 0))

    # Emotion score: detect dominant emotion
    emotion_scores = {}
    for emotion, keywords in _EMOTION_KEYWORDS.items():
        emotion_scores[emotion] = sum(1 for kw in keywords if kw in title_lower)
    top_emotion   = max(emotion_scores, key=emotion_scores.get)
    emotion_score = min(10.0, 7.0 + emotion_scores[top_emotion] * 0.8)

    # Readability: shorter titles read better on mobile
    words        = len(title.split())
    readability  = 10.0 if words <= 5 else (8.5 if words <= 7 else 7.0)

    # Mobile score: uppercase words help visibility
    upper_ratio  = sum(1 for w in title.split() if w.isupper()) / max(len(title.split()), 1)
    mobile_score = min(10.0, 7.5 + upper_ratio * 2.0)

    total = (ctr_score * 0.40 + emotion_score * 0.30 +
             readability * 0.15 + mobile_score * 0.15)

    return {
        "ctr_score":    round(ctr_score, 1),
        "emotion_score": round(emotion_score, 1),
        "readability":  round(readability, 1),
        "mobile_score": round(mobile_score, 1),
        "total_score":  round(total, 1),
    }


def _score_thumbnails(thumbnails_meta: list[dict], story: dict) -> list[dict]:
    """Score thumbnails using rule-based logic. Zero API calls."""
    for i, t in enumerate(thumbnails_meta):
        scores = _score_title(t.get("title", story.get("youtube_title", "")))
        # Apply theme boost (v1 red/yellow performs best historically)
        boost  = _THEME_BOOST[i % len(_THEME_BOOST)]
        scores["total_score"] = round(min(10.0, scores["total_score"] + boost), 1)
        t.update(scores)
    return thumbnails_meta


def generate_thumbnails(story: dict, run_id: str) -> tuple[str, list[dict]]:
    """
    Generate 4 thumbnail variants, score them, return best path + all metadata.
    """
    image_paths    = story.get("image_paths", [])
    title_variants = story.get("title_variants",
                                [story.get("youtube_title", story["title"])] * 4)

    while len(title_variants) < 4:
        title_variants.append(title_variants[0])

    thumbnails_meta = []
    rendered_paths  = []

    for variant in range(4):
        theme    = THEMES[variant]
        title    = title_variants[variant]
        subtitle = story.get("hook", "")[:40] if variant % 2 == 1 else ""
        path     = _render_thumbnail(image_paths, title, subtitle,
                                      theme, variant + 1, run_id)
        rendered_paths.append(path)
        thumbnails_meta.append({
            "variant": variant + 1,
            "path":    path,
            "title":   title,
            "selected": 0,
        })
        logger.info(f"Thumbnail v{variant+1} rendered: {path}")

    # Rule-based scoring (no API calls)
    thumbnails_meta = _score_thumbnails(thumbnails_meta, story)

    # Select best
    best = max(thumbnails_meta, key=lambda x: x.get("total_score", 0))
    best["selected"] = 1
    logger.info(
        f"Best thumbnail: v{best['variant']} "
        f"(score={best.get('total_score', 0):.1f})"
    )

    save_thumbnail_scores(run_id, thumbnails_meta)
    story["thumbnail_path"] = best["path"]
    story["all_thumbnails"] = thumbnails_meta
    return best["path"], thumbnails_meta
