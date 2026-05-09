"""
Finance News Source — scrapes major financial news sites and forums.
Sources: MarketWatch, Yahoo Finance, CNBC, Bloomberg, Reuters, Forbes,
         Seeking Alpha, ZeroHedge, Motley Fool, Business Insider,
         Hacker News finance, Quartz, Fortune, Investopedia.

Filters all stories through FINANCE_WEIRD_KEYWORDS to surface only
weird / funny / strange / interesting finance stories.
"""

import asyncio
import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from config.settings import RSS_FEEDS, FINANCE_WEIRD_KEYWORDS

logger = logging.getLogger(__name__)

# Additional scraped sources beyond RSS (HTML scraping)
SCRAPED_SOURCES = [
    {
        "name": "MarketWatch Investing",
        "url":  "https://www.marketwatch.com/latest-news",
        "selector": "h3.article__headline a",
    },
    {
        "name": "Yahoo Finance",
        "url":  "https://finance.yahoo.com/topic/latest-news/",
        "selector": "h3 a",
    },
]

# Forum/discussion sites with finance content
FORUM_RSS = [
    # Hacker News — finance, money, stocks, investing discussions
    "https://hnrss.org/frontpage?q=stock+market",
    "https://hnrss.org/frontpage?q=investing+money",
    "https://hnrss.org/frontpage?q=crypto+bitcoin",
    "https://hnrss.org/frontpage?q=finance+bankruptcy",
    # Slashdot finance
    "https://rss.slashdot.org/Slashdot/slashdotBusiness",
]


def _is_finance_weird(title: str, summary: str = "") -> bool:
    """True if story is weird/funny/interesting finance content."""
    text = (title + " " + summary).lower()
    return any(kw.lower() in text for kw in FINANCE_WEIRD_KEYWORDS)


def _is_finance_topic(title: str, summary: str = "") -> bool:
    """True if story is related to finance/money/markets at all."""
    finance_terms = [
        "stock", "market", "invest", "money", "financ", "crypto", "bitcoin",
        "bank", "fund", "hedge", "wall street", "nasdaq", "s&p", "dow",
        "trading", "trader", "million", "billion", "debt", "loan", "tax",
        "economy", "economic", "recession", "inflation", "fed", "federal reserve",
        "interest rate", "bond", "etf", "ipo", "merger", "acquisition",
        "earnings", "revenue", "profit", "loss", "bankrupt", "wealth",
        "portfolio", "dividend", "options", "futures", "commodity",
        "gold", "silver", "oil", "currency", "forex", "startup", "venture",
    ]
    text = (title + " " + summary).lower()
    return any(term in text for term in finance_terms)


def _fetch_rss_finance(limit_per_feed: int) -> list[dict]:
    """Fetch all RSS feeds and filter for weird finance stories."""
    stories = []
    all_feeds = RSS_FEEDS + FORUM_RSS

    for feed_url in all_feeds:
        try:
            feed = feedparser.parse(feed_url)
            source_name = feed.feed.get("title", feed_url.split("/")[2])
            count = 0
            for entry in feed.entries[:limit_per_feed * 2]:
                title   = entry.get("title", "").strip()
                url     = entry.get("link", "").strip()
                summary = (
                    getattr(entry, "summary", "") or
                    getattr(entry, "description", "") or ""
                )[:600]

                if not title or not url:
                    continue

                # Must be finance-related AND weird/interesting
                if not _is_finance_topic(title, summary):
                    continue
                if not _is_finance_weird(title, summary):
                    continue

                stories.append({
                    "title":    title,
                    "url":      url,
                    "summary":  summary,
                    "source":   source_name,
                    "upvotes":  0,
                    "category": "finance",
                })
                count += 1
                if count >= limit_per_feed:
                    break

            if count:
                logger.info(f"{source_name}: {count} weird finance stories")
        except Exception as e:
            logger.warning(f"RSS {feed_url} failed: {e}")

    return stories


def _fetch_scraped_finance(limit: int = 10) -> list[dict]:
    """Scrape headline lists from major finance sites."""
    stories = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    for source in SCRAPED_SOURCES:
        try:
            r = requests.get(source["url"], headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.select(source["selector"])
            count = 0
            for link in links[:limit * 3]:
                title = link.get_text(strip=True)
                url   = link.get("href", "")
                if not title or not url or len(title) < 15:
                    continue
                if not url.startswith("http"):
                    base = "/".join(source["url"].split("/")[:3])
                    url  = base + url
                if not _is_finance_topic(title):
                    continue
                if not _is_finance_weird(title):
                    continue
                stories.append({
                    "title":    title,
                    "url":      url,
                    "summary":  title,
                    "source":   source["name"],
                    "upvotes":  0,
                    "category": "finance",
                })
                count += 1
                if count >= limit:
                    break
            if count:
                logger.info(f"{source['name']}: {count} weird finance headlines")
        except Exception as e:
            logger.warning(f"{source['name']} scrape failed: {e}")

    return stories


def _fetch_sync(limit_per_feed: int) -> list[dict]:
    rss     = _fetch_rss_finance(limit_per_feed)
    scraped = _fetch_scraped_finance(limit=10)
    all_stories = rss + scraped
    logger.info(f"Finance news total: {len(all_stories)} weird finance stories")
    return all_stories


async def fetch_finance_news_async(limit_per_feed: int = 10) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync, limit_per_feed)
