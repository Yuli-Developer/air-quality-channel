"""
Finance Edition — Breaking News Broadcast style.
Story: Man forgot $4,500 investment for 30 years. Woke up with $4,000,000.

Run: python test_finance_richard.py
"""

import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_finance_richard")

from datetime import datetime
from storage.database         import init_db
from rendering.caption_engine  import prepare_voiceover
from rendering.visual_director import generate_all_images
from rendering.audio_engine    import get_music_track
from rendering.video_composer  import compose_main_video, compose_shorts
from thumbnails.thumbnail_engine import generate_thumbnails


STORY = {
    "title":   "Man Forgot $4,500 Investment for 30 Years. Woke Up With $4,000,000.",
    "url":     "https://www.uniladtech.com/news/man-accidentally-became-multi-millionaire-invested-4500-591571-20250602",
    "source":  "Unilad Tech",
    "summary": "A Boston man invested $4,500 into a company in 1987, completely forgot about it, "
               "and discovered in 2024 that it had grown to $4 million through stock splits "
               "and compounding dividends. He never checked the account once.",
    "viral_score": 9.4,
    "visual_style": "news_broadcast",
    "scores": {
        "curiosity": 10, "thumbnail_strength": 9, "ragebait": 5,
        "retention_potential": 10, "comment_potential": 10,
        "shareability": 10, "shorts_potential": 9,
    },
    "youtube_title":    "He Forgot About This Investment For 30 Years. Then He Checked His Account.",
    "hook":             "In 1987, a man put $4,500 into a stock and forgot it existed. Thirty years later, he checked his account. The number did not make sense.",
    "description_hook": "He didn't check in 2008. He didn't check in 2020. He just forgot.",
    "title_variants": [
        "He Forgot About This Investment For 30 Years. Then He Checked His Account.",
        "Man Forgets $4,500 Stock For 30 Years — Wakes Up a Millionaire",
        "His Strategy Was Forgetting. It Beat 80% of Fund Managers.",
        "$4,500 → $4,000,000. He Did Absolutely Nothing.",
    ],
    "narration": (
        "In 1987, a man in Boston named Richard made a single financial decision. "
        "He invested four thousand, five hundred dollars into a company. "
        "Then he forgot about it. "
        "Not strategically. Not as a long-term play. He just forgot. "
        "Richard did not check his portfolio in 1990. Or 1995. Or 2001, when everyone else was panicking. "
        "He did not check in 2008, when the entire global financial system was on fire. "
        "He did not check when the market crashed in 2020. "
        "He did not check at all. Not once. For thirty years. "
        "In 2024, Richard found an old document in a drawer. "
        "It was his original investment paperwork. "
        "He logged into the account. "
        "The account had four million dollars in it. "
        "The stock had split. Multiple times. The dividends had compounded. For thirty years. Unattended. "
        "Richard is not a financial genius. Richard is not a day trader. Richard does not know what a P/E ratio is. "
        "Richard just didn't touch it. "
        "Meanwhile, professional fund managers — people with MBAs, Bloomberg terminals, and very expensive suits — "
        "spent thirty years actively managing money. "
        "Eighty percent of them underperformed the index. "
        "Richard underperformed nothing. "
        "Richard went on a cruise. "
        "Financial experts have reviewed Richard's strategy. "
        "They describe it as, quote, accidentally correct. "
        "Richard has described it as, quote, I just forgot. "
        "His financial advisor, when contacted, had no comment. "
        "His financial advisor did not exist until 2024. "
        "The market, for its part, continues to function normally. "
        "Richard is currently on another cruise."
    ),
    "shorts_narration": (
        "A man put four thousand dollars in a stock in 1987. "
        "He forgot about it. "
        "Did not check in 2008 when markets crashed. "
        "Did not check in 2020. "
        "Checked in 2024. "
        "Four million dollars. "
        "His strategy: forgetting. "
        "Eighty percent of professional fund managers underperformed him. "
        "Richard is on a cruise."
    ),
    "characters": (
        "Richard: late 60s, relaxed Boston man, Hawaiian shirt, reading glasses pushed up on forehead, "
        "expression of completely unearned calm. "
        "News anchor: sharp blazer, perfect hair, deeply conflicted expression trying to report this seriously. "
        "Fund managers: suits, Bloomberg terminals, visible stress, red ticker screens."
    ),
    "tags": ["finance", "investing", "stocks", "accidental millionaire", "weird news", "money", "viral finance"],
    "scenes": [
        {
            "scene_number": 1,
            "narration_segment": "In 1987, a man in Boston named Richard made a single financial decision. He invested four thousand, five hundred dollars into a company. Then he forgot about it.",
            "storyboard_description": "Professional news broadcast studio. Serious anchor at desk, giant LED screen behind her reads in bold: 'BREAKING: LOCAL MAN INVESTS $4,500 IN 1987, IMMEDIATELY FORGETS.' "
                "Bottom chyron scrolls: 'LOCAL INVESTOR ACTS ONCE, RETIRES FOREVER — MARKETS BAFFLED.' "
                "Anchor's expression: attempting gravitas. Studio lighting: blue and red accent. Breaking news red banner top of screen.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["news broadcast studio", "breaking news anchor desk"],
        },
        {
            "scene_number": 2,
            "narration_segment": "Not strategically. Not as a long-term play. He just forgot. Richard did not check his portfolio in 1990. Or 1995. Or 2001, when everyone else was panicking.",
            "storyboard_description": "Split-screen news panel: LEFT side shows Richard in 1987 casually stuffing paperwork in a kitchen drawer, expression of complete indifference, walks away whistling. "
                "RIGHT side: a news ticker at the bottom reads 'INVESTMENT STRATEGY: NONE.' "
                "Top right corner inset shows a 1990s stock graph spiking wildly — Richard's house in background, lights off, blinds closed. "
                "Chyron: 'SUBJECT UNAWARE. ACCOUNT CONTINUES.'",
            "motion_effect": "pan_right",
            "search_keywords": ["TV news split screen", "1980s home kitchen"],
        },
        {
            "scene_number": 3,
            "narration_segment": "He did not check in 2008, when the entire global financial system was on fire.",
            "storyboard_description": "Dramatic news broadcast: urgent red BREAKING banner, anchor visibly stressed, giant LED screen behind showing '2008 FINANCIAL CRISIS — MARKETS IN FREEFALL.' "
                "Graphs crash dramatically on the screen. In a small picture-in-picture inset bottom-left, Richard is visible asleep in an armchair, TV off, completely peaceful. "
                "His account balance ticks quietly upward in a tiny corner graphic. Chyron: 'ONE BOSTON MAN: STILL ASLEEP. ACCOUNT: STILL GROWING.'",
            "motion_effect": "zoom_burst",
            "search_keywords": ["2008 financial crisis news broadcast", "breaking news red banner"],
        },
        {
            "scene_number": 4,
            "narration_segment": "In 2024, Richard found an old document in a drawer. He logged into the account. The account had four million dollars in it.",
            "storyboard_description": "Extreme close-up of a laptop screen in a dimly lit room. Account balance page loads slowly. The number appears: $4,000,000.00. "
                "A news broadcast chyron overlaid at the bottom reads: 'DEVELOPING STORY — $4,000,000.' "
                "Richard's hand is frozen mid-reach for the mouse. Studio camera zooms in on the number. "
                "Red breaking news banner pulses. Cursor blinks.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["laptop screen account balance", "dramatic reveal close-up"],
        },
        {
            "scene_number": 5,
            "narration_segment": "Richard is not a financial genius. He does not know what a P/E ratio is. Richard just didn't touch it. Meanwhile, professional fund managers spent thirty years actively managing money. Eighty percent of them underperformed the index.",
            "storyboard_description": "News studio graphic segment: anchor gestures to a giant split-screen graphic. "
                "LEFT: a flat horizontal line labeled 'RICHARD'S STRATEGY (DID NOTHING)' in green, trending upward. "
                "RIGHT: a chaotic jagged line labeled 'PROFESSIONAL FUND MANAGERS (VERY BUSY)' in red, ending lower. "
                "Anchor's expression: barely concealed existential crisis. "
                "Chyron: 'EXPERTS BAFFLED BY STRATEGY OF NOT BEING AN EXPERT.'",
            "motion_effect": "pan_left",
            "search_keywords": ["news anchor stock chart graphic", "financial data visualization TV"],
        },
        {
            "scene_number": 6,
            "narration_segment": "Financial experts have reviewed Richard's strategy. They describe it as accidentally correct. Richard has described it as: I just forgot.",
            "storyboard_description": "News broadcast interview panel: two financial analysts at desks, ties slightly loosened, looking at each other in silence. "
                "A graphic lower-third reads: 'EXPERT ANALYSIS: ACCIDENTALLY CORRECT.' "
                "In a separate inset box, a quote card appears on screen: '\"I just forgot.\" — Richard.' "
                "Both analysts stare at the camera. Nobody speaks. Chyron scrolls: 'MBA PROGRAMS REVIEWING CURRICULUM.'",
            "motion_effect": "ken_burns_zoom_out",
            "search_keywords": ["news panel discussion two experts", "TV studio interview"],
        },
        {
            "scene_number": 7,
            "narration_segment": "Richard is currently on another cruise. The market continues to function normally.",
            "storyboard_description": "Wide aerial shot of a cruise ship at sea, sun setting behind it. A news helicopter chyron overlay in corner reads 'LIVE.' "
                "At the bow of the ship, a tiny figure in a Hawaiian shirt stands with arms slightly out, relaxed, completely unbothered. "
                "Bottom chyron: 'RICHARD COULD NOT BE REACHED FOR COMMENT. HE IS ON A CRUISE.' "
                "Breaking news banner: 'MARKETS: NORMAL. RICHARD: ALSO NORMAL.' Slow zoom out.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["cruise ship aerial ocean sunset", "news helicopter live shot"],
        },
    ],
    "shorts_scenes": [
        {"scene_number": 1, "narration_segment": "A man put four thousand dollars in a stock in 1987 and forgot about it.", "storyboard_description": "News anchor breaking story: 'BREAKING: MAN FORGETS INVESTMENT.' Chyron scrolls below.", "duration_seconds": 9},
        {"scene_number": 2, "narration_segment": "Did not check in 2008. Did not check in 2020.", "storyboard_description": "Split screen: 2008 crisis news broadcast on TV, Richard asleep next to it.", "duration_seconds": 8},
        {"scene_number": 3, "narration_segment": "Checked in 2024. Four million dollars.", "storyboard_description": "Laptop screen: $4,000,000.00. Red BREAKING chyron. Cursor blinks.", "duration_seconds": 9},
        {"scene_number": 4, "narration_segment": "His strategy was forgetting. Richard is on a cruise.", "storyboard_description": "Aerial cruise ship shot. Chyron: 'COULD NOT BE REACHED FOR COMMENT. ON A CRUISE.'", "duration_seconds": 11},
    ],
}


