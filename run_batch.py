#!/usr/bin/env python3
"""
Air Quality Channel — batch runner.
Usage:
    python run_batch.py           # run + upload
    python run_batch.py --no-upload   # run without uploading (preview)
"""

import os
import sys
import time
import logging
import fcntl
import argparse

_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_DIR)   # ensure cron runs from the project root
os.makedirs(os.path.join(_DIR, "logs"), exist_ok=True)

# Prevent concurrent runs
_LOCK_FILE = open(os.path.join(_DIR, ".batch.lock"), "w")
try:
    fcntl.flock(_LOCK_FILE, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("air-quality-channel: another job is already running — exiting.")
    sys.exit(0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(_DIR, "logs", "aqi_pipeline.log")),
    ]
)
logger = logging.getLogger("batch")

from pipeline.orchestrator import run_full_pipeline


def _run_with_retry(upload: bool, max_retries: int = 3) -> dict:
    delays = [60, 120, 180]
    for attempt in range(max_retries + 1):
        try:
            return run_full_pipeline(upload=upload)
        except Exception as e:
            is_transient = any(x in str(e) for x in ("503", "UNAVAILABLE", "429", "Resource has been exhausted"))
            if attempt < max_retries and is_transient:
                wait = delays[min(attempt, len(delays) - 1)]
                logger.warning(f"Transient API error (attempt {attempt + 1}/{max_retries}), retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-upload", action="store_true",
                        help="Run pipeline but skip YouTube upload")
    args = parser.parse_args()

    result = _run_with_retry(upload=not args.no_upload)
    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    print("\n=== Air Quality Channel Run Complete ===")
    print(f"Worst city: {result.get('worst_city')} (AQI {result.get('worst_aqi')})")
    if result.get("shorts_url"):
        print(f"Shorts: {result['shorts_url']}")
    else:
        print("Upload skipped. Check output/shorts/ for the video file.")
