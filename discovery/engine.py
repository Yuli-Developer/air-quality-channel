"""
Trend Discovery Engine — parallel async scraping from all sources.
Deduplicates, normalizes, and returns a ranked story pool.
"""

import asyncio
import logging
from datetime import datetime
from storage.database import is_duplicate, save_story

logger = logging.getLogger(__name__)


async def _safe(coro, label: str) -> list:
    try:
        result = await coro
        logger.info(f"{label}: {len(result)} stories")
        return result
    except Exception as e:
        logger.warning(f"{label} failed: {e}")
        return []


async def discover_stories(limit_per_source: int = 15) -> list[dict]:
    """Run all scrapers in parallel and return deduplicated story pool."""

    from discovery.reddit_source    import fetch_reddit_async
    from discovery.rss_source       import fetch_rss_async
    from discovery.youtube_trending import fetch_youtube_trending_async
    from discovery.google_trends    import fetch_google_trends_async

    results = await asyncio.gather(
        _safe(fetch_reddit_async(limit_per_source),    "Reddit"),
        _safe(fetch_rss_async(limit_per_source),       "RSS"),
        _safe(fetch_youtube_trending_async(),           "YouTube Trending"),
        _safe(fetch_google_trends_async(),              "Google Trends"),
    )

    raw = []
    for batch in results:
        raw.extend(batch)

    # Deduplicate by URL hash against DB and within this batch
    seen_urls = set()
    stories = []
    for s in raw:
        url = s.get("url", "")
        if not url or url in seen_urls:
            continue
        if is_duplicate(url):
            continue
        seen_urls.add(url)
        stories.append(_normalize(s))

    logger.info(f"Discovery complete: {len(stories)} unique new stories")
    return stories


def _normalize(s: dict) -> dict:
    """Ensure all stories have a consistent schema."""
    return {
        "title":     s.get("title", "").strip(),
        "url":       s.get("url", "").strip(),
        "summary":   s.get("summary", s.get("title", "")).strip(),
        "source":    s.get("source", "unknown"),
        "upvotes":   s.get("upvotes", 0),
        "fetched_at": datetime.utcnow().isoformat(),
    }


def run_discovery(limit_per_source: int = 15) -> list[dict]:
    """Sync wrapper for the async discovery engine."""
    return asyncio.run(discover_stories(limit_per_source))
