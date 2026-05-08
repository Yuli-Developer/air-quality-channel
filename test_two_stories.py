"""
Two additional sample stories for Breaking Weird v2.

Story 1: Man applies for a job at the company he founded — gets rejected by HR.
Story 2: Woman wins divorce after citing husband's loud breathing as grounds.

Run:
    python test_two_stories.py --story 1
    python test_two_stories.py --story 2
    python test_two_stories.py          # runs both sequentially
"""

import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_two_stories")

from datetime import datetime
from storage.database        import init_db
from rendering.caption_engine import prepare_voiceover
from rendering.visual_director import generate_all_images
from rendering.audio_engine    import get_music_track
from rendering.video_composer  import compose_main_video, compose_shorts
from thumbnails.thumbnail_engine import generate_thumbnails


# ── Story 1 ──────────────────────────────────────────────────────────────────

STORY_FIRED_FOUNDER = {
    "title":   "Man Applies for Job at Company He Founded, Gets Rejected by HR",
    "url":     "https://example.com/founder-rejected",
    "source":  "LinkedIn News",
    "summary": "A Silicon Valley founder who stepped down from his own startup "
               "re-applied for his old position as a senior engineer. "
               "He was auto-rejected by the applicant tracking system he built. "
               "His resume was flagged for a six-month employment gap.",
    "viral_score": 9.5,
    "scores": {
        "curiosity": 10, "thumbnail_strength": 9, "ragebait": 8,
        "retention_potential": 9, "comment_potential": 10,
        "shareability": 10, "shorts_potential": 9,
    },
    "youtube_title":    "He Founded The Company. They Rejected His Resume.",
    "hook":             "He built the company. He wrote the hiring software. It rejected him.",
    "description_hook": "Six years. Two funding rounds. One employment gap flag.",
    "title_variants": [
        "He Founded The Company. They Rejected His Resume.",
        "This Man Got Rejected By His Own Company's HR Bot",
        "Silicon Valley Founder Can't Get His Own Job Back",
        "The AI He Built Rejected His Job Application",
    ],
    "narration": (
        "In San Francisco, a man named Derek spent six years building a startup from scratch. "
        "He wrote the business plan. He hired the engineers. "
        "He built the applicant tracking system that screened every resume that came through the door. "
        "Then, in 2023, Derek stepped down as CEO for what he called 'personal reasons.' "
        "The personal reason was burnout. Also his co-founder. Also both at the same time. "
        "After six months of rest, Derek decided he wanted back in. "
        "Not as CEO. Just as a senior engineer. Quietly. Humbly. "
        "He submitted his resume through the company website. "
        "His resume — the one that listed 'Founder and CEO' at the top — "
        "was automatically rejected within four seconds. "
        "The rejection email cited, quote, 'insufficient recent experience.' "
        "Derek had a six-month gap. The system he built flagged six-month gaps. "
        "He emailed HR. HR said the decision was final. "
        "He emailed the new CEO. The new CEO was someone Derek had hired. "
        "That email has not been returned. "
        "Derek posted about this on LinkedIn. "
        "The post has four hundred thousand likes. "
        "HR has not commented. "
        "The applicant tracking system has also not commented, "
        "but if it could, it would probably say the decision was final."
    ),
    "shorts_narration": (
        "A man built a startup from scratch. "
        "He built the hiring software. "
        "He stepped down. He applied for his old job. "
        "His own system rejected him in four seconds. "
        "Insufficient recent experience. "
        "The new CEO was someone he hired. "
        "That email has not been returned."
    ),
    "characters": (
        "Derek: mid-40s tech founder, slightly rumpled button-down, expensive watch, "
        "exhausted eyes, staring at a laptop screen in disbelief. "
        "HR Bot: represented as a glowing red robot stamp labeled REJECTED, "
        "cheerful expression, completely indifferent."
    ),
    "tags": ["tech", "startup", "fired", "HR", "Silicon Valley", "viral LinkedIn", "weird news"],
    "scenes": [
        {
            "scene_number": 1,
            "narration_segment": "In San Francisco, a man named Derek spent six years building a startup from scratch.",
            "storyboard_description": "Wide establishing shot of a sleek San Francisco office building at golden hour. "
                "A neon sign reads the company name. Through the glass, a lone figure sits at the founder's desk, surrounded by whiteboards covered in diagrams. "
                "Speed lines radiate from the building as if it's launching into orbit.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["startup office", "Silicon Valley building"],
        },
        {
            "scene_number": 2,
            "narration_segment": "He wrote the business plan. He hired the engineers. He built the applicant tracking system that screened every resume.",
            "storyboard_description": "Montage panel: Derek at a whiteboard drawing flowcharts, then shaking hands with engineers, "
                "then at a keyboard coding furiously. Speed lines everywhere. Sweat beads. Confidence radiates from him like a manga protagonist powering up.",
            "motion_effect": "zoom_burst",
            "search_keywords": ["programmer coding", "startup team"],
        },
        {
            "scene_number": 3,
            "narration_segment": "Derek stepped down as CEO for personal reasons. The personal reason was burnout. Also his co-founder. Also both at the same time.",
            "storyboard_description": "Extreme close-up of Derek's face, one eye twitching, a forced professional smile. "
                "Behind him, the office is slightly on fire. His co-founder stands in the background with arms crossed. "
                "A speech bubble from Derek says 'PERSONAL REASONS.' Ellipsis dot-dot-dot from the co-founder.",
            "motion_effect": "pan_right",
            "search_keywords": ["stressed businessman", "office burnout"],
        },
        {
            "scene_number": 4,
            "narration_segment": "Derek submitted his resume through the company website. It was automatically rejected within four seconds.",
            "storyboard_description": "Split panel: left — Derek clicking SUBMIT on a laptop, expression of cautious optimism. "
                "Right — a giant red REJECTED stamp crashes down in 0.4 seconds with a massive impact explosion. "
                "The stamp has googly eyes and is labeled 'YOUR OWN SYSTEM.' Shockwave lines everywhere.",
            "motion_effect": "pan_left",
            "search_keywords": ["job rejection letter", "computer screen"],
        },
        {
            "scene_number": 5,
            "narration_segment": "The rejection cited insufficient recent experience. Derek had a six-month gap. The system he built flagged six-month gaps.",
            "storyboard_description": "Close-up of Derek reading the rejection email on his phone. His expression: the exact face of a man realizing he has been destroyed by his own creation. "
                "In the background, a shadowy robot holds a clipboard labeled 'DEREK'S RULES.' A thought bubble shows a snake eating itself.",
            "motion_effect": "ken_burns_zoom_out",
            "search_keywords": ["man reading bad news phone", "disappointed businessman"],
        },
        {
            "scene_number": 6,
            "narration_segment": "He emailed the new CEO. The new CEO was someone Derek had hired. That email has not been returned.",
            "storyboard_description": "Over-the-shoulder shot of Derek typing an email. The recipient name glows ominously. "
                "Cut to the new CEO's inbox — Derek's email sits at the bottom, buried under a thousand other emails, slowly sinking. "
                "The CEO avatar has a tiny crown and a smug expression.",
            "motion_effect": "pan_right",
            "search_keywords": ["email inbox unread", "corporate office"],
        },
        {
            "scene_number": 7,
            "narration_segment": "Derek posted about this on LinkedIn. The post has four hundred thousand likes. HR has not commented.",
            "storyboard_description": "Extreme wide shot: Derek sitting alone with a laptop, the LinkedIn logo glowing above him like a beacon. "
                "The like counter spins upward: 10k... 100k... 400k. Confetti falls. Derek's expression: deeply conflicted satisfaction. "
                "In a small corner panel, an HR department building sits in darkness, blinds closed, a sign: 'NO COMMENT.'",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["viral social media post", "LinkedIn notification"],
        },
    ],
    "shorts_scenes": [
        {"scene_number": 1, "narration_segment": "A man built a startup from scratch.", "storyboard_description": "Derek founding his company, speed lines radiating.", "duration_seconds": 8},
        {"scene_number": 2, "narration_segment": "He built the hiring software. He stepped down.", "storyboard_description": "Derek coding the system, then clearing his desk.", "duration_seconds": 8},
        {"scene_number": 3, "narration_segment": "He applied for his old job. His own system rejected him in four seconds.", "storyboard_description": "REJECTED stamp crashing down with explosion.", "duration_seconds": 9},
        {"scene_number": 4, "narration_segment": "The new CEO was someone he hired. That email has not been returned.", "storyboard_description": "Derek staring at unanswered email, 400k LinkedIn likes rising.", "duration_seconds": 12},
    ],
}


