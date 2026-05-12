#!/usr/bin/env python3
"""
Air Quality Channel — batch runner.
Usage:
    python run_batch.py           # run + upload
    python run_batch.py --no-upload   # run without uploading (preview)
"""

import os
import sys
import logging
import argparse

_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_DIR)   # ensure cron runs from the project root

os.makedirs(os.path.join(_DIR, "logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(_DIR, "logs", "aqi_pipeline.log")),
    ]
)

from pipeline.orchestrator import run_full_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-upload", action="store_true",
                        help="Run pipeline but skip YouTube upload")
    args = parser.parse_args()

    result = run_full_pipeline(upload=not args.no_upload)
    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    print("\n=== Air Quality Channel Run Complete ===")
    print(f"Worst city: {result.get('worst_city')} (AQI {result.get('worst_aqi')})")
    if result.get("shorts_url"):
        print(f"Shorts: {result['shorts_url']}")
    else:
        print("Upload skipped. Check output/shorts/ for the video file.")
