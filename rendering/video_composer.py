"""
Video Composer — Air Quality Channel.
Clean slow Ken Burns (gentle zoom/pan) — no shaking, no speed lines, no finance branding.
"""

import os
import logging
import numpy as np
from PIL import Image
from moviepy import (
    AudioFileClip, CompositeAudioClip, VideoClip,
    concatenate_videoclips, ImageClip,
)
from config.settings import (
    SHORTS_DIR, FPS,
    SHORTS_WIDTH as SW, SHORTS_HEIGHT as SH,
    VIDEO_BITRATE, AUDIO_BITRATE,
)

logger = logging.getLogger(__name__)


# ── Smooth Ken Burns effect ─────────────────────────────────────────────────

def _ken_burns(image_path: str, duration: float, effect: str = "zoom_in") -> VideoClip:
    """
    Slow, smooth Ken Burns effect.
    No shaking. Gentle zoom in/out or subtle pan.
    """
    img      = Image.open(image_path).convert("RGB").resize((SW, SH), Image.LANCZOS)
    arr      = np.array(img, dtype=np.uint8)

    # Slightly oversized canvas to allow zoom/pan without black borders
    pad      = 60   # pixels of headroom
    img_big  = Image.open(image_path).convert("RGB").resize(
        (SW + pad * 2, SH + pad * 2), Image.LANCZOS
    )
    arr_big  = np.array(img_big, dtype=np.uint8)

    def frame(t):
        progress = t / max(duration, 0.001)   # 0.0 → 1.0

        if effect == "zoom_in":
            # Start slightly zoomed out, slowly zoom in
            scale = 1.0 + 0.04 * progress
            crop_w = int(SW / scale)
            crop_h = int(SH / scale)
            x0 = (SW + pad * 2 - crop_w) // 2
            y0 = (SH + pad * 2 - crop_h) // 2
            region = arr_big[y0:y0 + crop_h, x0:x0 + crop_w]

        elif effect == "zoom_out":
            # Start slightly zoomed in, slowly pull back
            scale = 1.04 - 0.04 * progress
            crop_w = int(SW / scale)
            crop_h = int(SH / scale)
            x0 = (SW + pad * 2 - crop_w) // 2
            y0 = (SH + pad * 2 - crop_h) // 2
            region = arr_big[y0:y0 + crop_h, x0:x0 + crop_w]

        elif effect == "pan_right":
            # Slow drift left → right
            offset = int(pad * progress)
            region = arr_big[pad:pad + SH, offset:offset + SW]

        elif effect == "pan_left":
            # Slow drift right → left
            offset = int(pad * (1 - progress))
            region = arr_big[pad:pad + SH, offset:offset + SW]

        else:
            return arr

        # Resize crop back to exact output size
        out = Image.fromarray(region).resize((SW, SH), Image.BILINEAR)
        return np.array(out)

    return VideoClip(frame, duration=duration).with_fps(FPS)


# ── Caption overlay ─────────────────────────────────────────────────────────

def _add_captions(clip: VideoClip, caption_chunks: list,
                  scene_start: float, scene_dur: float) -> VideoClip:
    """Overlay word-level captions relevant to this scene's time window."""
    from rendering.caption_engine import draw_captions
    relevant = [
        c for c in caption_chunks
        if c["chunk_end"] >= scene_start and c["chunk_start"] <= scene_start + scene_dur
    ]
    if not relevant:
        return clip

    def make_frame(t):
        base = clip.get_frame(t)
        abs_t = scene_start + t
        return draw_captions(base, abs_t, relevant)

    return VideoClip(make_frame, duration=scene_dur).with_fps(FPS)


# ── Shorts composer ─────────────────────────────────────────────────────────

def compose_shorts(story: dict, shorts_audio_path: str,
                   music_path: str | None, run_id: str) -> str:
    os.makedirs(SHORTS_DIR, exist_ok=True)
    output = os.path.join(SHORTS_DIR, f"{run_id}_shorts.mp4")

    narration   = AudioFileClip(shorts_audio_path)
    total_dur   = narration.duration
    scenes      = story.get("scenes", [])
    image_paths = story.get("image_paths", [])
    captions    = story.get("shorts_caption_chunks", story.get("caption_chunks", []))

    n_scenes  = max(len(scenes), 1)
    scene_dur = total_dur / n_scenes
    logger.info(f"Composing Shorts: {n_scenes} scenes × {scene_dur:.1f}s = {total_dur:.1f}s")

    # Cycle through 4 gentle effects
    EFFECTS = ["zoom_in", "zoom_out", "pan_right", "pan_left"]

    clips = []
    for i, scene in enumerate(scenes):
        idx    = scene.get("scene_number", i + 1) - 1
        effect = EFFECTS[i % len(EFFECTS)]

        if idx < len(image_paths) and os.path.exists(image_paths[idx]):
            clip = _ken_burns(image_paths[idx], scene_dur, effect)
            logger.info(f"  Scene {i+1}: {scene.get('city')} [{effect}]")
        else:
            # Plain coloured fallback
            color = _hex_rgb(scene.get("color", "#222222"))
            clip  = ImageClip(
                np.full((SH, SW, 3), color, dtype=np.uint8),
                duration=scene_dur
            ).with_fps(FPS)
            logger.warning(f"  Scene {i+1}: fallback color card")

        # Add captions
        scene_start = i * scene_dur
        clip = _add_captions(clip, captions, scene_start, scene_dur)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    # Audio: narration + soft background music
    if music_path and os.path.exists(music_path):
        music = AudioFileClip(music_path).subclipped(0, total_dur)
        music = music.with_volume_scaled(0.08)
        audio = CompositeAudioClip([narration, music])
    else:
        audio = narration

    video = video.with_audio(audio)

    logger.info(f"Rendering Shorts → {output}")
    video.write_videofile(
        output,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate=VIDEO_BITRATE,
        audio_bitrate=AUDIO_BITRATE,
        logger=None,
        preset="fast",
    )
    video.close()
    narration.close()

    story["shorts_path"] = output
    logger.info(f"Shorts done: {output}")
    return output


def _hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ── Stub for main video (not used in AQI channel) ──────────────────────────

def compose_main_video(story, *args, **kwargs):
    logger.info("Main video not used in AQI channel (Shorts only)")
    return None
