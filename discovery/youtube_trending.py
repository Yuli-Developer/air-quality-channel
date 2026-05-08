"""YouTube Trending — scrapes trending video titles as story seeds."""

import asyncio
import logging
import requests

logger = logging.getLogger(__name__)

TRENDING_RSS = "https://www.youtube.com/feeds/videos.xml?chart=mostPopular&regionCode=US&hl=en"


def _fetch_sync() -> list[dict]:
    import feedparser
    stories = []
    try:
        feed = feedparser.parse(TRENDING_RSS)
        for entry in feed.entries[:20]:
            title = entry.get("title", "")
            if not title:
                continue
            stories.append({
                "title":   title,
                "url":     entry.get("link", ""),
                "summary": title,
                "source":  "YouTube Trending",
                "upvotes": 0,
            })
    except Exception as e:
        logger.warning(f"YouTube trending failed: {e}")
    return stories


async def fetch_youtube_trending_async() -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync)