# ── Story 2 ──────────────────────────────────────────────────────────────────

STORY_BREATHING_DIVORCE = {
    "title":   "Woman Wins Divorce After Citing Husband's Loud Breathing as Grounds",
    "url":     "https://example.com/breathing-divorce",
    "source":  "The Independent",
    "summary": "A court in Austria granted a woman a divorce after she successfully argued "
               "that her husband's loud breathing during sleep made cohabitation impossible. "
               "The judge agreed. The husband said he was just breathing. "
               "His lawyer said it was a dark day for breathing.",
    "viral_score": 9.3,
    "scores": {
        "curiosity": 9, "thumbnail_strength": 9, "ragebait": 7,
        "retention_potential": 9, "comment_potential": 10,
        "shareability": 10, "shorts_potential": 9,
    },
    "youtube_title":    "She Divorced Him For Breathing Too Loud. The Judge Said Yes.",
    "hook":             "She filed for divorce. The reason: breathing.",
    "description_hook": "His lawyer called it a dark day for breathing.",
    "title_variants": [
        "She Divorced Him For Breathing Too Loud. The Judge Said Yes.",
        "Austrian Court Rules Loud Breathing Is Grounds For Divorce",
        "Woman Wins Divorce. Husband's Crime: Existing While Asleep.",
        "His Lawyer Said It Was A Dark Day For Breathing",
    ],
    "narration": (
        "In Vienna, Austria, a woman named Helga filed for divorce from her husband Klaus. "
        "Not for infidelity. Not for financial misconduct. Not for anything that has ever been "
        "cited in a divorce filing in the history of jurisprudence. "
        "Helga filed for divorce because Klaus breathes too loud. "
        "Specifically, during sleep. "
        "Klaus, for his part, maintains that he was simply breathing. "
        "This is technically accurate. "
        "Helga's lawyers argued that Klaus's breathing constituted, quote, "
        "'a persistent violation of the marital atmosphere.' "
        "They brought recordings. "
        "The recordings were described in court documents as 'distressing.' "
        "Klaus's lawyer argued that breathing is, and has always been, "
        "a biological necessity and not a punishable offense. "
        "The judge listened to both arguments. "
        "The judge listened to the recordings. "
        "The judge granted the divorce. "
        "Klaus was issued sole custody of his own lungs. "
        "His lawyer released a statement calling it, quote, "
        "'a dark day for breathing.' "
        "Legal scholars have called it unprecedented. "
        "Respiratory physicians have called it concerning. "
        "Helga has called it long overdue. "
        "Klaus, when reached for comment, said nothing. "
        "He was, at the time, breathing quietly."
    ),
    "shorts_narration": (
        "A woman in Austria filed for divorce. "
        "The reason: her husband breathed too loud. "
        "The judge heard recordings. "
        "The judge agreed. "
        "Klaus's lawyer called it a dark day for breathing. "
        "Klaus had no comment. He was breathing quietly."
    ),
    "characters": (
        "Helga: late 50s, composed Austrian woman, impeccable posture, noise-canceling headphones around her neck, "
        "expression of long-suffering vindication. "
        "Klaus: slightly rumpled middle-aged man, mouth slightly open, genuinely confused expression, "
        "breathing visibly through his nose. "
        "The Judge: stern, robes, gavel, deeply weary expression."
    ),
    "tags": ["divorce", "Austria", "weird news", "funny court", "viral", "bizarre", "relationships"],
    "scenes": [
        {
            "scene_number": 1,
            "narration_segment": "In Vienna, Austria, a woman named Helga filed for divorce from her husband Klaus.",
            "storyboard_description": "Wide establishing shot of a Viennese courthouse, ornate and imposing. "
                "Through one window, a silhouette of Helga stands with perfect posture. Through another, "
                "Klaus sits slumped with a question mark over his head. The filing papers flutter dramatically.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["courthouse Vienna Austria", "European court building"],
        },
        {
            "scene_number": 2,
            "narration_segment": "Helga filed for divorce because Klaus breathes too loud. Specifically, during sleep.",
            "storyboard_description": "Night scene split panel: left — Helga lying rigid in bed, fully awake, "
                "sweat beads on forehead, eyes wide open, headphones on. Right — Klaus asleep peacefully, "
                "massive sound waves emanating from his nose, each wave labeled 'INHALE' and 'EXHALE.' "
                "The waves are visually identical to a submarine sonar ping.",
            "motion_effect": "zoom_burst",
            "search_keywords": ["couple sleeping bedroom", "snoring husband"],
        },
        {
            "scene_number": 3,
            "narration_segment": "Helga's lawyers argued his breathing constituted a persistent violation of the marital atmosphere. They brought recordings.",
            "storyboard_description": "Courtroom scene: Helga's lawyer gestures dramatically at a speaker playing audio. "
                "Sound wave lines burst outward from the speaker. The judge, jurors, and court reporter all lean back in their chairs simultaneously. "
                "Klaus in the dock, genuinely confused, looking at his own chest as if betrayed by it.",
            "motion_effect": "pan_right",
            "search_keywords": ["courtroom lawyer dramatic", "court trial scene"],
        },
        {
            "scene_number": 4,
            "narration_segment": "Klaus's lawyer argued that breathing is a biological necessity and not a punishable offense.",
            "storyboard_description": "Klaus's lawyer stands in full dramatic pose, pointing skyward, light shining down from above. "
                "Behind him, a banner reads 'BREATHING IS NOT A CRIME.' Klaus nods eagerly. "
                "A small anatomical diagram of lungs glows heroically. Speed lines of righteous determination everywhere.",
            "motion_effect": "pan_left",
            "search_keywords": ["defense lawyer dramatic courtroom", "justice scales"],
        },
        {
            "scene_number": 5,
            "narration_segment": "The judge listened to the recordings. The judge granted the divorce.",
            "storyboard_description": "Close-up of the judge's face: stoic, measured, then a slow, decisive nod. "
                "The gavel falls in slow motion with a massive impact explosion. "
                "Papers scatter. Klaus's expression goes from confusion to devastation to resigned acceptance. "
                "A single tear rolls down his cheek while his lungs continue functioning normally.",
            "motion_effect": "ken_burns_zoom_out",
            "search_keywords": ["judge gavel courthouse ruling", "court decision"],
        },
        {
            "scene_number": 6,
            "narration_segment": "His lawyer released a statement calling it a dark day for breathing. Legal scholars called it unprecedented.",
            "storyboard_description": "Exterior courthouse steps: Klaus's lawyer at a podium before a crowd of reporters. "
                "His expression: profound grief. Behind him, a banner drops reading 'IN MEMORIAM: BREATHING 4000 BC – 2024.' "
                "News chyrons scroll: 'RESPIRATORY COMMUNITY IN SHOCK' and 'LUNGS COULD NOT BE REACHED FOR COMMENT.'",
            "motion_effect": "pan_right",
            "search_keywords": ["lawyer press conference steps", "news reporters microphones"],
        },
        {
            "scene_number": 7,
            "narration_segment": "Helga has called it long overdue. Klaus, when reached for comment, said nothing. He was, at the time, breathing quietly.",
            "storyboard_description": "Split final panel: Helga sits serenely in a silent apartment, noise-canceling headphones removed, "
                "reading a book, a small content smile. Across town, Klaus sits alone, breathing very, very quietly, "
                "glancing nervously at an invisible judge. A clock ticks. His lungs continue, cautiously.",
            "motion_effect": "ken_burns_zoom_in",
            "search_keywords": ["woman relaxing peaceful apartment", "man sitting alone contemplating"],
        },
    ],
    "shorts_scenes": [
        {"scene_number": 1, "narration_segment": "A woman in Austria filed for divorce. The reason: loud breathing.", "storyboard_description": "Night scene: Helga awake, Klaus asleep with massive sound waves.", "duration_seconds": 9},
        {"scene_number": 2, "narration_segment": "The judge heard recordings. The judge agreed.", "storyboard_description": "Courtroom: recordings play, judge nods, gavel falls with explosion.", "duration_seconds": 9},
        {"scene_number": 3, "narration_segment": "Klaus's lawyer called it a dark day for breathing.", "storyboard_description": "Lawyer at press conference, IN MEMORIAM banner drops behind him.", "duration_seconds": 8},
        {"scene_number": 4, "narration_segment": "Klaus had no comment. He was breathing quietly.", "storyboard_description": "Klaus sitting alone, breathing very carefully, glancing at invisible judge.", "duration_seconds": 11},
    ],
}


