"""
Test the finance discovery engine.
Run: python test_discovery.py
"""
import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from storage.database import init_db
from discovery.engine import run_discovery

init_db()

print("\n" + "="*60)
print("THE ODD INVESTOR — Finance Discovery Engine Test")
print("="*60)

stories = run_discovery(limit_per_source=10)

print(f"\nTotal weird finance stories found: {len(stories)}")
print("="*60)

for i, s in enumerate(stories, 1):
    print(f"\n#{i} [{s['source']}] upvotes={s.get('upvotes', 0)}")
    print(f"  TITLE:   {s['title']}")
    print(f"  SUMMARY: {s['summary'][:120]}...")
    print(f"  URL:     {s['url'][:80]}")

print("\n" + "="*60)
print(f"Done. {len(stories)} stories ready for scoring.")
print("="*60)
