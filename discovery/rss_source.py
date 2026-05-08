"""RSS source — async feedparser."""

import asyncio
import logging
import feedparser
from config.settings import RSS_FEEDS

logger = logging.getLogger(__name__)


def _fetch_sync(limit_per_feed: int) -> list[dict]:
    stories = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:limit_per_feed]:
                summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
                stories.append({
                    "title":   entry.get("title", ""),
                    "url":     entry.get("link", ""),
                    "summary": summary[:500],
                    "source":  feed.feed.get("title", feed_url),
                    "upvotes": 0,
                })
        except Exception as e:
            logger.warning(f"RSS {feed_url} failed: {e}")
    return stories


async def fetch_rss_async(limit_per_feed: int = 15) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync, limit_per_feed)
