"""
Reddit source — finance subreddits only.
Filters posts by weird/funny/interesting finance keywords.
"""

import asyncio
import logging
import praw
from config.settings import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    REDDIT_SUBREDDITS, FINANCE_WEIRD_KEYWORDS,
)

logger = logging.getLogger(__name__)

# Minimum scores per subreddit — higher bars for high-volume subs
_MIN_SCORES = {
    "wallstreetbets": 500,
    "Superstonk":     300,
    "CryptoCurrency": 300,
    "personalfinance": 200,
    "investing":      200,
    "stocks":         150,
    "StockMarket":    100,
}
_DEFAULT_MIN_SCORE = 100


def _is_finance_weird(title: str, body: str) -> bool:
    """Return True if the post contains at least one weird/interesting finance keyword."""
    text = (title + " " + body).lower()
    return any(kw.lower() in text for kw in FINANCE_WEIRD_KEYWORDS)


def _fetch_sync(limit_per_sub: int) -> list[dict]:
    if not REDDIT_CLIENT_ID:
        raise ValueError("REDDIT_CLIENT_ID not set")

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    stories = []
    seen = set()
    for sub in REDDIT_SUBREDDITS:
        try:
            min_score = _MIN_SCORES.get(sub, _DEFAULT_MIN_SCORE)
            subreddit = reddit.subreddit(sub)
            for post in subreddit.hot(limit=limit_per_sub * 2):  # fetch more, filter down
                if post.stickied or post.score < min_score:
                    continue
                if post.id in seen:
                    continue
                body = post.selftext[:500] if post.selftext else ""
                if not _is_finance_weird(post.title, body):
                    continue
                seen.add(post.id)
                stories.append({
                    "title":   post.title,
                    "url":     f"https://reddit.com{post.permalink}",
                    "summary": body or post.title,
                    "source":  f"r/{sub}",
                    "upvotes": post.score,
                    "category": "finance",
                })
            logger.info(f"r/{sub}: found {sum(1 for s in stories if s['source'] == f'r/{sub}')} weird finance posts")
        except Exception as e:
            logger.warning(f"r/{sub} failed: {e}")

    return stories


async def fetch_reddit_async(limit_per_sub: int = 15) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync, limit_per_sub)
