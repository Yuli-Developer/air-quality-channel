"""
Viral Prediction Engine — keyword-based scoring (no API calls).
Scores each story on 7 dimensions using weighted keyword matching,
computes weighted total, returns ranked list.
"""

import re
import logging
from config.settings import MIN_VIRAL_SCORE, TOP_STORIES_POOL, VIRAL_WEIGHTS

logger = logging.getLogger(__name__)

# ── Keyword banks per dimension ─────────────────────────────────────────────

CURIOSITY_KEYWORDS = [
    "why", "how", "secret", "nobody", "you won't believe", "nobody knew",
    "turns out", "accidentally", "forgot", "mystery", "unknown", "hidden",
    "surprising", "unexpected", "plot twist", "shocking", "revealed",
    "discovered", "found out", "woke up", "didn't know", "strange",
    "bizarre", "weird", "unusual", "against all odds", "somehow",
]

THUMBNAIL_KEYWORDS = [
    "million", "billion", "trillion", "%", "crashed", "surged", "record",
    "all-time", "biggest", "largest", "worst", "best", "first ever",
    "700%", "1000%", "zero", "bankrupt", "overnight", "one day",
    "shocked", "stunned", "jaw", "unbelievable", "insane", "wild",
]

RAGEBAIT_KEYWORDS = [
    "ceo", "executive", "billionaire", "wall street", "hedge fund",
    "bonus", "greed", "corruption", "fraud", "scam", "scandal",
    "fired", "sued", "arrested", "fine", "penalty", "bailout",
    "taxpayer", "unfair", "rigged", "manipulation", "insider",
    "while workers", "despite losses", "record profit",
]

RETENTION_KEYWORDS = [
    "but then", "twist", "plot twist", "however", "turned out",
    "accidentally", "mistake", "error", "actually", "in the end",
    "surprise", "nobody expected", "against all odds", "backfired",
    "irony", "ironic", "paradox", "despite", "even though",
]

COMMENT_KEYWORDS = [
    "should", "could", "would", "opinion", "debate", "controversial",
    "people are saying", "analysts say", "experts warn", "you think",
    "fair", "unfair", "right", "wrong", "crazy", "insane",
    "who is responsible", "blame", "fault", "lesson",
]

SHAREABILITY_KEYWORDS = [
    "potato", "duck", "alligator", "cat", "dog", "squirrel",
    "accidentally", "forgot", "glitch", "bug", "error", "wrong",
    "meme", "viral", "trending", "twitter", "reddit", "wtf",
    "you have to see this", "only in", "only possible",
    "meanwhile", "at the same time", "while everyone",
]

SHORTS_KEYWORDS = [
    "surged", "crashed", "soared", "plunged", "exploded", "collapsed",
    "%", "in one day", "overnight", "in a week", "in a month",
    "record", "all-time", "biggest", "fastest", "shortest",
    "accidental", "mistake", "error", "glitch", "wrong",
    "millionaire", "bankrupt", "fortune", "broke", "rich",
]

# Topics to reject (too dark/political for comedy)
REJECT_KEYWORDS = [
    "death", "died", "killed", "murder", "war casualties", "genocide",
    "tragedy", "disaster victims", "suicide", "cancer", "terrorism attack",
]


def _keyword_score(text: str, keywords: list, max_score: int = 10) -> float:
    """Count keyword hits in text, normalise to 0–10."""
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    # 1 hit = 4, 2 hits = 7, 3+ hits = 10
    return min(10.0, round(hits * 3.5, 1))


def _number_boost(text: str) -> float:
    """Boost score if large numbers or percentages are present."""
    has_pct  = bool(re.search(r'\d+%', text))
    has_big  = bool(re.search(r'\$?\d[\d,]*[mbMB]', text))   # $4M, 700B etc.
    has_huge = bool(re.search(r'[tbTB]rillion|[bB]illion', text))
    return (2.0 if has_pct else 0) + (1.5 if has_big else 0) + (2.0 if has_huge else 0)


def _score_one(story: dict) -> dict | None:
    title   = story.get("title", "")
    summary = story.get("summary", title)
    text    = f"{title} {summary}"

    # Reject dark/political topics
    text_lower = text.lower()
    for kw in REJECT_KEYWORDS:
        if kw in text_lower:
            logger.info(f"Rejected (dark topic): {title[:60]}")
            return None

    boost = _number_boost(text)

    scores = {
        "curiosity":          min(10, _keyword_score(text, CURIOSITY_KEYWORDS)   + boost * 0.3),
        "thumbnail_strength": min(10, _keyword_score(text, THUMBNAIL_KEYWORDS)   + boost * 0.5),
        "ragebait":           min(10, _keyword_score(text, RAGEBAIT_KEYWORDS)),
        "retention_potential":min(10, _keyword_score(text, RETENTION_KEYWORDS)   + boost * 0.2),
        "comment_potential":  min(10, _keyword_score(text, COMMENT_KEYWORDS)),
        "shareability":       min(10, _keyword_score(text, SHAREABILITY_KEYWORDS)+ boost * 0.3),
        "shorts_potential":   min(10, _keyword_score(text, SHORTS_KEYWORDS)      + boost * 0.4),
    }

    total = sum(scores[dim] * weight for dim, weight in VIRAL_WEIGHTS.items())
    total = round(total, 2)

    story["scores"]      = scores
    story["viral_score"] = total
    logger.debug(f"  {total:.1f}/10 — {title[:70]}")
    return story


def score_and_rank(stories: list[dict], top_n: int = 1) -> list[dict]:
    """Score all stories, filter by threshold, return top N. No API calls."""
    logger.info(f"Scoring {len(stories)} stories (keyword engine, no API)...")

    scored = []
    for story in stories[:TOP_STORIES_POOL]:
        result = _score_one(story)
        if result and result["viral_score"] >= MIN_VIRAL_SCORE:
            scored.append(result)

    ranked = sorted(scored, key=lambda x: x["viral_score"], reverse=True)
    logger.info(f"{len(ranked)} stories passed threshold. Top {top_n} selected.")
    for r in ranked[:5]:
        logger.info(f"  {r['viral_score']:.1f}/10 — {r['title'][:70]}")
    return ranked[:top_n]
