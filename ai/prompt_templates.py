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

Write a YouTube Shorts video package for this weird financial news story.
CRITICAL: This is Shorts-only. Max 55 seconds. Max 130 words narration. Hook in first 3 words.

Title: {title}
Summary: {summary}
URL: {url}
Narrator style: {style}

Return ONLY valid JSON (no markdown):
{{
  "youtube_title": "<punchy title under 55 chars — curiosity gap, no clickbait>",
  "hook": "<first sentence, 10 words max, immediate hook>",
  "narration": "<STRICT max 130 words, {style} tone, structure: 1-sentence hook → 2-sentence setup → twist → 1-line payoff. Every word earns its place. No filler.>",
  "title_variants": [
    "<title variant 1 — curiosity>",
    "<title variant 2 — shock>",
    "<title variant 3 — humor>",
    "<title variant 4 — ragebait>"
  ],
  "characters": "<visual description of 1-2 key characters for consistent image generation, include age, clothing, expression>",
  "scenes": [
    {{
      "scene_number": 1,
      "narration_segment": "<exact words for this scene, ~30 words>",
      "storyboard_description": "<VERTICAL 9:16 portrait composition. Subject centered and tall in frame. Close-up or medium shot preferred. Financial news broadcast aesthetic. Describe: subject, action, background, lighting, emotion>",
      "motion_effect": "<ken_burns_zoom_in|ken_burns_zoom_out|pan_left|pan_right>",
      "search_keywords": ["<keyword1>", "<keyword2>"]
    }}
  ],
  "tags": ["<tag1>", "<tag2>", "<tag3>", "<tag4>", "<tag5>", "<tag6>", "<tag7>"],
  "description_hook": "<2 punchy lines for YouTube description>"
}}

Requirements:
- Exactly 4 scenes
- Total narration MUST be under 130 words — count carefully
- Each scene narration ~25-35 words
- storyboard_description must specify VERTICAL 9:16 portrait framing
- Tags must include: finance, money, shorts, investing, weirdnews
- Deadpan underreaction tone — let absurdity speak for itself
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

FEEDBACK_PROMPT = """You are an AI content strategist analyzing performance data for "Breaking Weird" YouTube channel.

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
