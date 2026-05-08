"""Google Trends — fetches rising search trends as story seeds."""

import asyncio
import logging

logger = logging.getLogger(__name__)

WEIRD_KEYWORDS = ["bizarre", "strange", "weird", "florida man", "accidentally", "unexpected"]


def _fetch_sync() -> list[dict]:
    stories = []
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360)
        # Daily search trends
        trending = pt.trending_searches(pn="united_states")
        for term in trending[0].tolist()[:20]:
            stories.append({
                "title":   term,
                "url":     f"https://trends.google.com/trends/explore?q={term.replace(' ', '+')}",
                "summary": f"Trending search: {term}",
                "source":  "Google Trends",
                "upvotes": 500,
            })
    except ImportError:
        logger.debug("pytrends not installed, skipping Google Trends")
    except Exception as e:
        logger.warning(f"Google Trends failed: {e}")
    return stories


async def fetch_google_trends_async() -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync)
