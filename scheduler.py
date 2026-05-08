"""
macOS launchd scheduler — installs/removes daily pipeline job.
"""

import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

PLIST_PATH   = os.path.expanduser("~/Library/LaunchAgents/com.breakingweird.v2.plist")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON       = sys.executable
LOG_PATH     = os.path.join(PROJECT_ROOT, "logs", "cron.log")

PLIST = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.breakingweird.v2</string>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON}</string>
        <string>{os.path.join(PROJECT_ROOT, 'main.py')}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{PROJECT_ROOT}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>6</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{LOG_PATH}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_PATH}</string>
    <key>RunAtLoad</key><false/>
    <key>KeepAlive</key><false/>
</dict>
</plist>"""


def manage_schedule(command: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    if command == "install":
        with open(PLIST_PATH, "w") as f:
            f.write(PLIST)
        subprocess.run(["launchctl", "load", PLIST_PATH])
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "breakingweird" in result.stdout:
            print(f"✓ Scheduled daily at 6:00am")
            print(f"  Plist: {PLIST_PATH}")
            print(f"  Logs:  {LOG_PATH}")
        else:
            print("⚠️  Install may have failed. Check: launchctl list | grep breakingweird")

    elif command == "remove":
        subprocess.run(["launchctl", "unload", PLIST_PATH], capture_output=True)
        if os.path.exists(PLIST_PATH):
            os.remove(PLIST_PATH)
        print("✓ Schedule removed")

    elif command == "status":
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "breakingweird.v2" in result.stdout:
            print("✓ Breaking Weird v2 is scheduled (daily at 6am)")
        else:
            print("✗ Not scheduled. Run: python main.py --schedule install")

    else:
        print("Usage: python main.py --schedule [install|remove|status]")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    manage_schedule(cmd)
