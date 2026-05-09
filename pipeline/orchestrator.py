"""
Full Pipeline Orchestrator.

discover → predict → script → images → voice → compose → thumbnails → publish → analytics → improve
"""

import logging
from datetime import datetime

from discovery.engine       import run_discovery
from prediction.viral_scorer import score_and_rank
from ai.narrative_generator  import generate_script
from rendering.visual_director import generate_all_images
from rendering.kling_engine    import generate_all_kling_videos
from rendering.caption_engine  import prepare_voiceover
from rendering.audio_engine    import get_music_track
from rendering.video_composer  import compose_main_video, compose_shorts
from thumbnails.thumbnail_engine import generate_thumbnails
from publishing.youtube_publisher import publish_main, publish_shorts
from publishing.platform_adapter  import publish_all_platforms
from analytics.collector          import collect_and_store
from analytics.feedback_loop      import analyze_and_improve, get_optimized_style
from storage.database             import init_db, save_story, mark_used, save_run, update_run
from config.settings              import STORIES_PER_RUN, SHORTS_ONLY

logger = logging.getLogger(__name__)


def run_full_pipeline(
    upload: bool = True,
    narrator_style: str = None,
    skip_tiktok: bool = True,
    skip_instagram: bool = True,
) -> dict:
    """
    Run the complete Breaking Weird v2 pipeline for one video.
    Returns a result dict with URLs and metrics.
    """
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"{'='*60}")
    logger.info(f"Breaking Weird v2 — Pipeline run: {run_id}")
    logger.info(f"{'='*60}")

    init_db()

    # ── 0. Feedback loop — learn from previous videos ─────────────────────
    logger.info("Step 0: Checking analytics feedback loop...")
    analyze_and_improve()
    style = narrator_style or get_optimized_style()
    logger.info(f"Using narrator style: {style}")

    # ── 1. Discover stories ───────────────────────────────────────────────
    logger.info("Step 1: Discovering stories...")
    stories = run_discovery(limit_per_source=15)
    if not stories:
        logger.error("No stories discovered. Aborting.")
        return {"error": "no_stories"}

    # ── 2. Predict virality ───────────────────────────────────────────────
    logger.info(f"Step 2: Scoring {len(stories)} stories for virality...")
    top_stories = score_and_rank(stories, top_n=STORIES_PER_RUN)
    if not top_stories:
        logger.error("No stories passed viral threshold. Aborting.")
        return {"error": "no_scored_stories"}

    story = top_stories[0]
    save_story(story)
    save_run(run_id,
             story_title=story["title"],
             narrator_style=style,
             viral_score=story.get("viral_score", 0),
             status="running")
    logger.info(f"Selected: [{story['viral_score']:.1f}/10] {story['title'][:80]}")

    try:
        # ── 3. Generate script ────────────────────────────────────────────
        logger.info(f"Step 3: Generating {style} script...")
        story = generate_script(story, style=style)

        # ── 4. Generate images + optional Kling video clips ──────────────
        logger.info("Step 4: Generating storyboard images...")
        generate_all_images(story, run_id)

        logger.info("Step 4b: Generating Kling AI video clips (if enabled)...")
        generate_all_kling_videos(story, run_id)

        # ── 5. Voiceover + captions ───────────────────────────────────────
        if SHORTS_ONLY:
            # Single audio track — narration IS the shorts narration
            logger.info("Step 5: Generating Shorts voiceover + captions...")
            s_audio, _, s_chunks = prepare_voiceover(story["narration"], run_id, suffix="_shorts")
            story["shorts_audio_path"]     = s_audio
            story["shorts_caption_chunks"] = s_chunks
            audio_path = s_audio
        else:
            logger.info("Step 5a: Generating main voiceover + captions...")
            audio_path, _, caption_chunks = prepare_voiceover(story["narration"], run_id)
            story["audio_path"]     = audio_path
            story["caption_chunks"] = caption_chunks

            shorts_narration = story.get("shorts_narration", "")
            if shorts_narration:
                logger.info("Step 5b: Generating Shorts voiceover...")
                s_audio, _, s_chunks = prepare_voiceover(shorts_narration, run_id, suffix="_shorts")
                story["shorts_audio_path"]     = s_audio
                story["shorts_caption_chunks"] = s_chunks

        # ── 6. Music ──────────────────────────────────────────────────────
        logger.info("Step 6: Getting background music...")
        music_path = get_music_track()

        # ── 7. Compose video ──────────────────────────────────────────────
        if SHORTS_ONLY:
            logger.info("Step 7: Composing Shorts video (portrait 9:16)...")
            compose_shorts(story, story["shorts_audio_path"], music_path, run_id)
        else:
            logger.info("Step 7: Composing main video...")
            compose_main_video(story, audio_path, music_path, run_id)
            if story.get("shorts_audio_path"):
                logger.info("Step 7b: Composing Shorts video...")
                compose_shorts(story, story["shorts_audio_path"], music_path, run_id)

        # ── 8. Thumbnails ─────────────────────────────────────────────────
        logger.info("Step 8: Generating & scoring 4 thumbnail variants...")
        generate_thumbnails(story, run_id)

        # ── 9. Publish ────────────────────────────────────────────────────
        result = {
            "run_id":      run_id,
            "title":       story.get("youtube_title", story["title"]),
            "viral_score": story.get("viral_score", 0),
            "style":       style,
        }

        if upload:
            if not SHORTS_ONLY:
                logger.info("Step 9a: Publishing main video to YouTube...")
                yt_id = publish_main(story, run_id)
                if yt_id:
                    result["youtube_url"]      = story.get("youtube_video_url")
                    result["youtube_video_id"] = yt_id

            if story.get("shorts_path"):
                logger.info("Step 9b: Publishing Shorts to YouTube...")
                yt_shorts_id = publish_shorts(story, run_id)
                if yt_shorts_id:
                    result["shorts_url"]      = story.get("shorts_video_url")
                    result["shorts_video_id"] = yt_shorts_id

            if not SHORTS_ONLY:
                logger.info("Step 9c: Publishing to other platforms...")
                platform_results = publish_all_platforms(
                    story, run_id,
                    skip_tiktok=skip_tiktok,
                    skip_instagram=skip_instagram,
                )
                result.update(platform_results)

            mark_used(story["url"])

            # ── 10. Analytics ──────────────────────────────────────────────
            vid_id = result.get("shorts_video_id") or result.get("youtube_video_id")
            if vid_id:
                logger.info("Step 10: Collecting baseline analytics...")
                collect_and_store(run_id, vid_id, "youtube")

        update_run(run_id,
                   youtube_url=result.get("youtube_url", ""),
                   shorts_url=result.get("shorts_url", ""),
                   finished_at=datetime.utcnow().isoformat(),
                   status="done")

        logger.info(f"{'='*60}")
        logger.info(f"Pipeline complete: {run_id}")
        if result.get("youtube_url"):
            logger.info(f"YouTube: {result['youtube_url']}")
        if result.get("shorts_url"):
            logger.info(f"Shorts:  {result['shorts_url']}")
        logger.info(f"{'='*60}")

        return result

    except Exception as e:
        import traceback
        logger.error(f"Pipeline failed: {e}\n{traceback.format_exc()}")
        update_run(run_id, status="failed", error=str(e),
                   finished_at=datetime.utcnow().isoformat())
        raise
