"""
Finance Discovery Engine — scrapes only weird/funny/strange/interesting
financial news from Reddit finance communities, major financial news sites,
and financial discussion forums.

Sources:
  - Reddit: r/wallstreetbets, r/personalfinance, r/investing, r/stocks,
            r/CryptoCurrency, r/Superstonk, r/financialindependence, etc.
  - RSS:    Reuters Business, MarketWatch, CNBC, Yahoo Finance, Bloomberg,
            Forbes, Fortune, Seeking Alpha, ZeroHedge, Motley Fool,
            Business Insider, Hacker News finance, Quartz
  - Scraped: MarketWatch, Yahoo Finance headline lists

All stories must pass FINANCE_WEIRD_KEYWORDS filter before entering the pool.
"""

import asyncio
import logging
from datetime import datetime
from storage.database import is_duplicate

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
    """
    Run all finance scrapers in parallel.
    Returns a deduplicated pool of weird/interesting finance stories.
    """
    from discovery.reddit_source       import fetch_reddit_async
    from discovery.finance_news_source import fetch_finance_news_async

    results = await asyncio.gather(
        _safe(fetch_reddit_async(limit_per_source),       "Reddit Finance"),
        _safe(fetch_finance_news_async(limit_per_source), "Finance News Sites"),
    )

    raw = []
    for batch in results:
        raw.extend(batch)

    # Deduplicate within batch and against DB
    seen_urls = set()
    stories   = []
    for s in raw:
        url = s.get("url", "")
        if not url or url in seen_urls:
            continue
        if is_duplicate(url):
            continue
        seen_urls.add(url)
        stories.append(_normalize(s))

    # Sort by upvotes (Reddit signal) descending
    stories.sort(key=lambda x: x.get("upvotes", 0), reverse=True)

    logger.info(f"Finance discovery complete: {len(stories)} unique weird finance stories")
    return stories


def _normalize(s: dict) -> dict:
    """Ensure all stories have a consistent schema."""
    return {
        "title":      s.get("title", "").strip(),
        "url":        s.get("url", "").strip(),
        "summary":    s.get("summary", s.get("title", "")).strip(),
        "source":     s.get("source", "unknown"),
        "upvotes":    s.get("upvotes", 0),
        "category":   s.get("category", "finance"),
        "fetched_at": datetime.utcnow().isoformat(),
    }


def run_discovery(limit_per_source: int = 15) -> list[dict]:
    """Sync wrapper for the async discovery engine."""
    return asyncio.run(discover_stories(limit_per_source))
