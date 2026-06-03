# Air Quality Channel — YouTube Automation

Fully automated YouTube Shorts channel publishing daily air quality reports for the world's most polluted cities.

**Content mode**: Live data — fetches real AQI readings every run, no pre-written scripts.

---

## What It Does

Every day at 6pm, the pipeline:
1. Fetches live AQI data for 20 cities (Google Air Quality API + WAQI)
2. Ranks cities by pollution level
3. Generates a narrated report script (Gemini AI)
4. Creates AQI data cards + AI images per city
5. Composes a 9:16 Shorts video
6. Uploads to YouTube

---

## Monitored Cities (20)

Delhi, Beijing, Mumbai, Lahore, Dhaka, Karachi, New York, Los Angeles, London, Paris, Tokyo, Seoul, Moscow, São Paulo, Cairo, Singapore, Dubai, Bangkok, Kuala Lumpur, Sydney

---

## Pipeline Architecture

```
AQI Data Fetch (Google Air Quality API + WAQI)
    └── discovery/aqi_source.py
            │
            ▼
    Script Gen  ── Gemini 2.5 Flash (city-by-city narration)
    Images      ── Imagen 4 + AQI card renderer
    Voiceover   ── Gemini TTS (Zephyr voice)
    Video       ── FFmpeg (10 scenes, word-proportional durations)
    Upload      ── YouTube Data API v3
```

---

## Cron Schedule

```
0 18 * * *   run_batch.py    → 6:00 PM daily Short
```

---

## Tech Stack

| Component | Tool |
|-----------|------|
| AQI data | Google Air Quality API + WAQI (free token) |
| Script gen | Gemini 2.5 Flash |
| TTS voice | Gemini TTS — **Zephyr** (calm, informative) |
| Fallback TTS | Edge TTS |
| Images | Imagen 4 + custom AQI card renderer (PIL) |
| Video | MoviePy + FFmpeg (10 scenes) |
| Upload | YouTube Data API v3 |

---

## Key Config (.env)

```env
GEMINI_API_KEY=...           # AI Studio key (Gemini + Imagen)
GOOGLE_AQI_API_KEY=...       # Google Cloud key (Air Quality API enabled)
WAQI_TOKEN=...               # Free: https://aqicn.org/api/
IMAGE_TIER=imagen4
```

Note: `GOOGLE_AQI_API_KEY` must be from a GCP project with the **Air Quality API** enabled.

---

## File Structure

```
air-quality-channel/
├── discovery/
│   └── aqi_source.py          # fetches live AQI for all 20 cities
├── rendering/
│   ├── visual_director.py     # Imagen 4 city images
│   ├── aqi_card_renderer.py   # AQI data card (city, AQI value, color)
│   ├── caption_engine.py      # Gemini TTS + captions
│   └── video_composer.py      # 10-scene video assembly
├── publishing/
│   └── youtube_publisher.py   # upload
├── config/
│   └── settings.py            # 20 cities config + AQI categories
├── run_batch.py               # cron entry point
└── .env
```

---

## Known Limitations

- Custom thumbnails disabled — channel needs YouTube verification (1,000 subs)
- Analytics API not enabled on the AQI GCP project — collection silently skipped

---

**Repo**: `Yuli-Developer/air-quality-channel`
