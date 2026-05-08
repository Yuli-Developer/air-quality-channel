"""
Central configuration for Breaking Weird v2.
All settings driven by environment variables with sane defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── AI ─────────────────────────────────────────────────────────────────────
GEMINI_API_KEY        = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL          = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Sources ────────────────────────────────────────────────────────────────
REDDIT_CLIENT_ID      = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET  = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT     = os.getenv("REDDIT_USER_AGENT", "BreakingWeirdV2/2.0")
NEWSAPI_KEY           = os.getenv("NEWSAPI_KEY", "")
PEXELS_API_KEY        = os.getenv("PEXELS_API_KEY", "")

# ── YouTube ────────────────────────────────────────────────────────────────
YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")
YOUTUBE_TOKEN_PATH     = os.getenv("YOUTUBE_TOKEN_PATH", "token.pickle")
YOUTUBE_CHANNEL_ID     = os.getenv("YOUTUBE_CHANNEL_ID", "")

# ── Publishing ─────────────────────────────────────────────────────────────
TIKTOK_SESSION_ID     = os.getenv("TIKTOK_SESSION_ID", "")
INSTAGRAM_USERNAME    = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD    = os.getenv("INSTAGRAM_PASSWORD", "")

# ── Redis ──────────────────────────────────────────────────────────────────
REDIS_URL             = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USE_REDIS             = os.getenv("USE_REDIS", "false").lower() == "true"

# ── Image Generation ───────────────────────────────────────────────────────
COMFYUI_URL           = os.getenv("COMFYUI_URL", "http://localhost:8188")
USE_COMFYUI           = os.getenv("USE_COMFYUI", "false").lower() == "true"
IMAGE_TIER            = os.getenv("IMAGE_TIER", "pollinations")   # comfyui | pollinations

# ── Pipeline ───────────────────────────────────────────────────────────────
STORIES_PER_RUN       = int(os.getenv("STORIES_PER_RUN", "1"))
TOP_STORIES_POOL      = int(os.getenv("TOP_STORIES_POOL", "30"))
MIN_VIRAL_SCORE       = float(os.getenv("MIN_VIRAL_SCORE", "6.0"))
SCENES_PER_VIDEO      = int(os.getenv("SCENES_PER_VIDEO", "7"))

# ── Video ──────────────────────────────────────────────────────────────────
VIDEO_WIDTH           = 1920
VIDEO_HEIGHT          = 1080
SHORTS_WIDTH          = 1080
SHORTS_HEIGHT         = 1920
FPS                   = 24
VIDEO_BITRATE         = "5000k"
AUDIO_BITRATE         = "192k"

# ── Paths ──────────────────────────────────────────────────────────────────
OUTPUT_DIR            = os.getenv("OUTPUT_DIR", "output")
IMAGES_DIR            = os.path.join(OUTPUT_DIR, "images")
AUDIO_DIR             = os.path.join(OUTPUT_DIR, "audio")
VIDEO_DIR             = os.path.join(OUTPUT_DIR, "videos")
SHORTS_DIR            = os.path.join(OUTPUT_DIR, "shorts")
THUMB_DIR             = os.path.join(OUTPUT_DIR, "thumbnails")
DB_PATH               = os.getenv("DB_PATH", "data/breaking_weird.db")

# ── Narrator styles ────────────────────────────────────────────────────────
NARRATOR_STYLES = ["deadpan", "horror_documentary", "sarcastic", "investigative", "hyper_tiktok"]
DEFAULT_STYLE   = os.getenv("NARRATOR_STYLE", "deadpan")

# ── Subreddits ─────────────────────────────────────────────────────────────
REDDIT_SUBREDDITS = [
    "nottheonion", "FloridaMan", "WeirdNews",
    "mildlyinfuriating", "tifu", "Whatcouldgowrong",
    "HumansBeingBros", "therewasanattempt",
]

# ── RSS feeds ──────────────────────────────────────────────────────────────
RSS_FEEDS = [
    "https://www.boredpanda.com/feed/",
    "https://feeds.reuters.com/reuters/oddlyEnoughNews",
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

# ── Viral score weights ────────────────────────────────────────────────────
VIRAL_WEIGHTS = {
    "curiosity": 0.20,
    "thumbnail_strength": 0.20,
    "ragebait": 0.10,
    "retention_potential": 0.20,
    "comment_potential": 0.10,
    "shareability": 0.10,
    "shorts_potential": 0.10,
}
