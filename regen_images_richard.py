"""
Regenerate only the 7 scene images for the Richard finance story
using the updated master template, then recompose the full video.
"""
import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from storage.database          import init_db
from rendering.caption_engine  import prepare_voiceover
from rendering.visual_director import generate_all_images
from rendering.audio_engine    import get_music_track
from rendering.video_composer  import compose_main_video, compose_shorts
from thumbnails.thumbnail_engine import generate_thumbnails

# Re-use same run_id so output overwrites previous render
RUN_ID = "v2finance_20260508_110207"

from test_finance_richard import STORY

def main():
    init_db()
    print("\n[1/4] Regenerating 7 images with master template...")
    generate_all_images(STORY, RUN_ID)
    print(f"  Images: {len(STORY.get('image_paths', []))} panels")

    print("\n[2/4] Re-generating audio + captions...")
    audio_path, _, caption_chunks = prepare_voiceover(STORY["narration"], RUN_ID)
    STORY["audio_path"]     = audio_path
    STORY["caption_chunks"] = caption_chunks

    shorts_path, _, s_chunks = prepare_voiceover(STORY["shorts_narration"], RUN_ID, suffix="_shorts")
    STORY["shorts_audio_path"]     = shorts_path
    STORY["shorts_caption_chunks"] = s_chunks

    music_path = get_music_track()

    print("\n[3/4] Recomposing main video + Shorts...")
    compose_main_video(STORY, audio_path, music_path, RUN_ID)
    compose_shorts(STORY, shorts_path, music_path, RUN_ID)
    print(f"  Main:   {STORY.get('video_path')}")
    print(f"  Shorts: {STORY.get('shorts_path')}")

    print("\n[4/4] Regenerating thumbnails...")
    best_thumb, all_thumbs = generate_thumbnails(STORY, RUN_ID)
    for t in all_thumbs:
        marker = " <- SELECTED" if t.get("selected") else ""
        print(f"  Thumbnail v{t['variant']}: score={t.get('total_score',0):.1f}{marker}")

    print(f"\nDone! Main video: {STORY.get('video_path')}")

    import subprocess
    for path in [STORY.get("video_path"), STORY.get("shorts_path"), best_thumb]:
        if path and os.path.exists(path):
            subprocess.Popen(["open", path])

if __name__ == "__main__":
    main()
