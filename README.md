# 🤖 Mister Assistant

A "Digital Twin" Telegram bot designed for high-performance tracking and intelligent life management. Built with a strict **Living Organism** architecture.

## 🚀 Core Features (MVP)

1.  **Smart Guard Security**:
    - The bot is locked to a single Telegram owner.
    - **First-come-first-served**: The first person to send `/start` becomes the permanent owner.
    - **Identity Recovery**: A 24-character Master Recovery Key is generated on first start. Use `/recover <KEY>` from a new account to take over your data.

2.  **Zero-Friction Activity Tracking**:
    - `starting <name>`: Instantly begins tracking a new activity.
    - `now <name>`: Switches current activity (ends previous, starts new).
    - `done`: Ends the current activity and provides a duration summary.
    - *Automatic Logic*: Detects flow states (90+ min sessions) and calculates durations.

3.  **Heuristic Spending Log**:
    - `spent <amount> on <category>`: Automatically logs your expenses to the SQLite vault.
    - *Example*: `spent 4500 on dinner`.

4.  **Daily Report**:
    - `summary` or `/summary`: Get a formatted report of everything you logged today (Activities & Spending).

## 🛠️ Setup Instructions (Windows)

1.  **Environment**: Ensure Python 3.10+ is installed.
2.  **Bot Token**: Create a `.env` file in the root directory:
    ```env
    BOT_TOKEN=your_telegram_bot_token_here
    DATABASE_URL=sqlite+aiosqlite:///data/mister_assistant.db
    ```
3.  **One-Click Start**: Double-click `start.bat`.
    - It will create a virtual environment, install dependencies, and run an architecture health check.

## 🧪 What to Test

As you use the bot, try these flows to verify the "Mister Assistant" experience:

1.  **Security Flow**:
    - Run `/start`. Save your **Master Recovery Key**.
    - Try to message the bot from a different Telegram account; it should ignore you.
2.  **Tracking Flow**:
    - Text: `starting coding`
    - Wait a minute.
    - Text: `now lunch` (Check if it tells you how long you coded).
    - Text: `done` (Check the final summary).
3.  **Financial Flow**:
    - Text: `spent 5000 on groceries`.
    - Text: `summary` (Check if it calculates the total).
4.  **Resilience**:
    - Restart the bot. Your data is saved in `data/mister_assistant.db`.

## 🏛️ Architecture & Rules

This project follows a strict **No-Mutant** policy:
- **Core**: Pure logic only.
- **Bot**: Telegram interface.
- **Data**: All DB access through the Repository.
- **200-Line Limit**: No file can exceed 200 lines.

Run `python scripts/architecture_inspector.py` to verify health.
