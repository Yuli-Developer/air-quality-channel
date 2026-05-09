"""
Narrative Generator — produces scripts in multiple styles with
hook/setup/twist/climax/payoff structure, long-form + Shorts versions.
"""

import json
import logging
from google import genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, SCENES_PER_VIDEO, DEFAULT_STYLE
from ai.prompt_templates import STYLE_SYSTEM_PROMPTS, SCRIPT_PROMPT, SHORTS_SCRIPT_PROMPT
from config.settings import SHORTS_ONLY, MAX_SHORTS_WORDS

logger = logging.getLogger(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

STYLE_WORD_COUNTS = {
    "deadpan":            "200-250",
    "horror_documentary": "220-270",
    "sarcastic":          "190-240",
    "investigative":      "250-300",
    "hyper_tiktok":       "150-200",
}


def _parse_response(resp) -> dict:
    raw = resp.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_script(story: dict, style: str = None) -> dict:
    """
    Generate script package. Uses Shorts-only prompt when SHORTS_ONLY=True.
    Returns enriched story dict.
    """
    style = style or DEFAULT_STYLE
    if style not in STYLE_SYSTEM_PROMPTS:
        style = "deadpan"

    logger.info(f"Generating {style} script for: {story['title'][:70]}")

    if SHORTS_ONLY:
        return _generate_shorts_script(story, style)
    return _generate_full_script(story, style)


def _generate_shorts_script(story: dict, style: str) -> dict:
    """Shorts-only: 4 scenes, max 130 words, vertical compositions."""
    prompt = SHORTS_SCRIPT_PROMPT.format(
        system_prompt=STYLE_SYSTEM_PROMPTS[style],
        title=story["title"],
        summary=story.get("summary", story["title"]),
        url=story.get("url", ""),
        style=style,
    )

    resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    data = _parse_response(resp)

    narration = data["narration"]
    word_count = len(narration.split())
    if word_count > MAX_SHORTS_WORDS:
        logger.warning(f"Narration {word_count} words — trimming to {MAX_SHORTS_WORDS}")
        narration = " ".join(narration.split()[:MAX_SHORTS_WORDS])

    story["youtube_title"]        = data["youtube_title"]
    story["hook"]                 = data["hook"]
    story["narration"]            = narration
    story["shorts_narration"]     = narration          # same audio for Shorts
    story["title_variants"]       = data.get("title_variants", [data["youtube_title"]])
    story["characters"]           = data.get("characters", "")
    story["scenes"]               = data["scenes"]     # 4 scenes, vertical descriptions
    story["shorts_scenes"]        = data["scenes"]     # same scenes for shorts compose
    story["tags"]                 = data.get("tags", [])
    story["description_hook"]     = data.get("description_hook", "")
    story["narrator_style"]       = style
    story["shorts_only"]          = True
    story["visual_style"]         = story.get("visual_style", "news_broadcast")

    logger.info(
        f"Shorts script ready [{style}]: 4 scenes | {len(narration.split())} words"
    )
    return story


def _generate_full_script(story: dict, style: str) -> dict:
    """Full pipeline: main video + shorts."""
    prompt = SCRIPT_PROMPT.format(
        system_prompt=STYLE_SYSTEM_PROMPTS[style],
        title=story["title"],
        summary=story.get("summary", story["title"]),
        url=story.get("url", ""),
        style=style,
        word_count=STYLE_WORD_COUNTS[style],
        num_scenes=SCENES_PER_VIDEO,
    )

    resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    data = _parse_response(resp)

    story["youtube_title"]    = data["youtube_title"]
    story["hook"]             = data["hook"]
    story["narration"]        = data["narration"]
    story["shorts_narration"] = data.get("shorts_narration", "")
    story["title_variants"]   = data.get("title_variants", [story["youtube_title"]])
    story["hook_variants"]    = data.get("hook_variants", [story["hook"]])
    story["characters"]       = data.get("characters", "")
    story["scenes"]           = data["scenes"]
    story["shorts_scenes"]    = data.get("shorts_scenes", [])
    story["tags"]             = data.get("tags", [])
    story["description_hook"] = data.get("description_hook", "")
    story["narrator_style"]   = style

    logger.info(
        f"Script ready [{style}]: {len(story['scenes'])} scenes | "
        f"{len(story['narration'].split())} words"
    )
    return story
