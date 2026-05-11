"""
Caption Engine — animated word-by-word TikTok-style captions.
Supports main video (landscape) and Shorts (vertical).
"""

import re
import os
import asyncio
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip
from config.settings import AUDIO_DIR, SHORTS_WIDTH as W, SHORTS_HEIGHT as H

logger = logging.getLogger(__name__)

VOICE = "en-GB-RyanNeural"
CAPTION_Y_RATIO = 0.80      # vertical position of captions
FONT_SIZE       = 80
GAP             = 24


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── TTS ────────────────────────────────────────────────────────────────────

async def _tts_async(text: str, audio_path: str):
    import edge_tts
    comm = edge_tts.Communicate(text, voice=VOICE)
    with open(audio_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])


def generate_voiceover(narration: str, run_id: str, suffix: str = "") -> str:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    path = os.path.join(AUDIO_DIR, f"{run_id}_narration{suffix}.mp3")
    logger.info(f"Generating voiceover{suffix}...")
    asyncio.run(_tts_async(narration, path))
    return path


# ── Word Timings ───────────────────────────────────────────────────────────

def _word_weight(w: str) -> float:
    base = max(len(w.rstrip(".,!?;:")), 1)
    if w.rstrip().endswith((".", "!", "?")):
        base += 3
    elif w.rstrip().endswith((",", ";")):
        base += 1.5
    return float(base)


def estimate_timings(text: str, total_duration: float) -> list[dict]:
    words   = [w for w in re.split(r"\s+", text.strip()) if w]
    weights = [_word_weight(w) for w in words]
    total_w = sum(weights)
    timings = []
    t = 0.2
    for word, weight in zip(words, weights):
        dur = (weight / total_w) * (total_duration - 0.4)
        timings.append({
            "word":  word.rstrip(".,!?;:"),
            "start": round(t, 3),
            "end":   round(t + dur, 3),
        })
        t += dur
    return timings


def build_caption_chunks(timings: list[dict], words_per_chunk: int = 4) -> list[dict]:
    chunks = []
    i = 0
    while i < len(timings):
        chunk = timings[i: i + words_per_chunk]
        chunks.append({
            "words":       [w["word"] for w in chunk],
            "chunk_start": chunk[0]["start"],
            "chunk_end":   chunk[-1]["end"],
            "word_timings": chunk,
        })
        i += words_per_chunk
    return chunks


# ── Caption Rendering ──────────────────────────────────────────────────────

def draw_captions(frame: np.ndarray, t: float,
                   chunks: list[dict],
                   canvas_w: int = W, canvas_h: int = H,
                   font_size: int = FONT_SIZE) -> np.ndarray:
    img = Image.fromarray(frame)
    active_chunk, active_word_idx = None, 0

    for chunk in chunks:
        if chunk["chunk_start"] <= t <= chunk["chunk_end"] + 0.25:
            active_chunk = chunk
            for wi, wt in enumerate(chunk["word_timings"]):
                if wt["start"] <= t <= wt["end"] + 0.12:
                    active_word_idx = wi
                    break
            else:
                active_word_idx = len(chunk["words"]) - 1
            break

    if not active_chunk:
        return np.array(img)

    # Dark gradient overlay
    overlay = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    od      = ImageDraw.Draw(overlay)
    grad_y  = int(canvas_h * 0.60)
    for row in range(grad_y, canvas_h):
        alpha = int(200 * (row - grad_y) / (canvas_h - grad_y))
        od.rectangle([0, row, canvas_w, row + 1], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    words = active_chunk["words"]
    cf    = _font(font_size)
    sizes = [draw.textbbox((0, 0), w, font=cf) for w in words]
    widths = [b[2] - b[0] for b in sizes]
    total_w = sum(widths) + GAP * (len(words) - 1)
    x = (canvas_w - total_w) // 2
    y = int(canvas_h * CAPTION_Y_RATIO)

    stroke = 5
    for wi, (word, ww) in enumerate(zip(words, widths)):
        color = "#FFE600" if wi == active_word_idx else "#FFFFFF"
        for dx in (-stroke, 0, stroke):
            for dy in (-stroke, 0, stroke):
                if dx or dy:
                    draw.text((x + dx, y + dy), word, font=cf, fill="#000000")
        draw.text((x, y), word, font=cf, fill=color)
        x += ww + GAP

    return np.array(img)


# ── Full voiceover pipeline ────────────────────────────────────────────────

def prepare_voiceover(narration: str, run_id: str, suffix: str = "") -> tuple[str, list[dict], list[dict]]:
    """
    Generate audio + estimate timings + build chunks.
    Returns (audio_path, word_timings, caption_chunks)
    """
    audio_path = generate_voiceover(narration, run_id, suffix)
    clip       = AudioFileClip(audio_path)
    duration   = clip.duration
    clip.close()
    logger.info(f"Audio duration: {duration:.1f}s")

    timings = estimate_timings(narration, duration)
    chunks  = build_caption_chunks(timings, words_per_chunk=4)
    return audio_path, timings, chunks
