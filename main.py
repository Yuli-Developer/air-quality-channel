#!/usr/bin/env python3
"""Air Quality Channel — entry point."""
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/aqi_pipeline.log"),
    ]
)

from pipeline.orchestrator import run_full_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Air Quality Channel pipeline")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()
    result = run_full_pipeline(upload=not args.no_upload)
    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    print(f"\nDone! Worst city today: {result.get('worst_city')} AQI {result.get('worst_aqi')}")
    if result.get("shorts_url"):
        print(f"Shorts: {result['shorts_url']}")
