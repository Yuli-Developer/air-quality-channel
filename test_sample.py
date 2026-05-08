"""
v2 sample test — runs full pipeline on a hardcoded story, no upload.
Tests all systems: images, voiceover, captions, motion effects, thumbnails, video assembly.

Run: python test_sample.py
     python test_sample.py --style horror_documentary
     python test_sample.py --style sarcastic
"""

import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_sample")

from datetime import datetime
from storage.database        import init_db
from rendering.caption_engine import prepare_voiceover
from rendering.visual_director import generate_all_images
from rendering.audio_engine    import get_music_track
from rendering.video_composer  import compose_main_video, compose_shorts
from thumbnails.thumbnail_engine import generate_thumbnails

SAMPLE_STORY = {
    "title":   "Man Builds Full-Size Replica of Titanic in His Backyard, Plans to Sail It",
    "url":     "https://example.com/titanic-backyard",
    "source":  "Bored Panda",
    "summary": "A retired plumber in rural Kansas spent 8 years and his life savings "
               "constructing a full-size replica of the Titanic in his backyard. "
               "He now plans to float it down the local creek to the ocean. "
               "Experts have concerns. His wife has more.",
    "viral_score": 9.2,
    "scores": {
        "curiosity": 10, "thumbnail_strength": 9, "ragebait": 6,
        "retention_potential": 9, "comment_potential": 8,
        "shareability": 9, "shorts_potential": 8,
    },
    "youtube_title":    "Man Builds Titanic In His Backyard",
    "hook":             "A retired plumber in Kansas just finished building the Titanic. In his backyard.",
    "description_hook": "He spent 8 years. His life savings. His wife's patience.",
    "title_variants": [
        "Man Builds Titanic In His Backyard",
        "This Man Spent 8 Years Building The Titanic... At Home",
        "Kansas Man's Backyard Titanic Has Experts Worried",
        "He Built A Full-Size Titanic. His Wife Is Done.",
    ],
    "narration": (
        "In Wichita, Kansas, where the nearest ocean is approximately one thousand miles away, "
        "a retired plumber named Gerald has just completed an eight-year project. "
        "He built the Titanic. Not a model. Not a replica. The Titanic. Full size. In his backyard. "
        "Gerald says he was inspired by the 1997 film. "
        "His wife, Patricia, says she was not consulted. "
        "The ship is four hundred and eighty-two feet long. "
        "The backyard is five hundred feet long. "
        "Gerald considers this 'plenty of room.' "
        "When asked how he plans to get it to water, Gerald pointed to the creek behind his property. "
        "The creek is twelve feet wide. "
        "Structural engineers have reviewed Gerald's plans. "
        "They have used words like 'inadvisable,' 'structurally impossible,' and 'please stop.' "
        "Gerald has dismissed these concerns as 'negativity.' "
        "His GoFundMe for the maiden voyage has raised forty-seven dollars. "
        "Thirty-two of those dollars came from Gerald. "
        "Patricia has moved to her sister's house. "
        "Gerald says she will come around once the ship sets sail. "
        "The ship has not yet set sail. "
        "The ship may never set sail. "
        "But Gerald remains optimistic, standing on the bow of his landlocked Titanic, "
        "arms outstretched, wind in his hair, surrounded by corn."
    ),
    "shorts_narration": (
        "A man in Kansas just finished building the Titanic. "
        "Full size. In his backyard. "
        "The nearest ocean is one thousand miles away. "
        "He has a plan. His wife has left. "
        "Structural engineers have used words like 'inadvisable' and 'please stop.' "
        "Gerald remains optimistic."
    ),
    "characters": (
        "Gerald: retired plumber, 60s, weathered hands, overalls, hard hat, "
        "perpetually confident grin, measuring tape in pocket. "
        "Patricia: Gerald's wife, arms crossed, expression of exhausted disbelief, suitcase nearby."
    ),
    "tags": ["titanic", "backyard", "weird news", "funny", "kansas", "diy gone wrong"],
    "scenes": [
        {
            "scene_number": 1,
            "narration_segment": "In Wichita, Kansas, where the nearest ocean is approximately one thousand miles away, a retired plumber named Gerald has just completed an eight-year project.",
            "storyboard_description": "Wide aerial establishing shot over a suburban Kansas neighborhood. A colossal ship occupies one backyard, dwarfing every house around it. Corn fields stretch to the horizon. A tiny figure stands on the bow. Director annotation: TITANIC arrow pointing to the ship, KANSAS arrow pointing to corn.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["backyard construction", "suburban house"],
        },
        {
            "scene_number": 2,
            "narration_segment": "He built the Titanic. Not a model. Not a replica. The Titanic. Full size. In his backyard.",
            "storyboard_description": "Close-up extreme facial expression of Gerald on the bow of the ship. Titanic pose, arms wide, expression of pure triumphant madness. Behind him the ship's massive hull. Speed lines radiate from his grin. Motion lines everywhere.",
            "motion_effect": "zoom_burst",
            "search_keywords": ["happy man", "proud builder"],
        },
        {
            "scene_number": 3,
            "narration_segment": "His wife Patricia says she was not consulted. The ship is four hundred and eighty-two feet long. The backyard is five hundred feet long. Gerald considers this plenty of room.",
            "storyboard_description": "Over-the-shoulder shot from behind Patricia looking at the ship which fills the entire frame. Her posture: arms crossed, foot tapping. A measuring tape on the ground shows '482ft.' Gerald in background holds up thumb approvingly. Sweat drops around Patricia's head.",
            "motion_effect": "pan_right",
            "search_keywords": ["frustrated woman", "construction project"],
        },
        {
            "scene_number": 4,
            "narration_segment": "When asked how he plans to get it to water, Gerald pointed to the creek behind his property. The creek is twelve feet wide.",
            "storyboard_description": "Dutch angle shot: Gerald's finger pointing confidently off-panel. Cut to the twelve-foot creek — a tiny trickle with a rubber duck floating in it. The Titanic looms in the background. Scale comparison lines show 12ft vs 482ft. Gerald's expression: complete conviction.",
            "motion_effect": "pan_left",
            "search_keywords": ["small creek river", "water stream"],
        },
        {
            "scene_number": 5,
            "narration_segment": "Structural engineers have reviewed Gerald's plans. They have used words like inadvisable, structurally impossible, and please stop.",
            "storyboard_description": "Low angle shot of three engineers in hard hats staring up at the ship in horror. One holds blueprints that are covered in red X marks. Sweat beads and exclamation marks fill the panel. The ship towers above them, slightly tilted. A thought bubble shows the Titanic sinking.",
            "motion_effect": "ken_burns_zoom_out",
            "search_keywords": ["engineers concerned", "construction plans"],
        },
        {
            "scene_number": 6,
            "narration_segment": "His GoFundMe has raised forty-seven dollars. Thirty-two of those dollars came from Gerald. Patricia has moved to her sister's house.",
            "storyboard_description": "Aerial bird's-eye view split panel: left side shows a GoFundMe page with '$47' in giant text and a sad progress bar at 0.0001%. Right side shows Patricia dragging a suitcase toward a taxi, not looking back. Gerald waves from the ship's deck obliviously.",
            "motion_effect": "pan_right",
            "search_keywords": ["crowdfunding failure", "woman leaving"],
        },
        {
            "scene_number": 7,
            "narration_segment": "Gerald remains optimistic, standing on the bow of his landlocked Titanic, arms outstretched, surrounded by corn.",
            "storyboard_description": "Extreme wide shot: Gerald on the bow, Titanic pose, surrounded entirely by corn fields. No water in sight. The ship goes nowhere. Corn everywhere. Gerald's expression: complete, unshakeable peace. A single corn stalk bends in the wind. A caption reads: 'Day 2,921.'",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["corn field", "rural landscape"],
        },
    ],
    "shorts_scenes": [
        {"scene_number": 1, "narration_segment": "A man in Kansas just finished building the Titanic. Full size. In his backyard.", "storyboard_description": "Aerial view of Titanic in backyard surrounded by corn.", "duration_seconds": 10},
        {"scene_number": 2, "narration_segment": "The nearest ocean is one thousand miles away. He has a plan.", "storyboard_description": "Gerald pointing confidently at a tiny creek.", "duration_seconds": 8},
        {"scene_number": 3, "narration_segment": "His wife has left. Structural engineers say please stop.", "storyboard_description": "Patricia leaving with suitcase, engineers in horror.", "duration_seconds": 9},
        {"scene_number": 4, "narration_segment": "Gerald remains optimistic. Surrounded by corn.", "storyboard_description": "Gerald on bow doing Titanic pose, corn everywhere.", "duration_seconds": 10},
    ],
}


