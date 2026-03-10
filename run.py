import os
import subprocess
import sys
import time

def run_inspector():
    print("🔍 Running Architecture Inspector...")
    result = subprocess.run([sys.executable, "scripts/architecture_inspector.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True

def start_bot():
    print("🚀 Starting Mister Assistant (Hot Reload Active)...")
    try:
        from watchfiles import run_process
        run_process("./", target="python main.py")
    except ImportError:
        print("📦 Installing watchfiles for hot-reload...")
        subprocess.run([sys.executable, "-m", "pip", "install", "watchfiles"])
        from watchfiles import run_process
        run_process("./", target="python main.py")

if __name__ == "__main__":
    if run_inspector():
        start_bot()
    else:
        print("🛑 Boot aborted due to architectural violations.")
        sys.exit(1)
