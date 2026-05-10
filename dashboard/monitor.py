"""
CLI Dashboard — shows pipeline status, analytics, and feedback insights.
Run: python -m dashboard.monitor
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from storage.database import get_conn, get_recent_analytics
from workers.queue import queue_size


def _line(char="─", width=60):
    print(char * width)


def show_dashboard():
    _line("═")
    print(f"  THE ODD INVESTOR v2 — Dashboard  [{datetime.now().strftime('%Y-%m-%d %H:%M')}]")
    _line("═")

    # Queue
    print(f"\n  Queue: {queue_size()} jobs pending")

    # Recent runs
    conn = get_conn()
    runs = conn.execute(
        "SELECT * FROM runs ORDER BY started_at DESC LIMIT 10"
    ).fetchall()
    conn.close()

    print(f"\n  Recent Runs:")
    _line()
    if runs:
        for r in runs:
            status_icon = {"done": "✓", "running": "⟳", "failed": "✗"}.get(r["status"], "?")
            yt = r["youtube_url"] or "not uploaded"
            print(f"  {status_icon} [{r['run_id']}] {(r['story_title'] or '')[:45]}")
            print(f"    Style: {r['narrator_style'] or 'N/A'} | Score: {r['viral_score'] or 0:.1f} | {yt}")
    else:
        print("  No runs yet.")

    # Analytics
    print(f"\n  Recent Analytics:")
    _line()
    analytics = get_recent_analytics(5)
    if analytics:
        for a in analytics:
            print(
                f"  [{a['platform']}] {a['video_id']} | "
                f"Views: {a['views']:,} | "
                f"CTR: {a['ctr']*100:.2f}% | "
                f"Retention: {a['avg_retention']:.1f}%"
            )
    else:
        print("  No analytics collected yet.")

    # Feedback
    print(f"\n  Latest Feedback Insights:")
    _line()
    conn = get_conn()
    feedback = conn.execute(
        "SELECT * FROM feedback_log ORDER BY created_at DESC LIMIT 3"
    ).fetchall()
    conn.close()
    if feedback:
        for f in feedback:
            print(f"  [{f['applied_to']}] {(f['insight'] or '')[:80]}")
    else:
        print("  No feedback insights yet.")

    _line("═")


if __name__ == "__main__":
    import time
    refresh = "--watch" in sys.argv
    while True:
        os.system("clear")
        show_dashboard()
        if not refresh:
            break
        print("\n  Refreshing in 30s... (Ctrl+C to stop)")
        time.sleep(30)
