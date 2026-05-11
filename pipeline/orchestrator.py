"""
Air Quality Channel Pipeline Orchestrator.
discover (AQI API) → script → images (with AQI card) → voice → compose → thumbnails → publish
"""

import logging
from datetime import datetime

from discovery.aqi_source          import fetch_all_cities, build_daily_report
from rendering.visual_director     import generate_all_images
from rendering.caption_engine      import prepare_voiceover
from rendering.audio_engine        import get_music_track
from rendering.video_composer      import compose_shorts
from thumbnails.thumbnail_engine   import generate_thumbnails
from publishing.youtube_publisher  import publish_shorts
from storage.database              import init_db, save_run, update_run

logger = logging.getLogger(__name__)


def run_full_pipeline(upload: bool = True) -> dict:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info("=" * 60)
    logger.info(f"Air Quality Channel — run {run_id}")
    logger.info("=" * 60)

    init_db()

    # ── 1. Fetch live AQI data ────────────────────────────────────────────
    logger.info("Step 1: Fetching live AQI data for all cities...")
    cities = fetch_all_cities()
    if not cities:
        logger.error("No AQI data available. Aborting.")
        return {"error": "no_aqi_data"}

    # ── 2. Build daily report (story object) ─────────────────────────────
    logger.info("Step 2: Building daily report...")
    story = build_daily_report(cities)
    if not story:
        return {"error": "no_report"}

    logger.info(f"Today's worst: {story['worst_city']['city']} AQI {story['worst_city']['aqi']}")

    save_run(run_id,
             story_title=story["title"],
             narrator_style="documentary",
             viral_score=story.get("viral_score", 7.0),
             status="running")

    try:
        # ── 3. Generate images (skyline + AQI card overlay) ───────────────
        logger.info("Step 3: Generating city skyline images with AQI cards...")
        generate_all_images(story, run_id)

        # ── 4. Voiceover ──────────────────────────────────────────────────
        logger.info("Step 4: Generating voiceover...")
        audio_path, _, caption_chunks = prepare_voiceover(
            story["narration"], run_id, suffix="_shorts"
        )
        story["shorts_audio_path"]     = audio_path
        story["shorts_caption_chunks"] = caption_chunks

        # ── 5. Background music ───────────────────────────────────────────
        logger.info("Step 5: Getting background music...")
        music_path = get_music_track()

        # ── 6. Compose Shorts video ───────────────────────────────────────
        logger.info("Step 6: Composing Shorts video (9:16)...")
        compose_shorts(story, audio_path, music_path, run_id)

        # ── 7. Thumbnails ─────────────────────────────────────────────────
        logger.info("Step 7: Generating thumbnails...")
        generate_thumbnails(story, run_id)

        result = {
            "run_id":      run_id,
            "title":       story["youtube_title"],
            "viral_score": story.get("viral_score", 7.0),
            "worst_city":  story["worst_city"]["city"],
            "worst_aqi":   story["worst_city"]["aqi"],
        }

        # ── 8. Upload ─────────────────────────────────────────────────────
        if upload and story.get("shorts_path"):
            logger.info("Step 8: Uploading Shorts to YouTube...")
            yt_id = publish_shorts(story, run_id)
            if yt_id:
                result["shorts_url"]      = story.get("shorts_video_url")
                result["shorts_video_id"] = yt_id
                logger.info(f"Uploaded: {result['shorts_url']}")

        update_run(run_id,
                   shorts_url=result.get("shorts_url", ""),
                   finished_at=datetime.utcnow().isoformat(),
                   status="done")

        logger.info("=" * 60)
        logger.info(f"Pipeline complete: {run_id}")
        logger.info("=" * 60)
        return result

    except Exception as e:
        import traceback
        logger.error(f"Pipeline failed: {e}\n{traceback.format_exc()}")
        update_run(run_id, status="failed", error=str(e),
                   finished_at=datetime.utcnow().isoformat())
        raise
