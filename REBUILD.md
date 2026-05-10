# AI Rebuild Instructions

This file contains everything needed to fully rebuild the 4-channel YouTube automation
system from scratch. Feed this file to Claude Code and it will reconstruct the entire system.

---

## What to Build

4 automated YouTube Shorts channels on a single Mac. Each channel:
1. Discovers content from free APIs/RSS daily
2. Scores stories by viral potential (keyword-based, zero API calls)
3. Generates a script via Gemini AI (1 call per video)
4. Creates AI images via Pollinations.ai (free, no key)
5. Generates voiceover via Microsoft Edge TTS (free, no key)
6. Composes video via MoviePy with animated effects
7. Uploads to YouTube via Data API v3
8. Runs automatically via macOS cron — no human needed

---

## The 4 Channels

### Channel 1 — The Odd Investor
- **YouTube:** https://www.youtube.com/@TheOddInvestor
- **Niche:** Weird/bizarre real finance stories
- **Narrator:** Deadpan (calm about absurd events)
- **Discovery:** Reddit (WSB, personalfinance, investing) + Finance RSS (Reuters, CNBC, MarketWatch, Yahoo Finance, ZeroHedge)
- **Filter keywords:** accidentally, forgot, billion, crashed, bizarre, meme stock, glitch, sued, scam
- **Cron:** 12:00 PM daily, 1 video
- **YouTube category:** 25 (News & Politics)
- **Tags:** the odd investor, finance, investing, stock market, weird finance, meme stocks...
- **Thumbnail colors:** Dark red/yellow, dark purple/white, dark green/yellow, dark orange/white
- **Token file:** token.pickle
- **DB:** data/news.db
- **Repo:** Yuli-Developer/breaking-weird-v2
- **Project dir:** breaking-weird-v2/

### Channel 2 — Patent Secrets
- **YouTube:** https://www.youtube.com/@PatentSecrets
- **Niche:** What Big Tech is secretly building (USPTO patents)
- **Narrator:** Investigative journalist (exposing secrets)
- **Discovery:**
  - USPTO PatentsView API v1: `https://search.patentsview.org/api/v1/patent/`
  - Google News RSS per company: `https://news.google.com/rss/search?q={company}+patent`
  - TechCrunch patents feed, The Verge, Wired, Ars Technica
- **Companies watched:** Apple, Google, Meta, Amazon, Microsoft, Tesla, OpenAI, Nvidia, Samsung, Netflix, SpaceX, ByteDance, Anthropic, Snap
- **Viral keywords:** surveillance, tracking, brain, neural, emotion, facial recognition, autonomous, robot, hologram, implant
- **Cron:** 2:00 PM daily, 1 video
- **YouTube category:** 28 (Science & Technology)
- **Thumbnail colors:** Dark blue/green, dark purple/white, dark teal/gold, dark navy/white
- **Token file:** token_patent.pickle
- **DB:** data/patent_secrets.db
- **Repo:** Yuli-Developer/patent-secrets
- **Project dir:** patent-secrets/

### Channel 3 — Tax Money Watch
- **YouTube:** https://www.youtube.com/@TaxMoneyWatch
- **Niche:** Government waste / taxpayer money exposé
- **Narrator:** Sarcastic (outraged taxpayer)
- **Discovery:**
  - USASpending.gov API: `https://api.usaspending.gov/api/v2/search/spending_by_award/`
  - Filter: grants $500K–$50M with keywords (study, research, awareness, consulting, art, sculpture)
  - Google News RSS: "government waste taxpayer money", "federal government paid million study"
  - GovExec RSS, Federal News Network RSS
- **Viral keywords:** million, billion, taxpayer, government, wasted, ridiculous, study, consulting, awareness
- **Ragebait high weight (20%):** surveillance, without consent, manipulation, dynamic pricing
- **Amount boost:** +2.0 if award ≥ $10M, +1.0 if ≥ $1M
- **Cron:** 10:00 AM daily, 1 video
- **YouTube category:** 25 (News & Politics)
- **Thumbnail colors:** Dark red/gold, navy red/white, dark gold/red, dark red/white
- **Token file:** token_taxwatch.pickle
- **DB:** data/taxwatch.db
- **Repo:** Yuli-Developer/tax-money-watch
- **Project dir:** tax-money-watch/

### Channel 4 — Startup Graveyard (PRIORITY)
- **YouTube:** https://www.youtube.com/@StartupGraveyard
- **Niche:** Funded startup failures, rise-and-fall stories
- **Narrator:** Horror documentary (ominous, inevitable doom)
- **Discovery:**
  - Google News RSS: "startup shutdown 2025", "startup shuts down raised million", "tech startup closes bankrupt", "startup runs out of money", "vc backed startup folds"
  - TechCrunch startups feed + layoffs feed
  - Hacker News: `https://hnrss.org/frontpage?q=startup+shutdown+failed`
