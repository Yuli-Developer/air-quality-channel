"""
Upload the Richard finance video + Shorts to YouTube.
Run: python upload_finance_richard.py
"""
import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from publishing.youtube_publisher import publish_main, publish_shorts

story = {
    "title":         "Man Forgot $4,500 Investment for 30 Years. Woke Up With $4,000,000.",
    "youtube_title": "He Forgot About This Investment For 30 Years. Then He Checked His Account.",
    "hook":          "In 1987, a man put $4,500 into a stock and forgot it existed. Thirty years later, he checked his account. The number did not make sense.",
    "description_hook": "He didn't check in 2008. He didn't check in 2020. He just forgot.",
    "narration": (
        "In 1987, a man in Boston named Richard made a single financial decision. "
        "He invested four thousand, five hundred dollars into a company. "
        "Then he forgot about it. Not strategically. Not as a long-term play. He just forgot. "
        "Richard did not check his portfolio in 1990. Or 1995. Or 2001, when everyone else was panicking. "
        "He did not check in 2008, when the entire global financial system was on fire. "
        "He did not check when the market crashed in 2020. He did not check at all. Not once. For thirty years. "
        "In 2024, Richard found an old document in a drawer. He logged into the account. "
        "The account had four million dollars in it. "
        "Richard is not a financial genius. Richard does not know what a P/E ratio is. Richard just didn't touch it. "
        "Eighty percent of professional fund managers underperformed the index. Richard underperformed nothing. "
        "Richard is currently on another cruise."
    ),
    "url":    "https://www.uniladtech.com/news/man-accidentally-became-multi-millionaire-invested-4500-591571-20250602",
    "source": "Unilad Tech",
    "tags":   [
        "finance", "investing", "stocks", "accidental millionaire", "weird news",
        "money", "viral finance", "stock market", "personal finance", "investing tips",
        "breaking weird", "funny finance", "wealth", "passive investing",
    ],
    "video_path":     "output/videos/v2finance_20260508_110207_final.mp4",
    "shorts_path":    "output/shorts/v2finance_20260508_110207_shorts.mp4",
    "thumbnail_path": "output/thumbnails/v2finance_20260508_110207_thumb_v1.jpg",
}

run_id = "v2finance_20260508_110207"

print("\nUploading main video...")
vid_id = publish_main(story, run_id)
print(f"  Main:   {story.get('youtube_video_url')}")

print("\nUploading Shorts...")
short_id = publish_shorts(story, run_id)
print(f"  Shorts: {story.get('shorts_video_url')}")

print("\nDone!")
