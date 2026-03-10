import os
import re
import subprocess
import sys

# State file to keep track of last pushed commit message
STATE_FILE = ".git_sync_state"

def get_last_pushed():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return ""

def set_last_pushed(msg):
    with open(STATE_FILE, "w") as f:
        f.write(msg)

def get_latest_commit_message(tracking_file="docs/tracking.md"):
    if not os.path.exists(tracking_file):
        return None
    with open(tracking_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in reversed(lines):
        match = re.search(r'\|\s*`([^`]+)`\s*\|', line)
        if match:
            return match.group(1).strip()
    return None

def sync():
    msg = get_latest_commit_message()
    if not msg:
        return

    last_msg = get_last_pushed()
    if msg == last_msg:
        return # Already pushed this message

    # Check for actual changes
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout.strip()
    if not status:
        return

    print(f"[OK] New message detected: {msg}. Syncing...")
    subprocess.run("git add .", shell=True)
    subprocess.run(f'git commit -m "{msg}"', shell=True)
    subprocess.run("git push origin main", shell=True)
    set_last_pushed(msg)

if __name__ == "__main__":
    sync()
