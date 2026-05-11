"""
Air Quality Channel — configuration.
All settings driven by environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── AI ──────────────────────────────────────────────────────────────────────
GEMINI_API_KEY        = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL          = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Air Quality APIs ───────────────────────────────────────────────────
GOOGLE_AQI_API_KEY    = os.getenv("GOOGLE_AQI_API_KEY", "")      # same Google project key
WAQI_TOKEN            = os.getenv("WAQI_TOKEN", "")              # free: https://aqicn.org/api/
AQI_API_URL           = "https://airquality.googleapis.com/v1/currentConditions:lookup"

# ── YouTube ──────────────────────────────────────────────────────────────────
YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")
YOUTUBE_TOKEN_PATH     = os.getenv("YOUTUBE_TOKEN_PATH", "token.pickle")
YOUTUBE_CHANNEL_ID     = os.getenv("YOUTUBE_CHANNEL_ID", "")

# ── Image Generation ─────────────────────────────────────────────────────────
COMFYUI_URL           = os.getenv("COMFYUI_URL", "http://localhost:8188")
USE_COMFYUI           = os.getenv("USE_COMFYUI", "false").lower() == "true"
IMAGE_TIER            = os.getenv("IMAGE_TIER", "pollinations")

# ── Pipeline ─────────────────────────────────────────────────────────────────
SHORTS_ONLY           = True
SCENES_PER_VIDEO      = 5          # one scene per featured city
MAX_SHORTS_WORDS      = 140        # ~58s at moderate pace

# ── Video ────────────────────────────────────────────────────────────────────
SHORTS_WIDTH          = 1080
SHORTS_HEIGHT         = 1920
FPS                   = 24

# ── Video encoding
VIDEO_BITRATE         = "5000k"
AUDIO_BITRATE         = "192k"

# ── Paths ────────────────────────────────────────────────────────────────────
OUTPUT_DIR            = os.getenv("OUTPUT_DIR", "output")
IMAGES_DIR            = os.path.join(OUTPUT_DIR, "images")
AUDIO_DIR             = os.path.join(OUTPUT_DIR, "audio")
VIDEO_DIR             = os.path.join(OUTPUT_DIR, "videos")
SHORTS_DIR            = os.path.join(OUTPUT_DIR, "shorts")
THUMB_DIR             = os.path.join(OUTPUT_DIR, "thumbnails")
DB_PATH               = os.getenv("DB_PATH", "data/airquality.db")

# ── Cities to monitor ────────────────────────────────────────────────────────
# (lat, lon, display_name, country_code)
MONITORED_CITIES = [
    (28.6139,  77.2090, "Delhi",      "IN"),
    (39.9042, 116.4074, "Beijing",    "CN"),
    (19.0760,  72.8777, "Mumbai",     "IN"),
    (31.5204,  74.3587, "Lahore",     "PK"),
    (23.8103,  90.4125, "Dhaka",      "BD"),
    (24.8607,  67.0011, "Karachi",    "PK"),
    (40.7128, -74.0060, "New York",   "US"),
    (34.0522,-118.2437, "Los Angeles","US"),
    (51.5074,  -0.1278, "London",     "GB"),
    (48.8566,   2.3522, "Paris",      "FR"),
    (35.6762, 139.6503, "Tokyo",      "JP"),
    (37.5665, 126.9780, "Seoul",      "KR"),
    (55.7558,  37.6173, "Moscow",     "RU"),
    (-23.5505, -46.6333,"São Paulo",  "BR"),
    (30.0444,  31.2357, "Cairo",      "EG"),
    (1.3521,  103.8198, "Singapore",  "SG"),
    (25.2048,  55.2708, "Dubai",      "AE"),
    (13.7563, 100.5018, "Bangkok",    "TH"),
    (3.1390,  101.6869, "Kuala Lumpur","MY"),
    (-33.8688, 151.2093,"Sydney",     "AU"),
]

# ── AQI Categories ───────────────────────────────────────────────────────────
AQI_CATEGORIES = [
    (0,   50,  "Good",             "#00E400", "Air quality is satisfactory."),
    (51,  100, "Moderate",         "#FFFF00", "Acceptable, but some pollutants may concern sensitive people."),
    (101, 150, "Unhealthy for Some","#FF7E00","Sensitive groups may experience health effects."),
    (151, 200, "Unhealthy",        "#FF0000", "Everyone may experience health effects."),
    (201, 300, "Very Unhealthy",   "#8F3F97", "Health alert: serious effects for everyone."),
    (301, 500, "Hazardous",        "#7E0023", "Emergency conditions. Avoid all outdoor activity."),
]
