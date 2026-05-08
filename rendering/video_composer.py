"""
Video Composer — assembles the final video from all components.
Handles both landscape (main video) and vertical (Shorts).
"""

import os
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips,
)
from rendering.motion_engine import apply_motion, flash_transition, speed_lines_frame
from rendering.caption_engine import draw_captions
from config.settings import (
    VIDEO_DIR, SHORTS_DIR, FPS,
    VIDEO_WIDTH as W, VIDEO_HEIGHT as H,
    SHORTS_WIDTH as SW, SHORTS_HEIGHT as SH,
    VIDEO_BITRATE, AUDIO_BITRATE,
)

logger = logging.getLogger(__name__)

CHANNEL_NAME = "BREAKING WEIRD"


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


def _wrap(text: str, max_chars: int = 28) -> list[str]:
    words, lines, line = text.split(), [], []
    for w in words:
        if len(" ".join(line + [w])) <= max_chars:
            line.append(w)
        else:
            if line:
                lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))
    return lines


# ── Intro Card ─────────────────────────────────────────────────────────────

def make_intro_card(title: str, duration: float = 3.0,
                    canvas_w: int = W, canvas_h: int = H) -> VideoClip:
    img  = Image.new("RGB", (canvas_w, canvas_h), "#0A0A0A")
    draw = ImageDraw.Draw(img)

    # Top red bar
    draw.rectangle([0, 0, canvas_w, 10], fill="#E50000")

    # Channel badge
    lf = _font(34)
    badge_w = 280
    draw.rectangle([50, 30, 50 + badge_w, 78], fill="#E50000")
    draw.text((50 + badge_w // 2, 54), CHANNEL_NAME,
              font=lf, fill="white", anchor="mm")

    # Main title
    hf    = _font(88)
    lines = _wrap(title.upper(), max_chars=24)
    lh    = 104
    total = len(lines) * lh
    y     = (canvas_h - total) // 2 - 30
    for line in lines:
        for dx, dy in [(-3, 3), (3, 3)]:
            draw.text((canvas_w // 2 + dx, y + dy), line, font=hf,
                      fill="#000", anchor="mt")
        draw.text((canvas_w // 2, y), line, font=hf,
                  fill="#FFF", anchor="mt")
        y += lh

    # Bottom bar
    draw.rectangle([0, canvas_h - 60, canvas_w, canvas_h], fill="#E50000")
    sf = _font(26)
    draw.text((canvas_w // 2, canvas_h - 30),
              f"SUBSCRIBE  •  NEW EPISODE DAILY  •  {CHANNEL_NAME}",
              font=sf, fill="white", anchor="mm")
    draw.rectangle([0, canvas_h - 8, canvas_w, canvas_h], fill="#CC0000")

    arr = np.array(img)
    return VideoClip(lambda t: arr, duration=duration).with_fps(FPS)


# ── Scene Clip ─────────────────────────────────────────────────────────────

def _build_scene_clip(image_path: str, scene: dict,
                       scene_duration: float, chunks: list[dict],
                       scene_start: float,
                       canvas_w: int = W, canvas_h: int = H) -> VideoClip:
    """Build one scene: motion effect + captions."""
    effect   = scene.get("motion_effect", "ken_burns_zoom_in")
    bg_clip  = apply_motion(image_path, scene_duration, effect)

    # Adjust chunk timings relative to scene start
    adj_chunks = []
    for c in chunks:
        if c["chunk_end"] < scene_start or c["chunk_start"] > scene_start + scene_duration:
            continue
        adj_chunks.append({
            **c,
            "chunk_start": c["chunk_start"] - scene_start,
            "chunk_end":   c["chunk_end"]   - scene_start,
            "word_timings": [
                {**wt,
                 "start": wt["start"] - scene_start,
                 "end":   wt["end"]   - scene_start}
                for wt in c["word_timings"]
            ],
        })

    captioned = bg_clip.transform(
        lambda gf, t, ch=adj_chunks, cw=canvas_w, ch2=canvas_h:
            draw_captions(gf(t), t, ch, cw, ch2)
    )
    return captioned


# ── Main Video ─────────────────────────────────────────────────────────────

def compose_main_video(story: dict, audio_path: str,
                        music_path: str | None, run_id: str) -> str:
    os.makedirs(VIDEO_DIR, exist_ok=True)
    output = os.path.join(VIDEO_DIR, f"{run_id}_final.mp4")

    narration_audio = AudioFileClip(audio_path)
    total_dur       = narration_audio.duration
    caption_chunks  = story.get("caption_chunks", [])
    scenes          = story.get("scenes", [])
    image_paths     = story.get("image_paths", [])
    n_scenes        = max(len(scenes), 1)
    scene_dur       = total_dur / n_scenes

    logger.info(f"Composing: {n_scenes} scenes × {scene_dur:.1f}s = {total_dur:.1f}s")

    scene_clips = []
    for i, scene in enumerate(scenes):
        if i < len(image_paths) and os.path.exists(image_paths[i]):
            clip = _build_scene_clip(
                image_paths[i], scene, scene_dur,
                caption_chunks, i * scene_dur,
            )
        else:
            # Gradient fallback
            from phase2_video.stock_footage import make_gradient_frame
            arr = np.array([make_gradient_frame(t, scene.get("search_keywords", []), scene_dur)
                            for _ in [0]])[0]
            clip = VideoClip(lambda t: arr, duration=scene_dur).with_fps(FPS)
        scene_clips.append(clip)

    intro      = make_intro_card(story.get("youtube_title", story["title"]))
    main_video = concatenate_videoclips(scene_clips, method="compose")
    full_video = concatenate_videoclips([intro, main_video], method="compose")
    full_dur   = intro.duration + total_dur

    # Audio mix
    if music_path and os.path.exists(music_path):
        try:
            music = AudioFileClip(music_path)
            if music.duration < full_dur:
                reps  = int(full_dur / music.duration) + 2
                music = concatenate_audioclips([music] * reps).subclipped(0, full_dur)
            else:
                music = music.subclipped(0, full_dur)
            music       = music.with_volume_scaled(0.14)
            delayed     = narration_audio.with_start(intro.duration)
            final_audio = CompositeAudioClip([delayed, music])
        except Exception as e:
            logger.warning(f"Music mix failed: {e}")
            final_audio = narration_audio.with_start(intro.duration)
    else:
        final_audio = narration_audio.with_start(intro.duration)

    full_video = full_video.with_audio(final_audio)

    logger.info(f"Rendering → {output}")
    full_video.write_videofile(
        output, fps=FPS, codec="libx264",
        audio_codec="aac", bitrate=VIDEO_BITRATE,
        audio_bitrate=AUDIO_BITRATE,
        threads=4, preset="fast", logger=None,
    )
    narration_audio.close()
    full_video.close()
    story["video_path"] = output
    logger.info(f"Main video done: {output}")
    return output


# ── Shorts Video ───────────────────────────────────────────────────────────

def compose_shorts(story: dict, shorts_audio_path: str,
                    music_path: str | None, run_id: str) -> str:
    os.makedirs(SHORTS_DIR, exist_ok=True)
    output = os.path.join(SHORTS_DIR, f"{run_id}_shorts.mp4")

    narration_audio = AudioFileClip(shorts_audio_path)
    total_dur       = narration_audio.duration
    shorts_scenes   = story.get("shorts_scenes", story.get("scenes", [])[:4])
    image_paths     = story.get("image_paths", [])
    caption_chunks  = story.get("shorts_caption_chunks", story.get("caption_chunks", []))
    n_scenes        = max(len(shorts_scenes), 1)
    scene_dur       = total_dur / n_scenes

    logger.info(f"Composing Shorts: {n_scenes} scenes × {scene_dur:.1f}s")

    def _make_vertical(image_path: str, duration: float) -> VideoClip:
        """Crop landscape image to vertical 9:16 center crop."""
        img = Image.open(image_path).convert("RGB")
        iw, ih = img.size
        target_w = int(ih * SW / SH)
        if target_w > iw:
            target_w = iw
        x_off = (iw - target_w) // 2
        img   = img.crop((x_off, 0, x_off + target_w, ih))
        img   = img.resize((SW, SH), Image.LANCZOS)
        arr   = np.array(img)
        return VideoClip(lambda t: arr, duration=duration).with_fps(FPS)

    clips = []
    for i, scene in enumerate(shorts_scenes):
        idx = scene.get("scene_number", i + 1) - 1
        if idx < len(image_paths) and os.path.exists(image_paths[idx]):
            clip = _make_vertical(image_paths[idx], scene_dur)
        else:
            blank = np.zeros((SH, SW, 3), dtype=np.uint8)
            clip  = VideoClip(lambda t: blank, duration=scene_dur).with_fps(FPS)

        adj_chunks = []
        scene_start = i * scene_dur
        for c in caption_chunks:
            if c["chunk_end"] < scene_start or c["chunk_start"] > scene_start + scene_dur:
                continue
            adj_chunks.append({
                **c,
                "chunk_start": c["chunk_start"] - scene_start,
                "chunk_end":   c["chunk_end"] - scene_start,
                "word_timings": [
                    {**wt, "start": wt["start"] - scene_start,
                     "end": wt["end"] - scene_start}
                    for wt in c["word_timings"]
                ],
            })

        captioned = clip.transform(
            lambda gf, t, ch=adj_chunks:
                draw_captions(gf(t), t, ch, SW, SH, font_size=60)
        )
        clips.append(captioned)

    # Shorts branding overlay on first frame area
    intro  = make_intro_card(story.get("youtube_title", story["title"]),
                              duration=2.0, canvas_w=SW, canvas_h=SH)
    shorts = concatenate_videoclips([intro] + clips, method="compose")
    full_dur = shorts.duration

    if music_path and os.path.exists(music_path):
        try:
            music = AudioFileClip(music_path)
            if music.duration < full_dur:
                reps  = int(full_dur / music.duration) + 2
                music = concatenate_audioclips([music] * reps).subclipped(0, full_dur)
            else:
                music = music.subclipped(0, full_dur)
            music       = music.with_volume_scaled(0.12)
            delayed     = narration_audio.with_start(2.0)
            final_audio = CompositeAudioClip([delayed, music])
        except Exception as e:
            logger.warning(f"Shorts music mix failed: {e}")
            final_audio = narration_audio.with_start(2.0)
    else:
        final_audio = narration_audio.with_start(2.0)

    shorts = shorts.with_audio(final_audio)

    logger.info(f"Rendering Shorts → {output}")
    shorts.write_videofile(
        output, fps=FPS, codec="libx264",
        audio_codec="aac", bitrate="3000k",
        audio_bitrate="128k",
        threads=4, preset="fast", logger=None,
    )
    narration_audio.close()
    shorts.close()
    story["shorts_path"] = output
    logger.info(f"Shorts done: {output}")
    return output