- **Filter:** must contain shutdown/failed keyword AND money/funding keyword
- **Reject:** restaurant, bakery, retail, local business
- **Viral keywords:** raised, million, billion, series a/b/c, unicorn, shutdown, bankrupt, pivot, founder
- **Cron:** 4:00 PM daily, 3 videos (priority channel)
- **YouTube category:** 28 (Science & Technology)
- **Thumbnail colors:** Dark tombstone/gray, blood red/white, gray/ghost red, red alert/gold
- **Token file:** token_graveyard.pickle
- **DB:** data/graveyard.db
- **Repo:** Yuli-Developer/startup-graveyard
- **Project dir:** startup-graveyard/

---

## Core Pipeline (same for all channels)

Build this in `pipeline/orchestrator.py`:

```
Step 0:  analytics/feedback_loop.py → analyze_and_improve() + get_optimized_style()
Step 1:  discovery/engine.py → run_discovery(limit_per_source=15)
Step 2:  prediction/viral_scorer.py → score_and_rank(stories, top_n=STORIES_PER_RUN)
Step 3:  ai/narrative_generator.py → generate_script(story, style=style)
Step 4:  rendering/visual_director.py → generate_all_images(story, run_id)
Step 4b: rendering/kling_engine.py → generate_all_kling_videos(story, run_id)  [USE_KLING=false]
Step 5:  rendering/caption_engine.py → prepare_voiceover(narration, run_id)
Step 6:  rendering/audio_engine.py → get_music_track()
Step 7:  rendering/video_composer.py → compose_shorts(story, audio, music, run_id)
Step 8:  thumbnails/thumbnail_engine.py → generate_thumbnails(story, run_id)
Step 9:  publishing/youtube_publisher.py → publish_shorts(story, run_id)
Step 10: analytics/collector.py → collect_and_store(run_id, video_id, "youtube")
```

---

## Key Technical Decisions

### Viral Scoring — ZERO API calls
Never use Gemini for scoring. Use keyword matching only:
```python
def _keyword_score(text, keywords, cap=10.0):
    hits = sum(1 for kw in keywords if kw.lower() in text.lower())
    return min(cap, round(hits * 2.5, 1))
```
7 keyword banks: CURIOSITY, THUMBNAIL, RAGEBAIT, RETENTION, COMMENT, SHAREABILITY, SHORTS
Weighted sum → total score. Reject below MIN_VIRAL_SCORE=3.0

### Gemini — 1 call per video only (script generation)
Model: `gemini-2.0-flash`
Free tier: 20 requests/day. 6 videos/day uses only 6 calls.
Never call Gemini for scoring, thumbnails, or any other step.

### Image Generation — Pollinations.ai (free)
```python
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true"
```
Always use 1080×1920 (9:16 vertical for Shorts). 4 images per video.

### Voiceover — Microsoft Edge TTS (free)
```python
import edge_tts
comm = edge_tts.Communicate(text, voice="en-GB-RyanNeural")
```
No API key. No cost. Word-level timestamps for caption sync.

### YouTube Tags — 500 char total limit
```python
def _trim_tags(tags):
    result, total = [], 0
    for t in tags:
        t = t.replace('#','').strip()
        if t and total + len(t) + 1 <= 498:
            result.append(t); total += len(t) + 1
    return result
```
Always strip # from tags before uploading. YouTube rejects tags with #.

### YouTube API Quota — 10,000 units/day
- Upload video: 1,600 units
- Set thumbnail: 50 units
- Per video: 1,650 units
- 6 videos/day = 9,900 units (100 spare)
- Distribution: Startup Graveyard 3, others 1 each

### Thumbnails — 4 variants, rule-based scoring
Generate 4 variants with PIL. Score using:
- CTR keywords (40%): %, million, billion, crashed, shocked, secret, revealed
- Emotion keywords (30%): shock, curiosity, anger, laughter
- Readability (15%): words ≤5 = 10, ≤7 = 8.5, else 7.0
- Mobile score (15%): uppercase ratio
- Theme boost: [0.8, 0.4, 0.6, 0.5] for variants 1-4
Auto-select highest scoring. Upload via `youtube.thumbnails().set()`

### Shorts Script Format
Max 130 words narration. Exactly 4 scenes. Structure:
`Hook (10 words) → Setup (2 sentences) → Twist → 1-line payoff`
Gemini returns JSON with: youtube_title, hook, narration, title_variants (×4), scenes (×4), tags, description_hook

### Video Composition
- 2-second branded intro card (channel name + title)
- 4 scenes with motion effects (ken_burns_zoom_in/out, pan_left/right, parallax, zoom_burst)
- Camera shake on odd-numbered scenes
- Scanline overlay for cinematic feel
- Red alert pulse on high-energy moments
- Scrolling ticker bar with headline
- Captions: word-by-word, center screen, bold white with black outline
- Background music at 12% volume
- FFmpeg: libx264, aac, 3000k bitrate, preset=fast

---

## Environment Variables

