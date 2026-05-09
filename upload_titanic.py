"""
One-shot upload of the Titanic test video + Shorts to YouTube.
Run: python upload_titanic.py
"""
import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from publishing.youtube_publisher import publish_main, publish_shorts

story = {
    "title":         "Man Builds Full-Size Replica of Titanic in His Backyard, Plans to Sail It",
    "youtube_title": "Man Builds Titanic In His Backyard",
    "hook":          "A retired plumber in Kansas just finished building the Titanic. In his backyard.",
    "description_hook": "He spent 8 years. His life savings. His wife's patience.",
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
    "url":    "https://example.com/titanic-backyard",
    "source": "Bored Panda",
    "tags":   ["titanic", "backyard", "weird news", "funny", "kansas", "diy gone wrong"],
    "video_path":     "output/videos/v2test_20260507_231347_final.mp4",
    "shorts_path":    "output/shorts/v2test_20260507_231347_shorts.mp4",
    "thumbnail_path": "output/thumbnails/v2test_20260507_231347_thumb_v2.jpg",
}

run_id = "v2test_20260507_231347"

print("\nUploading main video...")
vid_id = publish_main(story, run_id)
print(f"  Main video: {story.get('youtube_video_url')}")

print("\nUploading Shorts...")
short_id = publish_shorts(story, run_id)
print(f"  Shorts: {story.get('shorts_video_url')}")

print("\nDone!")
