@echo off
setlocal

echo [!] Mister Assistant: One-Click Setup ^& Launch


:: Check if .venv exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created.
)

:: Activate venv
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate

:: Check for dependency changes
set "REQ_HASH_FILE=.venv\req_hash.txt"
set "CURRENT_REQ_FILE=requirements.txt"

for /f "tokens=*" %%a in ('certutil -hashfile %CURRENT_REQ_FILE% MD5 ^| find /v ":"') do set "NEW_HASH=%%a"

if exist "%REQ_HASH_FILE%" (
    set /p OLD_HASH=<"%REQ_HASH_FILE%"
) else (
    set "OLD_HASH=NONE"
)

if "%NEW_HASH%" neq "%OLD_HASH%" (
    echo 📥 Dependencies changed. Installing/Updating...
    pip install -r %CURRENT_REQ_FILE%
    echo %NEW_HASH% > "%REQ_HASH_FILE%"
) else (
    echo ✅ Dependencies up to date.
)

:: Run the project
echo 🚀 Launching...
python run.py

pause