def run_test(style: str = "deadpan"):
    init_db()
    run_id = f"v2test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    story  = {**SAMPLE_STORY}
    logger.info(f"=== Breaking Weird v2 Test | style={style} | run={run_id} ===")

    # Step 1: Images
    print("\n[1/6] Generating 7 anime storyboard images...")
    generate_all_images(story, run_id)
    print(f"  Images: {len(story.get('image_paths', []))} panels")

    # Step 2: Main voiceover + captions
    print("\n[2/6] Generating voiceover + captions...")
    audio_path, _, caption_chunks = prepare_voiceover(story["narration"], run_id)
    story["audio_path"]     = audio_path
    story["caption_chunks"] = caption_chunks
    print(f"  Audio: {audio_path}")
    print(f"  Caption chunks: {len(caption_chunks)}")

    # Step 3: Shorts voiceover
    print("\n[3/6] Generating Shorts voiceover...")
    s_audio, _, s_chunks = prepare_voiceover(story["shorts_narration"], run_id, suffix="_shorts")
    story["shorts_audio_path"]     = s_audio
    story["shorts_caption_chunks"] = s_chunks

    # Step 4: Music
    print("\n[4/6] Getting background music...")
    music_path = get_music_track()
    print(f"  Music: {music_path}")

    # Step 5: Compose main + shorts
    print("\n[5/6] Composing main video + Shorts...")
    compose_main_video(story, audio_path, music_path, run_id)
    compose_shorts(story, s_audio, music_path, run_id)
    print(f"  Main:   {story.get('video_path')}")
    print(f"  Shorts: {story.get('shorts_path')}")

    # Step 6: Thumbnails
    print("\n[6/6] Generating & scoring 4 thumbnail variants...")
    best_thumb, all_thumbs = generate_thumbnails(story, run_id)
    for t in all_thumbs:
        marker = " ← SELECTED" if t.get("selected") else ""
        print(f"  Thumbnail v{t['variant']}: score={t.get('total_score', 0):.1f}{marker}")

    print(f"\n{'='*60}")
    print(f"Test complete!")
    print(f"Main video:  {story.get('video_path')}")
    print(f"Shorts:      {story.get('shorts_path')}")
    print(f"Thumbnail:   {best_thumb}")
    print(f"{'='*60}")

    import subprocess
    for path in [story.get("video_path"), story.get("shorts_path"), best_thumb]:
        if path and os.path.exists(path):
            subprocess.Popen(["open", path])

    return story


if __name__ == "__main__":
    style = "deadpan"
    if "--style" in sys.argv:
        idx   = sys.argv.index("--style")
        style = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "deadpan"
    run_test(style=style)
