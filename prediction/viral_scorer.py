"""
Viral Prediction Engine.
Scores each story on 7 dimensions using Gemini,
computes weighted total, returns ranked list.
"""

import json
import logging
from google import genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, MIN_VIRAL_SCORE, TOP_STORIES_POOL, VIRAL_WEIGHTS

logger = logging.getLogger(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

SCORE_PROMPT = """You are a viral content strategist for "Breaking Weird" — a deadpan comedy news YouTube channel.

Score this news story across 7 dimensions, each from 0-10:

Title: {title}
Summary: {summary}
Source: {source}

Scoring dimensions:
- curiosity: Does the title make you NEED to know more?
- thumbnail_strength: Can this be turned into a jaw-dropping thumbnail?
- ragebait: Does this make people angry/outraged enough to comment?
- retention_potential: Will people watch to the end? Is there a twist/payoff?
- comment_potential: Will people debate, react, or share their own story?
- shareability: Will people send this to friends saying "wtf"?
- shorts_potential: Can this become a 30-60s viral Short?

Also provide:
- should_produce: true/false (false if topic is too dark, political, or not suitable for comedy)
- rejection_reason: only if should_produce is false

Return ONLY valid JSON:
{{
  "curiosity": 0-10,
  "thumbnail_strength": 0-10,
  "ragebait": 0-10,
  "retention_potential": 0-10,
  "comment_potential": 0-10,
  "shareability": 0-10,
  "shorts_potential": 0-10,
  "should_produce": true,
  "rejection_reason": ""
}}"""


def _score_one(story: dict) -> dict | None:
    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=SCORE_PROMPT.format(
                title=story["title"][:200],
                summary=story.get("summary", story["title"])[:500],
                source=story.get("source", "unknown"),
            ),
        )
        raw = resp.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())

        if not data.get("should_produce", True):
            logger.info(f"Rejected: {story['title'][:60]} — {data.get('rejection_reason', '')}")
            return None

        # Weighted total
        total = sum(
            data.get(dim, 0) * weight
            for dim, weight in VIRAL_WEIGHTS.items()
        )
        story["scores"]      = data
        story["viral_score"] = round(total, 2)
        return story

    except Exception as e:
        logger.warning(f"Scoring failed for '{story['title'][:50]}': {e}")
        return None


def score_and_rank(stories: list[dict], top_n: int = 1) -> list[dict]:
    """Score all stories, filter by threshold, return top N."""
    logger.info(f"Scoring {len(stories)} stories with Gemini...")

    scored = []
    for story in stories[:TOP_STORIES_POOL]:
        result = _score_one(story)
        if result and result["viral_score"] >= MIN_VIRAL_SCORE:
            scored.append(result)
            logger.info(f"  {result['viral_score']:.1f}/10 — {result['title'][:70]}")

    ranked = sorted(scored, key=lambda x: x["viral_score"], reverse=True)
    logger.info(f"{len(ranked)} stories passed threshold. Top {top_n} selected.")
    return ranked[:top_n]