```env
# Required
GEMINI_API_KEY=AIzaSyBZ8sSzhDb7ZHM3aSk4u4X6sIWW_om_TAI
GEMINI_MODEL=gemini-2.0-flash
YOUTUBE_CLIENT_SECRETS=client_secrets.json
YOUTUBE_TOKEN_PATH=token_X.pickle          # unique per channel
DB_PATH=data/X.db                          # unique per channel

# Pipeline
OUTPUT_DIR=output
STORIES_PER_RUN=1
MIN_VIRAL_SCORE=3.0
SHORTS_ONLY=true
MAX_SHORTS_WORDS=130
NARRATOR_STYLE=deadpan                     # per channel default

# Optional
IMAGE_TIER=pollinations
USE_KLING=false
AIMLAPI_KEY=4ab55a76c0c26ce8e07a877d6c11d0f5
```

---

## Cron Jobs (macOS)

```cron
0 10 * * * /Users/adityashri/miniconda3/bin/python3 /Users/adityashri/Desktop/business/business_software/youtube/tax-money-watch/run_batch.py 1 >> /Users/adityashri/Desktop/business/business_software/youtube/tax-money-watch/logs/batch_cron.log 2>&1
0 12 * * * /Users/adityashri/miniconda3/bin/python /Users/adityashri/Desktop/business/business_software/youtube/breaking-weird-v2/run_batch.py 1 >> /Users/adityashri/Desktop/business/business_software/youtube/breaking-weird-v2/logs/batch_cron.log 2>&1
0 14 * * * /Users/adityashri/miniconda3/bin/python3 /Users/adityashri/Desktop/business/business_software/youtube/patent-secrets/run_batch.py 1 >> /Users/adityashri/Desktop/business/business_software/youtube/patent-secrets/logs/batch_cron.log 2>&1
0 16 * * * /Users/adityashri/miniconda3/bin/python3 /Users/adityashri/Desktop/business/business_software/youtube/startup-graveyard/run_batch.py 3 >> /Users/adityashri/Desktop/business/business_software/youtube/startup-graveyard/logs/batch_cron.log 2>&1
```

Set with: `crontab -e`
Mac must not sleep: System Settings → Battery → Prevent automatic sleep

---

## YouTube OAuth Setup (per channel)

Each channel has its own token file. To authorize:
1. Copy `client_secrets.json` from Google Cloud Console into project folder
2. Run `python3 authorize_youtube.py`
3. Browser opens — select the correct channel brand account
4. Token saved automatically

Google Cloud project: same `client_secrets.json` for all 4 channels
Client ID: `1012569836740-psuai9nh87jh102bepg79qf1395jg556.apps.googleusercontent.com`

Channel tokens:
- The Odd Investor → `token.pickle` (channel: UChMgxbYfev1yPUuGR856S0Q... The-Odd-Investor)
- Patent Secrets → `token_patent.pickle` (channel: UCg7vjS5AwPLs3wP4sMs8cXw)
- Tax Money Watch → `token_taxwatch.pickle` (channel: UC4-sppHr3ZiWjIYRpbJsoZQ)
- Startup Graveyard → `token_graveyard.pickle` (channel: UCLUVNlmweVPXJerClTYIhSg)

---

## Dependencies (requirements.txt)

```
google-generativeai
google-genai
google-api-python-client
google-auth-oauthlib
google-auth-httplib2
moviepy>=2.0
Pillow
numpy
edge-tts
feedparser
aiohttp
praw
python-dotenv
requests
```

Install: `pip install -r requirements.txt`

---

## Music

Default track: `assets/music/cinematic_tensions.mp3` (Fesliyan Studios, free)
Used by all 4 channels. Copy into each channel's `assets/music/` folder.

---

## GitHub Repos (all private)

| Channel | Repo |
|---------|------|
| The Odd Investor | `Yuli-Developer/breaking-weird-v2` |
| Patent Secrets | `Yuli-Developer/patent-secrets` |
| Tax Money Watch | `Yuli-Developer/tax-money-watch` |
| Startup Graveyard | `Yuli-Developer/startup-graveyard` |
| Old (archived) | `Yuli-Developer/weird-news-automation` |

---

## Rebuild Steps for Claude

If rebuilding from scratch, tell Claude:

> "Read REBUILD.md in the breaking-weird-v2 repo and rebuild the complete
> 4-channel YouTube automation system exactly as described. Start with
> breaking-weird-v2, then patent-secrets, tax-money-watch, startup-graveyard.
> Use the same file structure, same API decisions, same cron schedule.
> Set up all YouTube OAuth tokens and cron jobs at the end."

Claude will need access to:
- This REBUILD.md file
- The `client_secrets.json` file
- The Gemini API key
- macOS terminal with Python 3.12 + pip

Estimated rebuild time with Claude: 2–3 hours.

---

## Monthly Cost Summary

| Item | Cost |
|------|------|
| Gemini 2.0 Flash (6 calls/day, free tier) | $0 |
| Edge TTS | $0 |
| Pollinations.ai | $0 |
| YouTube Data API | $0 |
| Electricity | ~$0.10 |
| **Total** | **~$0.10/month** |
