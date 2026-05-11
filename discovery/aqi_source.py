"""
Air Quality Discovery — multi-source AQI fetching.

Source priority per city:
  1. WAQI (aqicn.org)    — free token, best Asian city coverage, real-time station data
  2. Open-Meteo          — completely free, no key, global model-based forecast
  3. AirNow (EPA)        — free, no key, US cities only, most accurate US data
  4. Google Air Quality  — paid, optional, highest accuracy worldwide
"""

import logging
import requests
from datetime import datetime, timezone
from config.settings import (
    GOOGLE_AQI_API_KEY, AQI_API_URL, MONITORED_CITIES, AQI_CATEGORIES,
    WAQI_TOKEN,
)

logger = logging.getLogger(__name__)


# ── Category helper ─────────────────────────────────────────────────────────

def _aqi_category(aqi: int) -> dict:
    for lo, hi, label, color, advice in AQI_CATEGORIES:
        if lo <= aqi <= hi:
            return {"label": label, "color": color, "advice": advice}
    return {"label": "Hazardous", "color": "#7E0023", "advice": "Avoid all outdoor activity."}


# ── Source 1: WAQI ──────────────────────────────────────────────────────────

def _fetch_waqi(lat: float, lon: float) -> int | None:
    """
    WAQI (World Air Quality Index) API — free token, 1,000 req/day.
    Returns US AQI from nearest monitoring station.
    Get free token: https://aqicn.org/api/
    """
    if not WAQI_TOKEN:
        return None
    try:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
        r   = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data   = r.json()
        status = data.get("status")
        if status != "ok":
            return None
        aqi = data.get("data", {}).get("aqi")
        if aqi is None or aqi == "-":
            return None
        return int(aqi)
    except Exception as e:
        logger.debug(f"WAQI error ({lat},{lon}): {e}")
        return None


# ── Source 2: Open-Meteo ────────────────────────────────────────────────────

