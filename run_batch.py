"""
Batch pipeline runner — runs the full pipeline N times sequentially,
uploading each video to YouTube Shorts.

Usage:
  python run_batch.py          # 10 videos (default)
  python run_batch.py 5        # 5 videos
  python run_batch.py --no-upload
"""

import os, sys, time, logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/batch.log", mode="a"),
    ],
)
logger = logging.getLogger("batch")

from pipeline.orchestrator import run_full_pipeline

def run_batch(n: int = 10, upload: bool = True):
    results = []
    failed  = 0

    print(f"\n{'='*60}")
    print(f"BATCH RUN — {n} videos | upload={upload}")
    print(f"{'='*60}\n")

    for i in range(1, n + 1):
        print(f"\n{'─'*60}")
        print(f"VIDEO {i}/{n}")
        print(f"{'─'*60}")
        try:
            result = run_full_pipeline(upload=upload)

            # Detect soft failures (no stories found, scoring failed, etc.)
            if "error" in result:
                failed += 1
                err = result["error"]
                logger.warning(f"Video {i} soft-failed: {err}")
                print(f"\n✗ Video {i} soft-failed: {err}")
                if err == "no_stories":
                    print("  Hint: all discovered stories already used — waiting 60s for fresh feed")
                    time.sleep(60)
                continue

            results.append(result)
            url = result.get("shorts_url") or result.get("youtube_url", "no url")
            score = result.get("viral_score", 0)
            title = result.get("title", "")
            print(f"\n✓ Video {i} done: {title[:60]}")
            print(f"  Score: {score:.1f}/10 | URL: {url}")

        except Exception as e:
            failed += 1
            logger.error(f"Video {i} failed: {e}")
            print(f"\n✗ Video {i} FAILED: {e}")
            time.sleep(30)

        if i < n:
            print(f"\nWaiting 15s before next video...")
            time.sleep(15)

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {len(results)} succeeded, {failed} failed")
    for r in results:
        url = r.get("shorts_url") or r.get("youtube_url", "")
        print(f"  [{r.get('viral_score',0):.1f}] {r.get('title','')[:55]} → {url}")
    print(f"{'='*60}\n")
    return results


if __name__ == "__main__":
    args  = sys.argv[1:]
    n     = 10
    upload = "--no-upload" not in args
    for a in args:
        if a.isdigit():
            n = int(a)
    run_batch(n=n, upload=upload)
