# YouTube Automation System — Full Architecture

4 fully automated YouTube Shorts channels running on a single Mac.
Zero daily effort after setup. Discovers content, writes scripts, generates voice + visuals, composes video, and uploads — all automatically via cron.

---

## Channels

| Channel | Niche | Cron | Videos/day | Est. CPM |
|---------|-------|------|------------|---------|
| [The Odd Investor](https://www.youtube.com/@TheOddInvestor) | Weird finance stories | 12:00 PM | 1 | $4–8 |
| [Patent Secrets](https://www.youtube.com/@PatentSecrets) | Big Tech secret patents | 2:00 PM | 1 | $15–25 |
| [Tax Money Watch](https://www.youtube.com/@TaxMoneyWatch) | Government waste exposé | 10:00 AM | 1 | $8–15 |
| [Startup Graveyard](https://www.youtube.com/@StartupGraveyard) | Funded startup failures | 4:00 PM | 3 | $10–20 |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        macOS Cron (4 jobs)                      │
│         10AM · 12PM · 2PM · 4PM — one per channel              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   pipeline/orchestrator.py                      │
│                                                                 │
│  Step 0  ── Analytics feedback loop (improve over time)        │
│  Step 1  ── Discovery Engine (find stories)                    │
│  Step 2  ── Viral Scorer (rank stories, keyword-based)         │
│  Step 3  ── Script Generator (Gemini AI)                       │
│  Step 4  ── Image Generator (Pollinations.ai)                  │
│  Step 4b ── Kling AI video clips (optional, paid)              │
│  Step 5  ── Voiceover + Captions (Microsoft Edge TTS)          │
│  Step 6  ── Background Music (local MP3)                       │
│  Step 7  ── Video Composer (MoviePy + FFmpeg)                  │
│  Step 8  ── Thumbnail Generator (PIL, 4 variants scored)       │
│  Step 9  ── YouTube Upload (Data API v3)                       │
│  Step 10 ── Baseline Analytics Collection                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Discovery Sources (per channel)

### The Odd Investor
- Reddit: r/wallstreetbets, r/personalfinance, r/investing, r/stocks, r/CryptoCurrency
- RSS: Reuters Business, MarketWatch, CNBC, Yahoo Finance, Bloomberg, Forbes, ZeroHedge

### Patent Secrets
- USPTO PatentsView API v1 — 14 companies monitored daily:
  Apple, Google, Meta, Amazon, Microsoft, Tesla, OpenAI, Nvidia, Samsung, Netflix, SpaceX, ByteDance, Anthropic, Snap
- Google News RSS: `[company] patent` per company
- TechCrunch, The Verge, Wired, Ars Technica

### Tax Money Watch
- USASpending.gov API — federal grants/contracts filtered for bizarre spending
- Google News RSS: government waste, taxpayer money, federal spending
- GovExec, Federal News Network

### Startup Graveyard
- Google News RSS: startup shutdown, startup bankrupt, startup closes
- TechCrunch: startups + layoffs feeds
- Hacker News: startup failure discussions

---

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Orchestration | Python 3.12 + cron | Free |
| Script generation | Google Gemini 2.0 Flash | Free (20 req/day) |
| Voiceover | Microsoft Edge TTS (`edge-tts`) | Free |
| Images | Pollinations.ai (Flux model) | Free |
| Video compose | MoviePy 2.x + FFmpeg | Free |
| Captions | Word-by-word animated (custom PIL) | Free |
| Thumbnails | PIL/Pillow — 4 variants, auto-scored | Free |
| Background music | Local MP3 (Cinematic Tensions) | Free |
| Database | SQLite | Free |
| YouTube upload | YouTube Data API v3 | Free |
| Storage | Local filesystem | Free |
| **Total** | | **~$0/month** |

---

## File Structure (per channel)

```
channel-name/
├── pipeline/
│   └── orchestrator.py        # master pipeline controller
├── discovery/
│   ├── engine.py              # discovery orchestrator
│   ├── rss_source.py          # RSS feed fetcher
│   ├── reddit_source.py       # Reddit API (Odd Investor only)
│   ├── uspto_source.py        # USPTO API (Patent Secrets only)
│   ├── govspend_source.py     # USASpending.gov (Tax Money Watch only)
│   └── startup_source.py     # Startup failure news (Startup Graveyard only)
├── prediction/
│   └── viral_scorer.py        # keyword-based viral scoring (zero API calls)
├── ai/
│   ├── narrative_generator.py # Gemini API script generation
│   └── prompt_templates.py    # channel-specific narrator prompts
├── rendering/
│   ├── visual_director.py     # Pollinations.ai image generation
│   ├── caption_engine.py      # Edge TTS voiceover + animated captions
│   ├── audio_engine.py        # background music selection
│   ├── motion_engine.py       # Ken Burns, zoom, pan, parallax effects
│   ├── video_composer.py      # final video assembly (main + Shorts)
│   └── kling_engine.py        # Kling AI video clips (optional)
├── thumbnails/
│   └── thumbnail_engine.py    # 4-variant thumbnail generator + scorer
├── publishing/
│   ├── youtube_publisher.py   # YouTube upload + thumbnail set
│   └── platform_adapter.py   # TikTok/Instagram (optional)
├── analytics/
│   ├── collector.py           # YouTube Analytics API collector
│   └── feedback_loop.py       # auto-improve based on performance
├── storage/
│   └── database.py            # SQLite: stories, runs, analytics
├── config/
│   └── settings.py            # all settings via .env
├── run_batch.py               # batch runner (called by cron)
├── authorize_youtube.py       # one-time YouTube OAuth setup
└── .env                       # API keys + channel config
```

---

## Video Pipeline (per video, ~3–5 minutes total)

```
Discovery (5–15s)
    └── Fetch stories from APIs/RSS feeds in parallel (asyncio)
    └── Deduplicate against SQLite DB

Viral Scoring (instant)
    └── Keyword matching across 7 dimensions
    └── Zero API calls — runs offline

Script Generation (10–20s)
    └── Gemini 2.0 Flash — 1 API call per video
    └── Returns JSON: title, narration, 4 scenes, tags, hooks

Image Generation (30–90s)
    └── 4 scenes × Pollinations.ai Flux model
    └── Async parallel requests
    └── 9:16 vertical portrait framing (Shorts optimised)

Voiceover (10–20s)
    └── Microsoft Edge TTS (en-GB-RyanNeural)
    └── Outputs MP3 with word-level timestamps

Video Composition (60–180s)
    └── 2s intro card (channel branding)
    └── 4 scenes × animated motion effects
    └── Word-by-word caption overlay
    └── Background music mixed at 12% volume
    └── FFmpeg export: libx264, 3000k bitrate

Thumbnails (5s)
    └── 4 variants rendered (different color themes)
    └── Rule-based CTR scoring
    └── Best variant auto-selected and uploaded

YouTube Upload (30–60s)
    └── Resumable upload (10MB chunks)
    └── Metadata: title, tags, description, category
    └── Thumbnail set via separate API call
```

---

## Viral Scoring System

No API calls — pure keyword matching across 7 dimensions:

| Dimension | Weight | What it checks |
|-----------|--------|---------------|
| Curiosity | 25–30% | Topic novelty, intrigue keywords |
| Thumbnail strength | 20% | Visual/title clickability keywords |
| Ragebait | 10–20% | Outrage/anger triggers |
| Retention potential | 15–20% | Story structure hooks |
| Comment potential | 10% | Divisive/brand name mentions |
| Shareability | 10% | "Send this to someone" triggers |
| Shorts potential | 10% | Fast-paced, punchy keywords |

Stories scoring below 3.0/10 are rejected. Top story per run is selected.

---

## Thumbnail System

4 variants generated per video with channel-specific color schemes:

| Channel | Theme 1 | Theme 2 | Theme 3 | Theme 4 |
|---------|---------|---------|---------|---------|
| Odd Investor | Dark red/gold | Dark purple/white | Dark green/gold | Dark orange/white |
| Patent Secrets | Dark blue/green | Dark purple/white | Dark teal/gold | Dark navy/white |
| Tax Money Watch | Dark red/gold | Navy red/white | Dark gold/red | Dark red/white |
| Startup Graveyard | Dark tombstone | Blood red/white | Gray/red | Red alert |

Scoring: CTR keywords (40%) + emotion (30%) + readability (15%) + mobile (15%)

---

## YouTube API Quota

One shared Google Cloud project — 10,000 units/day:

| Action | Units | Daily usage |
|--------|-------|-------------|
| Video upload | 1,600 | 6 uploads × 1,600 = 9,600 |
| Thumbnail set | 50 | 6 × 50 = 300 |
| **Total** | | **9,900 / 10,000** |

To scale beyond 6 videos/day: request quota increase at console.cloud.google.com (free, 1–2 days).

---

## Narrator Styles (per channel)

| Channel | Default Style | Tone |
|---------|--------------|------|
| The Odd Investor | `deadpan` | Calm, clinical, underreact to absurdity |
| Patent Secrets | `investigative` | Methodical, urgent, conspiratorial |
| Tax Money Watch | `sarcastic` | Outraged disbelief, rhetorical questions |
| Startup Graveyard | `horror_documentary` | Ominous, inevitable doom, cinematic |

All channels support: `deadpan`, `horror_documentary`, `sarcastic`, `investigative`, `hyper_tiktok`

---

## Environment Variables (.env)

```env
GEMINI_API_KEY=           # Google AI Studio key
GEMINI_MODEL=gemini-2.0-flash
YOUTUBE_CLIENT_SECRETS=client_secrets.json
YOUTUBE_TOKEN_PATH=       # unique per channel (token_X.pickle)
DB_PATH=                  # unique per channel (data/X.db)
OUTPUT_DIR=output
STORIES_PER_RUN=1
MIN_VIRAL_SCORE=3.0
SHORTS_ONLY=true
NARRATOR_STYLE=           # channel default style
IMAGE_TIER=pollinations
USE_KLING=false
```

---

## Cron Jobs (macOS)

```cron
0 10 * * *  python3 /path/tax-money-watch/run_batch.py 1
0 12 * * *  python3 /path/breaking-weird-v2/run_batch.py 1
0 14 * * *  python3 /path/patent-secrets/run_batch.py 1
0 16 * * *  python3 /path/startup-graveyard/run_batch.py 3
```

Mac must be on and not sleeping. Disable sleep: System Settings → Battery → Prevent automatic sleep.

---

## GitHub Repos (all private)

| Repo | Channel |
|------|---------|
| `Yuli-Developer/breaking-weird-v2` | The Odd Investor |
| `Yuli-Developer/patent-secrets` | Patent Secrets |
| `Yuli-Developer/tax-money-watch` | Tax Money Watch |
| `Yuli-Developer/startup-graveyard` | Startup Graveyard |

---

## Monthly Cost

| Item | Cost |
|------|------|
| Gemini API (free tier — 20 req/day, 6 used) | $0 |
| Edge TTS | $0 |
| Pollinations.ai | $0 |
| YouTube API | $0 |
| Electricity | ~$0.10 |
| **Total** | **~$0.10/month** |

---

## Scale-Up Roadmap

| Milestone | Action |
|-----------|--------|
| Any channel 500 subs | Enable YouTube monetization |
| Want 5 videos/channel/day | Request API quota increase (free) |
| 3 months stable | Add TikTok + Instagram cross-posting |
| Channel gaining traction | Add affiliate links to descriptions |
| $500+/month revenue | Enable Gemini billing, scale to 10 videos/day |