# ── Runner ────────────────────────────────────────────────────────────────────

def run_story(story: dict, label: str):
    init_db()
    run_id = f"v2test_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"=== Breaking Weird v2 | {label} | run={run_id} ===")

    print(f"\n{'='*60}")
    print(f"STORY: {story['title']}")
    print(f"{'='*60}")

    print("\n[1/6] Generating 7 anime storyboard images...")
    generate_all_images(story, run_id)
    print(f"  Images: {len(story.get('image_paths', []))} panels")

    print("\n[2/6] Generating main voiceover + captions...")
    audio_path, _, caption_chunks = prepare_voiceover(story["narration"], run_id)
    story["audio_path"]     = audio_path
    story["caption_chunks"] = caption_chunks
    print(f"  Audio: {audio_path}")
    print(f"  Caption chunks: {len(caption_chunks)}")

    print("\n[3/6] Generating Shorts voiceover...")
    s_audio, _, s_chunks = prepare_voiceover(story["shorts_narration"], run_id, suffix="_shorts")
    story["shorts_audio_path"]     = s_audio
    story["shorts_caption_chunks"] = s_chunks

    print("\n[4/6] Getting background music...")
    music_path = get_music_track()
    print(f"  Music: {music_path}")

    print("\n[5/6] Composing main video + Shorts...")
    compose_main_video(story, audio_path, music_path, run_id)
    compose_shorts(story, s_audio, music_path, run_id)
    print(f"  Main:   {story.get('video_path')}")
    print(f"  Shorts: {story.get('shorts_path')}")

    print("\n[6/6] Generating & scoring 4 thumbnail variants...")
    best_thumb, all_thumbs = generate_thumbnails(story, run_id)
    for t in all_thumbs:
        marker = " <- SELECTED" if t.get("selected") else ""
        print(f"  Thumbnail v{t['variant']}: score={t.get('total_score', 0):.1f}{marker}")

    print(f"\n{'='*60}")
    print(f"Done: {label}")
    print(f"Main video:  {story.get('video_path')}")
    print(f"Shorts:      {story.get('shorts_path')}")
    print(f"Thumbnail:   {best_thumb}")
    print(f"{'='*60}\n")

    import subprocess
    for path in [story.get("video_path"), story.get("shorts_path"), best_thumb]:
        if path and os.path.exists(path):
            subprocess.Popen(["open", path])

    return story


if __name__ == "__main__":
    which = None
    if "--story" in sys.argv:
        idx   = sys.argv.index("--story")
        which = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

    if which == "1":
        run_story(STORY_FIRED_FOUNDER,    "founder_rejected")
    elif which == "2":
        run_story(STORY_BREATHING_DIVORCE, "breathing_divorce")
    else:
        run_story(STORY_FIRED_FOUNDER,    "founder_rejected")
        run_story(STORY_BREATHING_DIVORCE, "breathing_divorce")
