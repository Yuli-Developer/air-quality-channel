"""
Pipeline Worker — processes jobs from the queue.
Each job runs the full pipeline: discover → score → script → render → publish.
"""

import logging
import traceback
from workers.queue import dequeue, complete_job, fail_job, queue_size
from pipeline.orchestrator import run_full_pipeline

logger = logging.getLogger(__name__)


def process_one() -> bool:
    """Process one job from the queue. Returns True if a job was processed."""
    job = dequeue()
    if not job:
        return False

    job_id   = job["id"]
    job_type = job["type"]
    payload  = job.get("payload", {})

    logger.info(f"Processing job {job_id} [{job_type}]")

    try:
        if job_type == "full_pipeline":
            result = run_full_pipeline(
                upload=payload.get("upload", True),
                narrator_style=payload.get("narrator_style"),
                skip_tiktok=payload.get("skip_tiktok", True),
                skip_instagram=payload.get("skip_instagram", True),
            )
            complete_job(job_id, result=result)
            logger.info(f"Job {job_id} complete: {result.get('youtube_url', 'no upload')}")

        else:
            raise ValueError(f"Unknown job type: {job_type}")

    except Exception as e:
        error = traceback.format_exc()
        fail_job(job_id, error=error)
        logger.error(f"Job {job_id} failed: {e}")

    return True


def run_worker(poll_interval: float = 30.0):
    """
    Continuous worker loop — polls queue and processes jobs.
    Run this in a separate process for distributed rendering.
    """
    import time
    logger.info("Pipeline worker started")

    while True:
        processed = process_one()
        if not processed:
            remaining = queue_size()
            logger.debug(f"Queue empty ({remaining} jobs). Sleeping {poll_interval}s...")
            time.sleep(poll_interval)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    poll = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    run_worker(poll_interval=poll)
