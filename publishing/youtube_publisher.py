"""
YouTube Publisher — uploads main video and Shorts using Data API v3.
Handles OAuth2, resumable uploads, thumbnail setting, playlist management.
"""

import os
import pickle
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import YOUTUBE_CLIENT_SECRETS, YOUTUBE_TOKEN_PATH

logger = logging.getLogger(__name__)

# ── Tags ────────────────────────────────────────────────────────────────────

def _trim_tags(tags: list) -> list:
    """YouTube enforces 500 total characters across all tags."""
    result, total = [], 0
    for t in tags:
        t = t.replace('#', '').strip()
        if t and total + len(t) + 1 <= 498:
            result.append(t)
            total += len(t) + 1
    return result


FINANCE_TAGS = [
    # Channel
    "the odd investor", "theoddinvestor", "odd investor",
    # Finance general
    "finance", "investing", "stock market", "stocks", "money",
    "personal finance", "financial news", "market news",
    "wall street", "trading", "investor", "wealth",
    # Weird finance niche
    "weird finance", "bizarre market", "funny finance",
    "strange investing", "wtf finance", "market madness",
    "financial fails", "accidental millionaire",
    # Viral finance
    "meme stocks", "get rich", "financial freedom",
    "money mistakes", "market crash", "stock crash",
    "crypto news", "bitcoin news", "finance explained",
]

SHORTS_TAGS = [
    "shorts", "youtubeshorts", "shortsvideo",
    "financeshorts", "moneytips", "investingshorts",
    "stockmarketshorts", "financefacts", "moneyshorts",
]

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def _get_service():
    creds = None
    if os.path.exists(YOUTUBE_TOKEN_PATH):
        with open(YOUTUBE_TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRETS, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(YOUTUBE_TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def _upload_video(youtube, video_path: str, body: dict) -> str:
    media = MediaFileUpload(
        video_path, mimetype="video/mp4",
        resumable=True, chunksize=10 * 1024 * 1024,
    )
    request = youtube.videos().insert(
        part=",".join(body.keys()), body=body, media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"Upload: {int(status.progress() * 100)}%")
    return response["id"]


def _set_thumbnail(youtube, video_id: str, thumb_path: str):
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg"),
        ).execute()
        logger.info(f"Thumbnail set for {video_id}")
    except Exception as e:
        logger.error(f"Thumbnail upload failed: {e}")


def publish_main(story: dict, run_id: str) -> str | None:
    """Upload main video. Returns YouTube video ID."""
    video_path = story.get("video_path")
    if not video_path or not os.path.exists(video_path):
        logger.error("No video file found to upload")
        return None

    youtube = _get_service()
    title   = story.get("youtube_title", story["title"])[:100]
    tags    = _trim_tags(story.get("tags", []) + FINANCE_TAGS)

    description = _build_description(story)

    body = {
        "snippet": {
            "title":           title,
            "description":     description,
            "tags":            tags,
            "categoryId":      "25",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":              "public",
            "madeForKids":                False,
            "selfDeclaredMadeForKids":    False,
        },
    }

    logger.info(f"Uploading main video: {title}")
    video_id = _upload_video(youtube, video_path, body)
    logger.info(f"Uploaded: https://www.youtube.com/watch?v={video_id}")

    thumb = story.get("thumbnail_path")
    if thumb and os.path.exists(thumb):
        _set_thumbnail(youtube, video_id, thumb)

    story["youtube_video_id"]  = video_id
    story["youtube_video_url"] = f"https://www.youtube.com/watch?v={video_id}"
    return video_id


def publish_shorts(story: dict, run_id: str) -> str | None:
    """Upload Shorts version. Returns YouTube video ID."""
    shorts_path = story.get("shorts_path")
    if not shorts_path or not os.path.exists(shorts_path):
        logger.warning("No Shorts file found — skipping Shorts upload")
        return None

    youtube = _get_service()
    title   = f"{story.get('youtube_title', story['title'])[:90]} #Shorts"
    tags    = _trim_tags(story.get("tags", []) + FINANCE_TAGS + SHORTS_TAGS)

    body = {
        "snippet": {
            "title":           title,
            "description":     _build_description(story, is_shorts=True),
            "tags":            tags,
            "categoryId":      "25",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":           "public",
            "madeForKids":             False,
            "selfDeclaredMadeForKids": False,
        },
    }

    logger.info(f"Uploading Shorts: {title}")
    video_id = _upload_video(youtube, shorts_path, body)
    logger.info(f"Shorts uploaded: https://www.youtube.com/shorts/{video_id}")

    story["shorts_video_id"]  = video_id
    story["shorts_video_url"] = f"https://www.youtube.com/shorts/{video_id}"
    return video_id


def _build_description(story: dict, is_shorts: bool = False) -> str:
    hook        = story.get("description_hook", story.get("hook", ""))
    narration   = story.get("narration", "")
    excerpt     = narration[:200].rstrip() + "..." if narration and not is_shorts else hook
    source_url  = story.get("url", "")
    source_name = story.get("source", "the internet")

    return f"""{excerpt}

{"Original story" if not is_shorts else "Source"}: {source_name}
{source_url}

---
The Odd Investor — weird finance stories that actually happened.
New video every day. Subscribe so you never miss a story.

#TheOddInvestor #WeirdFinance #StockMarket #Investing #Finance #MoneyNews #WallStreet #FinanceFacts #WTFFinance #StrangeButTrue #FinancialNews #Stocks #MoneyTips #InvestingTips #FinanceShorts
"""
