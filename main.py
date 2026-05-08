"""
Breaking Weird v2 — Main Entry Point

Usage:
  python main.py                        # run full pipeline once
  python main.py --no-upload            # run without uploading
  python main.py --style horror_documentary
  python main.py --worker               # run as continuous queue worker
  python main.py --dashboard            # show dashboard
  python main.py --collect <video_id>   # collect analytics for a video
  python main.py --schedule install     # install daily launchd job
  python main.py --schedule remove      # remove daily launchd job
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/pipeline.log", mode="a"),
    ],
)

logger = logging.getLogger("main")


def main():
    args = sys.argv[1:]

    os.makedirs("logs", exist_ok=True)

    # Dashboard
    if "--dashboard" in args:
        from dashboard.monitor import show_dashboard
        watch = "--watch" in args
        import time
        while True:
            os.system("clear")
            show_dashboard()
            if not watch:
                break
            print("\nRefreshing in 30s... (Ctrl+C to stop)")
            time.sleep(30)
        return

    # Continuous worker
    if "--worker" in args:
        from workers.pipeline_worker import run_worker
        poll = 30.0
        for i, a in enumerate(args):
            if a == "--poll" and i + 1 < len(args):
                poll = float(args[i + 1])
        run_worker(poll_interval=poll)
        return

    # Analytics collection
    if "--collect" in args:
        idx = args.index("--collect")
        if idx + 1 >= len(args):
            print("Usage: --collect <video_id>")
            sys.exit(1)
        video_id = args[idx + 1]
        from analytics.collector import collect_and_store
        collect_and_store(run_id="manual", video_id=video_id, platform="youtube")
        return

    # Scheduler
    if "--schedule" in args:
        idx = args.index("--schedule")
        cmd = args[idx + 1] if idx + 1 < len(args) else "status"
        from scheduler import manage_schedule
        manage_schedule(cmd)
        return

    # Full pipeline
    upload = "--no-upload" not in args
    style  = None
    if "--style" in args:
        idx   = args.index("--style")
        style = args[idx + 1] if idx + 1 < len(args) else None

    from pipeline.orchestrator import run_full_pipeline
    result = run_full_pipeline(upload=upload, narrator_style=style)

    print("\n" + "="*60)
    print(f"Title:  {result.get('title', 'N/A')}")
    print(f"Score:  {result.get('viral_score', 0):.1f}/10")
    print(f"Style:  {result.get('style', 'N/A')}")
    if result.get("youtube_url"):
        print(f"YouTube: {result['youtube_url']}")
    if result.get("shorts_url"):
        print(f"Shorts:  {result['shorts_url']}")
    print("="*60)


if __name__ == "__main__":
    main()
