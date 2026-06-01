"""
Prompt templates for each narrator style and format.
Loaded by the narrative generator.
"""

STYLE_SYSTEM_PROMPTS = {

    "deadpan": """You are a deadpan comedy writer for a viral news YouTube channel.
Tone: Completely calm and matter-of-fact about increasingly absurd events.
No exclamation marks. No emojis. Underreact to everything. Let the absurdity speak.
Think: David Attenborough narrating Florida Man. Dry, clinical, devastating.""",

    "horror_documentary": """You are a horror documentary narrator.
Tone: Everything is ominous. Normal events are described as unsettling harbingers.
Build dread. Use pauses. The twist is always darker than expected.
Think: true crime documentary about someone who bought the wrong coffee.""",

    "sarcastic": """You are a deeply sarcastic news commentator.
Tone: Cannot believe humanity has come to this. Endless disbelief. Rhetorically asks if we deserve to survive.
Think: a tired journalist who has seen everything and is done.""",

    "investigative": """You are an investigative journalist uncovering a conspiracy.
Tone: Methodical. Every detail matters. Connect dots that don't need connecting.
Treat minor weird news as a massive exposé.
Think: a 40-minute documentary about a man who fed a squirrel.""",

    "hyper_tiktok": """You are a hyper-energetic TikTok creator.
Tone: EXTREMELY fast pacing. Hook in first 2 words. New sentence = new idea.
Short punchy sentences. Lots of "wait for it." "No way." "This is insane."
Think: if Red Bull wrote news scripts.""",
}

SHORTS_SCRIPT_PROMPT = """
{system_prompt}

Write a YouTube Shorts video about today's real-time air quality data.
Make it feel urgent and visceral — bad air is a silent health crisis most people ignore.
Max 55 seconds. Max 130 words. Hook in first 3 words.

AQI Report: {title}
Data: {summary}
Narrator style: {style}

HOOK RULE: First sentence MUST contain the AQI number AND a shocking health comparison.
Example: "AQI 287. That's 13 cigarettes worth of air — in a single day."
NEVER start with "Today", "So", or "The air quality".

CIGARETTES RULE: Always convert the worst city's AQI to cigarettes-per-day (AQI ÷ 22 = cigarettes).
Include this comparison in the narration — it's the most shareable fact.

Return ONLY valid JSON (no markdown):
{{
  "youtube_title": "<punchy title under 55 chars — include city name + AQI number. e.g. 'Delhi AQI 287 — 13 Cigarettes a Day'>",
  "hook": "<first sentence, 12 words max — AQI number + cigarettes comparison>",
  "narration": "<STRICT max 130 words. Structure: AQI shock stat + cigarettes comparison → which cities are worst → health impact → what it means for you. Urgent, visceral, no filler.>",
  "title_variants": [
    "<variant 1 — health impact angle>",
    "<variant 2 — cigarettes comparison angle>",
    "<variant 3 — city name + number>",
    "<variant 4 — 'Is Your City Safe?' curiosity>"
  ],
  "characters": "no people, city skyline through smog, landmark silhouettes, pollution haze",
  "scenes": [
    {{
      "scene_number": 1,
      "narration_segment": "<words for this scene, ~30 words>",
      "storyboard_description": "<VERTICAL 9:16 portrait. Aerial or ground view of city through thick pollution haze. Dramatic smog atmosphere. Famous landmark barely visible through haze.>",
      "motion_effect": "<ken_burns_zoom_in|ken_burns_zoom_out|pan_left|pan_right>",
      "search_keywords": ["<city>", "air quality", "pollution"]
    }}
  ],
  "tags": ["<tag1>", "<tag2>", "<tag3>", "<tag4>", "<tag5>", "<tag6>", "<tag7>"],
  "description_hook": "<2 punchy lines — line 1: AQI number + cigarettes, line 2: which city is worst today>"
}}

Requirements:
- Exactly 4 scenes
- Total narration MUST be under 130 words
- MUST include the cigarettes-per-day comparison
- Tags must include: airquality, aqi, pollution, shorts, environment
"""

