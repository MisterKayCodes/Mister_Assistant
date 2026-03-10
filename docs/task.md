# 🎯 Mister Assistant MVP Tasks

This is the roadmap for the Minimum Viable Product. Each task is designed to be small and verifiable.

## Phase 1: Infrastructure & Skeleton
- [x] Task 1.1: Initialize Folder Structure (Core, Services, Bot, Data, Utils).
- [x] Task 1.2: Setup `config.py` with Pydantic Settings.
- [ ] Task 1.3: Initialize Alembic and create initial SQLite migrations.
- [x] Task 1.4: Define `Models` (User, Activity, Spending, Context).



## Phase 2: The Mouth & The Guard (Security)
- [ ] Task 2.1: Implement `SmartGuardMiddleware` for User ID locking.
- [ ] Task 2.2: Implement `/start` and Owner Registration logic.
- [ ] Task 2.3: Implement **Recovery Key** generation and `/recover` handler.

## Phase 3: Core Activity Tracking
- [ ] Task 3.1: Implement "starting <activity>" parser and logic (Brain -> Repo).
- [ ] Task 3.2: Implement "now <activity>" (Stop current, start new).
- [ ] Task 3.3: Implement "done" (Stop current, show duration).
- [ ] Task 3.4: Add context prompts (🍽️ Eaten?, ⚡ Power?).

## Phase 4: Basic Spending
- [ ] Task 4.1: Implement "spent <amount> on <category>" parser.
- [ ] Task 4.2: Data persistence for spending logs.

## Phase 5: MVP Review & Summary
- [ ] Task 5.1: Create "Daily Summary" logic (Aggregation).
- [ ] Task 5.2: Final verification of architectural rules (Zero Mutants).
