# YouTube Automation — 4 Channel Plan

## Overview
4 fully automated YouTube Shorts channels running on a single Mac.
Each channel discovers content, generates scripts (Gemini AI), creates voiceover (Microsoft Edge TTS),
generates images (Pollinations.ai), composes video (MoviePy), and uploads to YouTube — all automatically.

---

## Channels

### 1. The Odd Investor
- **URL:** https://www.youtube.com/@TheOddInvestor
- **Niche:** Weird/bizarre real finance stories
- **Narrator style:** Deadpan
- **Source:** Reddit (WSB, personalfinance) + Finance RSS feeds
- **CPM:** $4–8
- **Cron:** 12:00 PM daily
- **Videos/day:** 1
- **Project:** `breaking-weird-v2/`
- **Token:** `token.pickle`

### 2. Patent Secrets
- **URL:** https://www.youtube.com/@PatentSecrets
- **Niche:** What Big Tech is secretly building (USPTO patents)
- **Narrator style:** Investigative journalist
- **Source:** USPTO PatentsView API + Google News patent RSS
- **Companies watched:** Apple, Google, Meta, Amazon, Microsoft, Tesla, OpenAI, Nvidia, Samsung, Netflix, SpaceX, ByteDance, Anthropic, Snap
- **CPM:** $15–25 (tech audience)
- **Cron:** 2:00 PM daily
- **Videos/day:** 1
- **Project:** `patent-secrets/`
- **Token:** `token_patent.pickle`

### 3. Tax Money Watch
- **URL:** https://www.youtube.com/@TaxMoneyWatch (create this)
- **Niche:** Government waste / your taxes exposé
- **Narrator style:** Sarcastic outrage
- **Source:** USASpending.gov API + Google News government waste RSS
- **CPM:** $8–15 (politics/news audience)
- **Cron:** 10:00 AM daily
- **Videos/day:** 1
- **Project:** `tax-money-watch/`
- **Token:** `token_taxwatch.pickle`

### 4. Startup Graveyard ⭐ Priority Channel
- **URL:** https://www.youtube.com/@StartupGraveyard (create this)
- **Niche:** Funded startup failures / rise and fall stories
- **Narrator style:** Horror documentary
- **Source:** Google News + TechCrunch + Hacker News startup shutdowns
- **CPM:** $10–20 (tech/business audience)
- **Cron:** 4:00 PM daily
- **Videos/day:** 3 (priority channel)
- **Project:** `startup-graveyard/`
- **Token:** `token_graveyard.pickle`

---

## Daily Schedule

| Time     | Channel            | Videos | API Units |
|----------|--------------------|--------|-----------|
| 10:00 AM | Tax Money Watch    | 1      | 1,650     |
| 12:00 PM | The Odd Investor   | 1      | 1,650     |
| 2:00 PM  | Patent Secrets     | 1      | 1,650     |
| 4:00 PM  | Startup Graveyard  | 3      | 4,950     |
| **Total**|                    | **6**  | **9,900** |

YouTube API quota: 10,000 units/day (9,900 used — 100 spare)

---

## Monthly Cost

| Service            | Cost         |
|--------------------|--------------|
| Gemini 2.0 Flash   | ~$0.24/month |
| Edge TTS           | FREE         |
| Pollinations.ai    | FREE         |
| YouTube API        | FREE         |
| Electricity        | ~$0.10/month |
| **Total**          | **~$0.35/month** |

---

## Tech Stack

| Component       | Tool                        | Cost  |
|-----------------|-----------------------------|-------|
| Script AI       | Google Gemini 2.0 Flash     | Paid  |
| Voiceover       | Microsoft Edge TTS          | Free  |
| Images          | Pollinations.ai (flux model)| Free  |
| Video compose   | MoviePy + FFmpeg            | Free  |
| Video upload    | YouTube Data API v3         | Free  |
| Database        | SQLite                      | Free  |
| Scheduler       | macOS cron                  | Free  |

---

## GitHub Repos

- `github.com/Yuli-Developer/breaking-weird-v2` — The Odd Investor
- `github.com/Yuli-Developer/patent-secrets` — Patent Secrets
- `github.com/Yuli-Developer/tax-money-watch` — Tax Money Watch
- `github.com/Yuli-Developer/startup-graveyard` — Startup Graveyard

---

## Requirements to Keep Running

- Mac must be ON and not sleeping (disable sleep in System Settings → Battery)
- Internet connection
- Gemini API billing enabled (~$0.35/month total)
- YouTube OAuth tokens valid (auto-refresh, no manual action needed)

---

## Scale-Up Path

| When                        | Action                                           |
|-----------------------------|--------------------------------------------------|
| Any channel hits 1K subs    | Enable YouTube monetization on that channel      |
| Want more than 6 videos/day | Request YouTube API quota increase (free, 1-2 days) |
| Want 5 videos/channel/day   | Create separate Google Cloud project per channel |
| Channel hits 10K views/Short| Add affiliate links to descriptions             |
| 3 months in                 | Add TikTok + Instagram cross-posting (code exists)|

---

## Revenue Estimate (12 months)

| Channel           | Est. Monthly (mature) |
|-------------------|-----------------------|
| The Odd Investor  | $100–400              |
| Patent Secrets    | $300–800              |
| Tax Money Watch   | $200–600              |
| Startup Graveyard | $300–700              |
| + Affiliates      | $500–2,000            |
| **Total**         | **$1,400–4,500/month**|

---

## Next Steps

- [ ] Enable Gemini billing (console.cloud.google.com → APIs → Gemini → Billing)
- [ ] Disable Mac sleep (System Settings → Battery → Prevent sleep)
- [ ] Wait for Gemini quota reset (midnight Pacific) for first test run
- [ ] Monitor first week of videos in YouTube Studio
- [ ] Add affiliate links to video descriptions once channels grow
