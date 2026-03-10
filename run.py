import os
import subprocess
import sys
import threading
import re
import hashlib
from scripts.architecture_inspector import scan_organism
from scripts.git_sync import sync

def get_req_hash():
    """Returns MD5 hash of requirements.txt."""
    if not os.path.exists("requirements.txt"):
        return ""
    with open("requirements.txt", "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def check_dependencies():
    """Smart dependency check. Only installs if requirements.txt changed."""
    hash_file = ".venv/req_hash.txt"
    current_hash = get_req_hash()
    
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    if current_hash != old_hash:
        print("[...] Dependencies changed. Updating environment...")
        try:
            # Create .venv if it doesn't exist (though usually it should if sys.executable is inside it)
            os.makedirs(".venv", exist_ok=True)
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            with open(hash_file, "w") as f:
                f.write(current_hash)
            print("[+] Environment updated.")
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to update dependencies: {e}")
            return False
    return True

def run_inspector():
    print("[...] Running Architecture Inspector...")
    if not scan_organism("."):
        return False
    return True

def watch_docs():
    """Background thread to watch for changes in tracking.md."""
    try:
        from watchfiles import watch
        print("[LOG] Documentation Sync Watcher Active.")
        for changes in watch("docs/tracking.md"):
            print("\n[!] Change detected in docs/tracking.md. Attempting Git Sync...")
            sync(silent=False, manual_fallback=False)
    except Exception as e:
        print(f"[!] Doc Watcher Error: {e}")

def start_bot():
    print("[>>>] Starting Mister Assistant (Hot Reload Active)...")
    
    # Start the Doc Watcher
    threading.Thread(target=watch_docs, daemon=True).start()

    try:
        from watchfiles import run_process, DefaultFilter

        class BotFilter(DefaultFilter):
            def __call__(self, change, path):
                # Normalize path for regex
                path_str = path.replace("\\", "/")
                # Ignore specific patterns
                if any(re.search(p, path_str) for p in [
                    r"\.db$", r"\.sqlite$", r"docs/", 
                    r"personal/", r"\.git/", r"__pycache__/"
                ]):
                    return False
                return super().__call__(change, path)

        # WATCH ONLY CODE - Using watch_filter
        run_process("./", 
                    target=f"{sys.executable} main.py",
                    watch_filter=BotFilter())
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "watchfiles"])
        from watchfiles import run_process
        run_process("./", target=f"{sys.executable} main.py")

if __name__ == "__main__":
    if not check_dependencies():
        print("[!] Boot aborted: Dependency installation failed.")
        sys.exit(1)
        
    if run_inspector():
        start_bot()
    else:
        print("[!] Boot aborted due to architectural violations.")
        sys.exit(1)