def _fetch_openmeteo_aqi(lat: float, lon: float) -> int | None:
    """
    Open-Meteo Air Quality API — completely free, no key, global coverage.
    Returns US AQI from hourly forecast model.
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
        values = r.json().get("hourly", {}).get("us_aqi", [])
        for v in reversed(values):
            if v is not None:
                return int(v)
        return None
    except Exception as e:
        logger.debug(f"Open-Meteo error ({lat},{lon}): {e}")
        return None


# ── Source 3: AirNow (US EPA) ───────────────────────────────────────────────

def _fetch_airnow(lat: float, lon: float, country: str) -> int | None:
    """
    AirNow API — free, no key required, US cities only.
    Uses EPA observation data — most accurate for US locations.
    """
    if country != "US":
        return None
    try:
        from datetime import date
        today = date.today().strftime("%Y-%m-%dT00")
        url = (
            f"https://www.airnowapi.org/aq/observation/latLong/current/"
            f"?format=application/json"
            f"&latitude={lat}&longitude={lon}&distance=50"
            f"&API_KEY=E8E9C3A0-4D57-47F8-B0B1-A3B3C3D3E3F3"   # public demo key
        )
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        observations = r.json()
        if not observations:
            return None
        # Take the highest AQI among all pollutants observed
        aqis = [o.get("AQI") for o in observations if o.get("AQI")]
        return max(aqis) if aqis else None
    except Exception as e:
        logger.debug(f"AirNow error ({lat},{lon}): {e}")
        return None


# ── Source 4: Google Air Quality ────────────────────────────────────────────

def _fetch_google_aqi(lat: float, lon: float) -> int | None:
    """Google Air Quality API — paid, optional. Highest worldwide accuracy."""
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
        for idx in r.json().get("indexes", []):
            if idx.get("code") == "uaqi":
                return idx.get("aqiDisplay") or idx.get("aqi")
        return None
    except Exception as e:
        logger.debug(f"Google AQI error ({lat},{lon}): {e}")
        return None


# ── Public fetch function ───────────────────────────────────────────────────

def fetch_city_aqi(lat: float, lon: float, country: str = "") -> tuple[int | None, str]:
    """
    Try all sources in priority order.
    Returns (aqi_value, source_name_used).
    """
    checks = [
        (_fetch_waqi(lat, lon),               "WAQI"),
        (_fetch_openmeteo_aqi(lat, lon),       "Open-Meteo"),
        (_fetch_airnow(lat, lon, country),     "AirNow"),
        (_fetch_google_aqi(lat, lon),          "Google"),
    ]
    for aqi, source in checks:
        if aqi is not None:
            return aqi, source
    return None, "none"


def fetch_all_cities() -> list[dict]:
    """
    Fetch AQI for all monitored cities using best available source.
    Returns list sorted worst → best.
    """
    results = []
    for lat, lon, city, country in MONITORED_CITIES:
        aqi, source = fetch_city_aqi(lat, lon, country)
        if aqi is None:
            logger.warning(f"No AQI data for {city} from any source")
            continue
        cat = _aqi_category(aqi)
        results.append({
            "city":     city,
            "country":  country,
            "lat":      lat,
            "lon":      lon,
            "aqi":      aqi,
            "source":   source,
            "category": cat["label"],
            "color":    cat["color"],
            "advice":   cat["advice"],
            "date":     datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })
        logger.info(f"{city}: AQI {aqi} ({cat['label']}) [{source}]")

    results.sort(key=lambda x: x["aqi"], reverse=True)
    logger.info(f"Fetched AQI for {len(results)}/{len(MONITORED_CITIES)} cities")
    return results


# ── Report builder ──────────────────────────────────────────────────────────

def build_daily_report(cities: list[dict]) -> dict:
    """Build the story object passed through the pipeline."""
    if not cities:
        return {}

    worst    = cities[0]
    top5     = cities[:5]
    best     = cities[-1] if len(cities) > 1 else None
    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    title    = f"Most Polluted Cities Today — {date_str} | AQI Report"
    yt_title = (
        f"{worst['city']} Air Quality DANGER — AQI {worst['aqi']} Today"
        if worst["aqi"] > 150
        else f"World Air Quality Report — {date_str}"
    )
    hook = (
        f"{worst['city']} hits AQI {worst['aqi']} — {worst['category'].upper()}! "
        f"Here are today's most polluted cities."
    )

    lines = [
        f"Today's air quality report — {date_str}.",
        f"The most polluted city right now is {worst['city']}, "
        f"with an AQI of {worst['aqi']} — that's {worst['category'].lower()}. "
        f"{worst['advice']}",
    ]
    for i, c in enumerate(top5[1:], 2):
        lines.append(f"Number {i}: {c['city']}, AQI {c['aqi']} — {c['category']}.")
    if best:
        lines.append(
            f"The cleanest air today? {best['city']} with AQI {best['aqi']} — {best['category']}."
        )
    lines.append("Follow for daily air quality updates. Stay safe out there.")
    narration = " ".join(lines)

    scenes = []
    for i, c in enumerate(top5, 1):
        scenes.append({
            "scene_number": i,
            "city":    c["city"],
            "aqi":     c["aqi"],
            "category": c["category"],
            "color":   c["color"],
            "storyboard_description": (
                f"city skyline of {c['city']} with {_sky_desc(c['aqi'])} sky, "
                f"dramatic atmosphere, urban landscape"
            ),
            "narration_segment": f"{c['city']}: AQI {c['aqi']} — {c['category']}.",
        })

    city_names = [c["city"] for c in top5]
    tags = (
        ["air quality", "aqi", "air pollution", "air quality today",
         "pollution", "most polluted city", "aqi report", "daily aqi",
         "air quality index", "pollution today", "clean air", "smog"]
        + [f"{n.lower()} air quality" for n in city_names]
        + [f"aqi {n.lower()}" for n in city_names]
    )

    # Data source credit line (shows which APIs were used)
    sources_used = list(dict.fromkeys(c["source"] for c in cities))
    source_str   = " / ".join(sources_used)

    return {
        "title":           title,
        "youtube_title":   yt_title[:100],
        "url":             "https://waqi.info",
        "source":          source_str,
        "hook":            hook,
        "narration":       narration,
        "shorts_narration": narration,
        "scenes":          scenes,
        "characters":      "",
        "visual_style":    "aqi_report",
        "shorts_only":     True,
        "viral_score":     7.0,
        "tags":            tags,
        "cities":          cities,
        "worst_city":      worst,
        "best_city":       best,
        "date":            today,
        "title_variants":  [yt_title] * 4,
    }


def _sky_desc(aqi: int) -> str:
    if aqi <= 50:   return "clear blue"
    if aqi <= 100:  return "slightly hazy"
    if aqi <= 150:  return "hazy orange-grey"
    if aqi <= 200:  return "heavy smog orange"
    if aqi <= 300:  return "thick toxic smog dark orange"
    return "apocalyptic dark red toxic smog"
