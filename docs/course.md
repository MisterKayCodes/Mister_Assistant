---

## 🟢 Level 1: The Foundation (Basics)

### 1.1 Python Basics & Pip
- **Concept**: Python is the "Engine" of your bot. 
- **Style**: We use **Python 3.10+** for modern features.
- **Used In**: Every `.py` file you see.
- **Library**: `pip` is the package manager. `requirements.txt` is our shopping list.
- **Developer Pattern**: **Virtual Environments (`.venv`)**. We keep our project dependencies isolated.

### 1.2 The Bot API (Aiogram)
- **Concept**: How the bot talks to Telegram.
- **Library**: `aiogram` (v3.x). 
- **Used In**: `main.py` (Initialization) and `bot/routers/` (Handling your talk).

---

## 🟡 Level 2: Data & Structure

### 2.1 The Repository Pattern (The Librarian)
- **Concept**: Don't let your bot talk to the database directly. Use a middleman.
- **File**: `data/repository.py`.
- **Used In**: `bot/routers/activities.py` calls `repo.start_activity()` instead of writing SQL.
- **Why?**: Decoupling makes the code interchangeable and clean.

### 2.2 SQLAlchemy (The Translator)
- **Concept**: Treating database tables like Python Classes.
- **Style**: **ORM (Object-Relational Mapping)**.
- **Used In**: `data/models.py`. Notice how `class Activity(Base)` looks like a real-world object.

---

## 🟠 Level 3: Advanced Automation

### 3.1 Middleware (The Smart Guard)
- **Concept**: A "Checkpost" that every message must pass through.
- **File**: `bot/guard.py`.
- **Used In**: `dp.message.middleware(SmartGuardMiddleware())` in `main.py`.

### 3.2 File Watchers (Hot Reload)
- **Concept**: Saving a file should restart the bot automatically.
- **Library**: `watchfiles`. Used in `run.py`.

---

## 🔴 Level 4: Conversational Intelligence

### 4.1 Natural Language Understanding (NLU)
- **Concept**: Converting "human chat" into "machine intent."
- **File**: `core/nlu.py`.
- **Used In**: `NLUEngine.analyze(message.text)` in `activities.py`.

### 4.2 Finite State Machines (FSM)
- **Concept**: A "Memory" for the conversation.
- **File**: `bot/states.py`.
- **Used In**: When you say "I will...", he enters the `waiting_for_confirmation` state to remember he's waiting for your 'Yes/No'.

---

## 💎 Level 5: Architecture & Scalability

### 5.1 The "Living Organism" Pattern
- **Rules**:
  1. No file can exceed 200 lines (Prevents "God Objects").
  2. No business logic in the bot layer.
- **Automation**: `scripts/architecture_inspector.py` checks these every time.

---

## 💎 Level 6: The Live Learner (Behavioral AI)

### 6.1 Interactive Learning Loops
- **Concept**: A bot that asks "What do you mean?" and remembers the answer.
- **Pattern**: **Intent Persistence**. 
- **Used In**: `repo.add_custom_mapping()` stores your unique phrases in the database.

### 6.2 Conversation Logging
- **Concept**: Tracking interactions for future pattern analysis.
- **Used In**: The very first line of `handle_message` in `activities.py` logs your chat.

---
*Last Updated: 2026-03-10 - Refactoring & Educational Hardening*