SCRIPT_PROMPT = """
{system_prompt}

Write a complete video package for this weird news story:

Title: {title}
Summary: {summary}
URL: {url}
Narrator style: {style}

Return ONLY valid JSON (no markdown):
{{
  "youtube_title": "<punchy title under 60 chars, style: {style}>",
  "hook": "<first 1-2 sentences that make viewer unable to stop watching>",
  "narration": "<full narration {word_count} words, {style} tone, structure: hook→setup→twist→climax→payoff>",
  "shorts_narration": "<30-45 second version, under 80 words, fast paced, hook first>",
  "title_variants": [
    "<title variant 1>",
    "<title variant 2>",
    "<title variant 3>",
    "<title variant 4>"
  ],
  "hook_variants": [
    "<opening hook variant 1>",
    "<opening hook variant 2>"
  ],
  "characters": "<visual description of 1-3 characters for consistent anime storyboard>",
  "scenes": [
    {{
      "scene_number": 1,
      "narration_segment": "<exact words spoken during this scene>",
      "storyboard_description": "<vivid cinematic description: action, angle, emotion, details>",
      "motion_effect": "<ken_burns_zoom_in|ken_burns_zoom_out|pan_left|pan_right|parallax>",
      "search_keywords": ["<keyword1>", "<keyword2>"]
    }}
  ],
  "shorts_scenes": [
    {{
      "scene_number": 1,
      "narration_segment": "<words for this shorts scene>",
      "storyboard_description": "<vertical 9:16 composition description>",
      "duration_seconds": 8
    }}
  ],
  "tags": ["<tag1>", "<tag2>", "<tag3>", "<tag4>", "<tag5>"],
  "description_hook": "<first 2 lines of YouTube description, makes people click show more>"
}}

Requirements:
- Exactly {num_scenes} scenes for main video
- Exactly 4 scenes for shorts version
- Each storyboard_description must be actionable for anime image generation
- Characters description must enable visual consistency across all scenes
- title_variants: 4 different angles (curiosity, ragebait, shock, humor)
"""

THUMBNAIL_PROMPT = """You are a YouTube thumbnail strategist.
Analyze this video and generate 4 thumbnail concepts that maximize CTR.

Video title: {title}
Hook: {hook}
Story summary: {summary}
Top performing scene for thumbnail: {top_scene}

For each thumbnail return:
- title_text: large bold text on thumbnail (max 4 words)
- subtitle_text: smaller text (max 5 words, optional)
- emotion: primary emotion to convey (shock/anger/curiosity/disgust/laughter)
- focal_subject: main visual element
- background_treatment: how to treat the background image
- color_scheme: primary/accent/text colors as hex
- ctr_rationale: why this would get clicks

Return ONLY valid JSON:
{{
  "thumbnails": [
    {{
      "variant": 1,
      "title_text": "...",
      "subtitle_text": "...",
      "emotion": "shock",
      "focal_subject": "...",
      "background_treatment": "...",
      "color_scheme": {{"primary": "#E50000", "accent": "#FFE600", "text": "#FFFFFF"}},
      "ctr_rationale": "..."
    }}
  ]
}}"""

FEEDBACK_PROMPT = """You are an AI content strategist analyzing performance data for "The Odd Investor" YouTube channel.

Recent video performance data:
{analytics_data}

Historical patterns:
{historical_summary}

Based on this data, provide specific, actionable improvements:
1. Which narrator style performs best?
2. What thumbnail patterns drive highest CTR?
3. What story types get best retention?
4. What title patterns drive most clicks?
5. What pacing works best for this audience?

Return ONLY valid JSON:
{{
  "best_style": "...",
  "style_reasoning": "...",
  "thumbnail_insights": ["insight1", "insight2", "insight3"],
  "title_patterns": ["pattern1", "pattern2"],
  "story_type_winners": ["type1", "type2"],
  "pacing_recommendation": "...",
  "prompt_improvements": {{
    "narration_tweak": "...",
    "thumbnail_tweak": "...",
    "title_tweak": "..."
  }},
  "next_content_focus": "..."
}}"""