def run_test():
    init_db()
    run_id = f"v2finance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"=== Breaking Weird Finance | news_broadcast style | run={run_id} ===")

    print(f"\n{'='*60}")
    print(f"STORY: {STORY['title']}")
    print(f"STYLE: {STORY['visual_style']}")
    print(f"{'='*60}")

    print("\n[1/6] Generating 7 news broadcast scene images...")
    generate_all_images(STORY, run_id)
    print(f"  Images: {len(STORY.get('image_paths', []))} panels")

    print("\n[2/6] Generating main voiceover + captions...")
    audio_path, _, caption_chunks = prepare_voiceover(STORY["narration"], run_id)
    STORY["audio_path"]     = audio_path
    STORY["caption_chunks"] = caption_chunks
    print(f"  Audio: {audio_path}")
    print(f"  Caption chunks: {len(caption_chunks)}")

    print("\n[3/6] Generating Shorts voiceover...")
    s_audio, _, s_chunks = prepare_voiceover(STORY["shorts_narration"], run_id, suffix="_shorts")
    STORY["shorts_audio_path"]     = s_audio
    STORY["shorts_caption_chunks"] = s_chunks

    print("\n[4/6] Getting background music...")
    music_path = get_music_track()
    print(f"  Music: {music_path}")

    print("\n[5/6] Composing main video + Shorts...")
    compose_main_video(STORY, audio_path, music_path, run_id)
    compose_shorts(STORY, s_audio, music_path, run_id)
    print(f"  Main:   {STORY.get('video_path')}")
    print(f"  Shorts: {STORY.get('shorts_path')}")

    print("\n[6/6] Generating & scoring 4 thumbnail variants...")
    best_thumb, all_thumbs = generate_thumbnails(STORY, run_id)
    for t in all_thumbs:
        marker = " <- SELECTED" if t.get("selected") else ""
        print(f"  Thumbnail v{t['variant']}: score={t.get('total_score', 0):.1f}{marker}")

    print(f"\n{'='*60}")
    print(f"Finance test complete!")
    print(f"Main video:  {STORY.get('video_path')}")
    print(f"Shorts:      {STORY.get('shorts_path')}")
    print(f"Thumbnail:   {best_thumb}")
    print(f"{'='*60}\n")

    import subprocess
    for path in [STORY.get("video_path"), STORY.get("shorts_path"), best_thumb]:
        if path and os.path.exists(path):
            subprocess.Popen(["open", path])

    return STORY


if __name__ == "__main__":
    run_test()
