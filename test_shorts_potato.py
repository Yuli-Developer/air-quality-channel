"""
End-to-end Shorts-only test — Finance weird story.
Story: Potato CFDs surged 705% in one month, beating Bitcoin, Nasdaq, and gold.

Tests full pipeline:
  Gemini script → portrait images (1080x1920) → Ryan voice → compose Shorts → thumbnails → upload

Run: python test_shorts_potato.py
     python test_shorts_potato.py --no-upload
"""

import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_shorts_potato")

from datetime import datetime
from storage.database          import init_db
from ai.narrative_generator    import generate_script
from rendering.visual_director import generate_all_images
from rendering.kling_engine    import generate_all_kling_videos
from rendering.caption_engine  import prepare_voiceover
from rendering.audio_engine    import get_music_track
from rendering.video_composer  import compose_shorts
from thumbnails.thumbnail_engine import generate_thumbnails
from publishing.youtube_publisher import publish_shorts

STORY = {
    "title":       "The Best Trade of the Month Wasn't Crypto or Oil. It Was Potatoes.",
    "url":         "https://beincrypto.com/best-trade-of-the-month-not-crypto-oil-stocks/",
    "source":      "Yahoo Finance / BeInCrypto",
    "summary":     (
        "Potato CFDs surged 705% in less than a month, beating Bitcoin, Nasdaq, and gold "
        "as Iran war speculation roiled commodity markets. Traders who accidentally held "
        "potato futures while trying to buy oil made the trade of the year. "
        "Financial analysts are struggling to explain this with a straight face."
    ),
    "viral_score": 9.6,
    "visual_style": "news_broadcast",
}


def run_test(upload: bool = True):
    init_db()
    run_id = f"v2shorts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"=== Shorts Pipeline Test | run={run_id} ===")

    print(f"\n{'='*60}")
    print(f"STORY: {STORY['title']}")
    print(f"MODE:  Shorts-only | Portrait 1080x1920 | Ryan voice")
    print(f"{'='*60}")

    # Step 1: Gemini generates Shorts script (4 scenes, ~130 words)
    print("\n[1/6] Generating Shorts script via Gemini...")
    story = generate_script(STORY, style="deadpan")
    print(f"  Title:     {story['youtube_title']}")
    print(f"  Words:     {len(story['narration'].split())}")
    print(f"  Scenes:    {len(story['scenes'])}")
    print(f"  Hook:      {story['hook'][:80]}")
    print(f"\n  --- NARRATION ---")
    print(f"  {story['narration']}")
    print(f"  ----------------")

    # Step 2: Portrait images (1080x1920)
    print("\n[2/6] Generating 4 portrait images (1080x1920)...")
    generate_all_images(story, run_id)
    print(f"  Images: {len(story.get('image_paths', []))} panels")

    # Step 2b: Kling AI video clips (if USE_KLING=true)
    print("\n[2b] Generating Kling AI video clips (if enabled)...")
    kling_paths = generate_all_kling_videos(story, run_id)
    print(f"  Kling clips: {len(kling_paths)}/4 scenes")

    # Step 3: Voiceover (Ryan British)
    print("\n[3/6] Generating voiceover (en-GB-RyanNeural)...")
    audio_path, _, caption_chunks = prepare_voiceover(story["narration"], run_id, suffix="_shorts")
    story["shorts_audio_path"]     = audio_path
    story["shorts_caption_chunks"] = caption_chunks
    print(f"  Audio: {audio_path}")
    print(f"  Duration: check log above | Chunks: {len(caption_chunks)}")

    # Step 4: Music
    print("\n[4/6] Getting background music...")
    music_path = get_music_track()
    print(f"  Music: {music_path}")

    # Step 5: Compose Shorts (9:16 portrait)
    print("\n[5/6] Composing Shorts (9:16 portrait)...")
    compose_shorts(story, audio_path, music_path, run_id)
    print(f"  Shorts: {story.get('shorts_path')}")

    # Step 6: Thumbnails
    print("\n[6/6] Generating & scoring thumbnails...")
    best_thumb, all_thumbs = generate_thumbnails(story, run_id)
    for t in all_thumbs:
        marker = " <- SELECTED" if t.get("selected") else ""
        print(f"  Thumbnail v{t['variant']}: score={t.get('total_score', 0):.1f}{marker}")

    print(f"\n{'='*60}")
    print(f"Shorts: {story.get('shorts_path')}")
    print(f"Thumb:  {best_thumb}")
    print(f"{'='*60}\n")

    import subprocess
    for path in [story.get("shorts_path"), best_thumb]:
        if path and os.path.exists(path):
            subprocess.Popen(["open", path])

    # Step 7: Upload
    if upload:
        print("\n[7/6] Uploading to YouTube Shorts...")
        vid_id = publish_shorts(story, run_id)
        print(f"\n  LIVE: {story.get('shorts_video_url')}")

    return story


if __name__ == "__main__":
    upload = "--no-upload" not in sys.argv
    run_test(upload=upload)
