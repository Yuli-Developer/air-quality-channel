"""
YouTube Publisher — Air Quality Channel.
Uploads daily AQI Shorts to YouTube.
"""

import os
import re
import pickle
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import YOUTUBE_CLIENT_SECRETS, YOUTUBE_TOKEN_PATH

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]

AQI_TAGS_BASE = [
    "air quality", "aqi", "air pollution", "pollution today",
    "air quality today", "daily aqi", "smog", "clean air",
    "air quality index", "pollution report", "air quality report",
    "most polluted city", "aqi shorts", "environment",
]


def _trim_tags(tags: list) -> list:
    result, total = [], 0
    for t in tags:
        t = re.sub(r"[^\w\s\-\.]", "", t.replace("#", "")).strip()
        if not t or len(t) > 30:
            continue
        if total + len(t) + 1 <= 498:
            result.append(t)
            total += len(t) + 1
    return result


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
    media   = MediaFileUpload(video_path, mimetype="video/mp4",
                               resumable=True, chunksize=10 * 1024 * 1024)
    request = youtube.videos().insert(
        part=",".join(body.keys()), body=body, media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"Upload: {int(status.progress() * 100)}%")
    return response["id"]


def _build_description(story: dict) -> str:
    worst  = story.get("worst_city", {})
    cities = story.get("cities", [])
    top5   = cities[:5] if cities else []

    lines = [story.get("hook", ""), ""]
    if top5:
        lines.append("TODAY'S TOP 5 MOST POLLUTED CITIES:")
        for i, c in enumerate(top5, 1):
            lines.append(f"{i}. {c['city']} — AQI {c['aqi']} ({c['category']})")
    lines += [
        "",
        "Data: Google Air Quality API / Open-Meteo",
        "---",
        "AQI Daily — real-time air quality data for cities worldwide.",
        "Follow @AQIDaily for daily updates. Stay safe.",
        "",
        "#AQIDaily #AirQuality #AQI #Pollution #AirQualityIndex "
        "#AirPollution #CleanAir #Environment #AQIReport #Shorts",
    ]
    return "\n".join(lines)


def publish_shorts(story: dict, run_id: str) -> str | None:
    shorts_path = story.get("shorts_path")
    if not shorts_path or not os.path.exists(shorts_path):
        logger.warning("No Shorts file found — skipping upload")
        return None

    youtube = _get_service()
    title   = f"{story.get('youtube_title', story['title'])[:90]} #Shorts"
    tags    = _trim_tags(story.get("tags", []) + AQI_TAGS_BASE)

    body = {
        "snippet": {
            "title":           title,
            "description":     _build_description(story),
            "tags":            tags,
            "categoryId":      "28",   # Science & Technology
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":           "public",
            "madeForKids":             False,
            "selfDeclaredMadeForKids": False,
        },
    }

    logger.info(f"Uploading AQI Shorts: {title}")
    video_id = _upload_video(youtube, shorts_path, body)
    logger.info(f"Uploaded: https://www.youtube.com/shorts/{video_id}")

    story["shorts_video_id"]  = video_id
    story["shorts_video_url"] = f"https://www.youtube.com/shorts/{video_id}"

    thumb = story.get("thumbnail_path")
    if thumb and os.path.exists(thumb):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumb, mimetype="image/jpeg"),
            ).execute()
            logger.info(f"Thumbnail set for {video_id}")
        except Exception as e:
            logger.error(f"Thumbnail upload failed: {e}")

    return video_id
