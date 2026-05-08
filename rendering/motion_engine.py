"""
Motion Engine — cinematic effects applied to still images.
Supports: Ken Burns, parallax, camera shake, manga speed lines,
rain/fire overlays, particles, zoom burst.
"""

import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy import VideoClip
from config.settings import VIDEO_WIDTH as W, VIDEO_HEIGHT as H, FPS


# ── Ken Burns ──────────────────────────────────────────────────────────────

def ken_burns_clip(image_path: str, duration: float,
                   effect: str = None) -> VideoClip:
    """Zoom/pan a still image for cinematic motion."""
    img = Image.open(image_path).convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.array(img)
    effect = effect or random.choice(["zoom_in", "zoom_out", "pan_right", "pan_left"])

    def make_frame(t):
        progress = t / max(duration, 0.001)
        scale = {
            "zoom_in":   1.0 + 0.12 * progress,
            "zoom_out":  1.12 - 0.12 * progress,
            "pan_right": 1.08,
            "pan_left":  1.08,
        }[effect]

        cw, ch = int(W / scale), int(H / scale)

        if effect == "pan_right":
            ox = int((W - cw) * progress)
            oy = (H - ch) // 2
        elif effect == "pan_left":
            ox = int((W - cw) * (1 - progress))
            oy = (H - ch) // 2
        else:
            ox = (W - cw) // 2
            oy = (H - ch) // 2

        ox = max(0, min(ox, W - cw))
        oy = max(0, min(oy, H - ch))
        cropped = arr[oy:oy + ch, ox:ox + cw]
        return np.array(Image.fromarray(cropped).resize((W, H), Image.LANCZOS))

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ── Parallax ───────────────────────────────────────────────────────────────

def parallax_clip(image_path: str, duration: float,
                  layers: int = 3) -> VideoClip:
    """
    Simulates parallax by splitting image into horizontal bands
    that move at different speeds — creates depth illusion.
    """
    img   = Image.open(image_path).convert("RGB").resize((W, H), Image.LANCZOS)
    arr   = np.array(img)
    bands = np.array_split(arr, layers, axis=0)
    speeds = [0.04 * (i + 1) for i in range(layers)]   # pixels per second

    def make_frame(t):
        canvas = arr.copy()
        y = 0
        for band, speed in zip(bands, speeds):
            bh = band.shape[0]
            shift = int(t * speed * FPS) % W
            shifted = np.roll(band, shift, axis=1)
            canvas[y:y + bh] = shifted
            y += bh
        return canvas

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ── Camera Shake ───────────────────────────────────────────────────────────

def add_camera_shake(clip: VideoClip, intensity: int = 4) -> VideoClip:
    """Add subtle random camera shake to a clip."""
    duration = clip.duration

    def make_frame(t):
        frame = clip.get_frame(t)
        img   = Image.fromarray(frame)
        dx    = random.randint(-intensity, intensity)
        dy    = random.randint(-intensity, intensity)
        img   = img.transform(
            (W, H), Image.AFFINE,
            (1, 0, dx, 0, 1, dy),
            fillcolor=(0, 0, 0),
        )
        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ── Speed Lines Overlay ────────────────────────────────────────────────────

def speed_lines_frame(frame: np.ndarray, cx: int = None,
                       cy: int = None, intensity: float = 1.0) -> np.ndarray:
    """Draw radial speed lines on a single frame (manga action effect)."""
    cx = cx or W // 2
    cy = cy or H // 3
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    n_lines = int(60 * intensity)
    for i in range(n_lines):
        angle  = (2 * math.pi * i) / n_lines + random.uniform(-0.03, 0.03)
        length = random.randint(300, 900)
        gap    = random.randint(10, 30)
        x0 = cx + gap * math.cos(angle)
        y0 = cy + gap * math.sin(angle)
        x1 = cx + length * math.cos(angle)
        y1 = cy + length * math.sin(angle)
        alpha = random.randint(40, 100)
        width = random.choice([1, 1, 2])
        draw.line([(x0, y0), (x1, y1)], fill=(255, 255, 255, alpha), width=width)

    base = Image.fromarray(frame).convert("RGBA")
    comp = Image.alpha_composite(base, overlay)
    return np.array(comp.convert("RGB"))


# ── Rain Overlay ───────────────────────────────────────────────────────────

def rain_frame(frame: np.ndarray, t: float, density: int = 200) -> np.ndarray:
    """Add animated rain streaks to a frame."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    rng     = random.Random(int(t * 30))

    for _ in range(density):
        x   = rng.randint(0, W)
        y   = (rng.randint(0, H) + int(t * 800)) % H
        length = rng.randint(15, 40)
        alpha  = rng.randint(60, 130)
        draw.line([(x, y), (x - 3, y + length)],
                  fill=(180, 200, 255, alpha), width=1)

    base = Image.fromarray(frame).convert("RGBA")
    return np.array(Image.alpha_composite(base, overlay).convert("RGB"))


# ── Particle Overlay ───────────────────────────────────────────────────────

def particles_frame(frame: np.ndarray, t: float,
                     count: int = 40, color=(255, 220, 50)) -> np.ndarray:
    """Floating particle effect (embers / dust)."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    rng     = random.Random(42)

    for _ in range(count):
        x    = rng.randint(0, W)
        base_y = rng.randint(0, H)
        y    = (base_y - int(t * rng.randint(30, 100))) % H
        r    = rng.randint(2, 5)
        alpha = rng.randint(100, 200)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=(*color, alpha))

    base = Image.fromarray(frame).convert("RGBA")
    return np.array(Image.alpha_composite(base, overlay).convert("RGB"))


# ── Manga Transition Flash ─────────────────────────────────────────────────

def flash_transition(duration: float = 0.15) -> VideoClip:
    """White flash frame for manga-style scene cuts."""
    white = np.full((H, W, 3), 255, dtype=np.uint8)
    return VideoClip(lambda t: white, duration=duration).with_fps(FPS)


# ── Zoom Burst ─────────────────────────────────────────────────────────────

def zoom_burst_clip(image_path: str, duration: float) -> VideoClip:
    """Fast zoom into image center — high energy manga impact."""
    img = Image.open(image_path).convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.array(img)

    def make_frame(t):
        progress = (t / duration) ** 1.5    # accelerating zoom
        scale    = 1.0 + 0.5 * progress
        cw, ch   = int(W / scale), int(H / scale)
        ox, oy   = (W - cw) // 2, (H - ch) // 2
        ox = max(0, min(ox, W - cw))
        oy = max(0, min(oy, H - ch))
        cropped  = arr[oy:oy + ch, ox:ox + cw]
        return np.array(Image.fromarray(cropped).resize((W, H), Image.LANCZOS))

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ── Apply motion by name ────────────────────────────────────────────────────

def apply_motion(image_path: str, duration: float, effect: str) -> VideoClip:
    """Route to the correct motion effect by name."""
    if effect == "zoom_burst":
        return zoom_burst_clip(image_path, duration)
    elif effect == "parallax":
        return parallax_clip(image_path, duration)
    elif effect in ("ken_burns_zoom_in", "ken_burns_zoom_out", "pan_left", "pan_right"):
        eff = effect.replace("ken_burns_", "")
        return ken_burns_clip(image_path, duration, effect=eff)
    else:
        return ken_burns_clip(image_path, duration)
