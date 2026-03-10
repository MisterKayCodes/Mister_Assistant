import os
import re
import subprocess
import sys

def get_latest_commit_message(tracking_file="docs/tracking.md"):
    if not os.path.exists(tracking_file):
        return None

    with open(tracking_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Look for the last row in the table (excluding separators)
    # Pattern: | Task | Status | Started | Finished | `message` |
    for line in reversed(lines):
        match = re.search(r'\|\s*`([^`]+)`\s*\|', line)
        if match:
            return match.group(1).strip()
    
    return None

def run_command(cmd, silent=False):
    if not silent: print(f"[>>>] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        if not silent: print(f"[!] Error: {result.stderr}")
        return False
    if not silent: print(result.stdout)
    return True

def sync(silent=False, manual_fallback=True):
    # 1. Check status
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout.strip()
    if not status:
        if not silent: print("[+] No changes to sync.")
        return False

    # 2. Get message
    message = get_latest_commit_message()
    if not message:
        if not silent: print("[?] Could not find a commit message in docs/tracking.md.")
        if manual_fallback:
            message = input("[>>>] Enter manual commit message (or Ctrl+C to abort): ").strip()
        
        if not message:
            if not silent: print("[!] Aborted.")
            return False

    if not silent: print(f"[OK] Found message: {message}")

    # 3. Git flow
    if not run_command("git add .", silent): return False
    if not run_command(f'git commit -m "{message}"', silent): return False
    if not run_command("git push origin main", silent): return False

    if not silent: print("[+] Git Sync Complete!")
    return True

if __name__ == "__main__":
    try:
        sync()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(1)
