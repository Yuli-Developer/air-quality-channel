"""Reddit source — async wrapper around PRAW."""

import asyncio
import logging
import praw
from config.settings import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_SUBREDDITS

logger = logging.getLogger(__name__)


def _fetch_sync(limit_per_sub: int) -> list[dict]:
    if not REDDIT_CLIENT_ID:
        raise ValueError("REDDIT_CLIENT_ID not set")

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    stories = []
    for sub in REDDIT_SUBREDDITS:
        try:
            subreddit = reddit.subreddit(sub)
            for post in subreddit.hot(limit=limit_per_sub):
                if post.stickied or post.score < 100:
                    continue
                stories.append({
                    "title":   post.title,
                    "url":     f"https://reddit.com{post.permalink}",
                    "summary": post.selftext[:500] if post.selftext else post.title,
                    "source":  f"r/{sub}",
                    "upvotes": post.score,
                })
        except Exception as e:
            logger.warning(f"r/{sub} failed: {e}")

    return stories


async def fetch_reddit_async(limit_per_sub: int = 15) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync, limit_per_sub)
