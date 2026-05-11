"""
Air Quality Discovery — fetches live AQI data from Google Air Quality API
for all monitored cities and ranks them worst-to-best.
Falls back to Open-Meteo Air Quality API (completely free, no key needed).
"""

import logging
import requests
from datetime import datetime, timezone
from config.settings import (
    GOOGLE_AQI_API_KEY, AQI_API_URL, MONITORED_CITIES, AQI_CATEGORIES
)

logger = logging.getLogger(__name__)


def _aqi_category(aqi: int) -> dict:
    for lo, hi, label, color, advice in AQI_CATEGORIES:
        if lo <= aqi <= hi:
            return {"label": label, "color": color, "advice": advice}
    return {"label": "Hazardous", "color": "#7E0023", "advice": "Avoid all outdoor activity."}


def _fetch_google_aqi(lat: float, lon: float) -> int | None:
    """Call Google Air Quality API for one location. Returns US AQI or None."""
    if not GOOGLE_AQI_API_KEY:
        return None
    try:
        payload = {
            "location": {"latitude": lat, "longitude": lon},
            "universalAqi": True,
        }
        r = requests.post(
            f"{AQI_API_URL}?key={GOOGLE_AQI_API_KEY}",
            json=payload, timeout=10
        )
        if r.status_code != 200:
            return None
        data = r.json()
        indexes = data.get("indexes", [])
        for idx in indexes:
            if idx.get("code") == "uaqi":
                return idx.get("aqiDisplay") or idx.get("aqi")
        return None
    except Exception as e:
        logger.debug(f"Google AQI API error ({lat},{lon}): {e}")
        return None


def _fetch_openmeteo_aqi(lat: float, lon: float) -> int | None:
    """
    Free fallback: Open-Meteo Air Quality API.
    Returns US AQI equivalent derived from PM2.5 hourly.
    """
    try:
        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=us_aqi&forecast_days=1&timezone=auto"
        )
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data   = r.json()
        values = data.get("hourly", {}).get("us_aqi", [])
        # Take the most recent non-null value
        for v in reversed(values):
            if v is not None:
                return int(v)
        return None
    except Exception as e:
        logger.debug(f"Open-Meteo AQI error ({lat},{lon}): {e}")
        return None


def fetch_city_aqi(lat: float, lon: float) -> int | None:
    """Try Google first, fall back to Open-Meteo."""
    aqi = _fetch_google_aqi(lat, lon)
    if aqi is None:
        aqi = _fetch_openmeteo_aqi(lat, lon)
    return aqi


def fetch_all_cities() -> list[dict]:
    """
    Fetch AQI for all monitored cities.
    Returns list sorted worst → best.
    """
    results = []
    for lat, lon, city, country in MONITORED_CITIES:
        aqi = fetch_city_aqi(lat, lon)
        if aqi is None:
            logger.warning(f"Could not fetch AQI for {city}")
            continue
        cat = _aqi_category(aqi)
        results.append({
            "city":     city,
            "country":  country,
            "lat":      lat,
            "lon":      lon,
            "aqi":      aqi,
            "category": cat["label"],
            "color":    cat["color"],
            "advice":   cat["advice"],
            "date":     datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })
        logger.info(f"{city}: AQI {aqi} ({cat['label']})")

    results.sort(key=lambda x: x["aqi"], reverse=True)
    logger.info(f"Fetched AQI for {len(results)}/{len(MONITORED_CITIES)} cities")
    return results


def build_daily_report(cities: list[dict]) -> dict:
    """
    Build a daily report dict from city AQI data.
    This is the 'story' object passed through the pipeline.
    """
    if not cities:
        return {}

    worst      = cities[0]
    top5       = cities[:5]
    best       = cities[-1] if len(cities) > 1 else None
    date_str   = datetime.now(timezone.utc).strftime("%B %d, %Y")
    today_str  = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Build title
    title = f"Most Polluted Cities Today — {date_str} | AQI Report"

    # YouTube SEO title (punchy)
    yt_title = (
        f"{worst['city']} Air Quality DANGER — AQI {worst['aqi']} Today"
        if worst["aqi"] > 150
        else f"World Air Quality Report — {date_str}"
    )

    # Hook
    hook = (
        f"{worst['city']} hits AQI {worst['aqi']} — {worst['category'].upper()}! "
        f"Here are today's most polluted cities."
    )

    # Narration script (fed to TTS)
    lines = [
        f"Today's air quality report — {date_str}.",
        f"The most polluted city right now is {worst['city']}, "
        f"with an AQI of {worst['aqi']} — that's {worst['category'].lower()}. "
        f"{worst['advice']}",
    ]
    for i, c in enumerate(top5[1:], 2):
        lines.append(
            f"Number {i}: {c['city']}, AQI {c['aqi']} — {c['category']}."
        )
    if best:
        lines.append(
            f"The cleanest air today? {best['city']} with AQI {best['aqi']} — {best['category']}."
        )
    lines.append("Follow for daily air quality updates. Stay safe out there.")
    narration = " ".join(lines)

    # Scenes for image generation (one per top city)
    scenes = []
    for i, c in enumerate(top5, 1):
        scenes.append({
            "scene_number": i,
            "city": c["city"],
            "aqi":  c["aqi"],
            "category": c["category"],
            "color": c["color"],
            "storyboard_description": (
                f"city skyline of {c['city']} with {_sky_desc(c['aqi'])} sky, "
                f"dramatic atmosphere, urban landscape"
            ),
            "narration_segment": (
                f"{c['city']}: AQI {c['aqi']} — {c['category']}."
            ),
        })

    # Tags
    city_names = [c["city"] for c in top5]
    tags = (
        ["air quality", "aqi", "air pollution", "air quality today",
         "pollution", "most polluted city", "aqi report", "daily aqi",
         "air quality index", "pollution today", "clean air", "smog"]
        + [f"{n.lower()} air quality" for n in city_names]
        + [f"aqi {n.lower()}" for n in city_names]
    )

    return {
        "title":         title,
        "youtube_title": yt_title[:100],
        "url":           "https://air-quality-api.open-meteo.com",
        "source":        "Google Air Quality API / Open-Meteo",
        "hook":          hook,
        "narration":     narration,
        "shorts_narration": narration,
        "scenes":        scenes,
        "characters":    "",
        "visual_style":  "aqi_report",
        "shorts_only":   True,
        "viral_score":   7.0,
        "tags":          tags,
        "cities":        cities,
        "worst_city":    worst,
        "best_city":     best,
        "date":          today_str,
        "title_variants": [yt_title] * 4,
    }


def _sky_desc(aqi: int) -> str:
    if aqi <= 50:   return "clear blue"
    if aqi <= 100:  return "slightly hazy"
    if aqi <= 150:  return "hazy orange-grey"
    if aqi <= 200:  return "heavy smog orange"
    if aqi <= 300:  return "thick toxic smog dark orange"
    return "apocalyptic dark red toxic smog"
