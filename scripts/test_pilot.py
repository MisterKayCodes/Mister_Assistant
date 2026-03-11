import asyncio
import sys
import os

# Mocking and path setup
sys.path.append(os.getcwd())

from services.nlu_service import nlu_service
from data.repository import repo

class TestPilot:
    """Simulates user interactions to test Mister Assistant's Brain."""

    TEST_CASES = [
        ("I want to go to the gym later today", "future"),
        ("What is the time?", "time"),
        ("I am coding", "present"),
        ("I'll exercise at 5pm", "future"),
        ("I finished lunch", "past"),
        ("Summary", "summary"),
        ("Cancel that", "cancel"),
        ("Random gibberish", "none"),
        ("Spent 2000 on food", "spent"),
        ("I spent 2000 naira on food", "spent"),
        ("I spent 2000 naira", "spent"),
        ("spent on dinner", "spent"),
        ("Remind me to gym in 10 minutes", "future"),
        ("Remind me to gym in 10 mins", "future"),
    ]

    async def run_diagnostics(self):
        print("--- Mister Assistant: Test Pilot Diagnostics --- \n")
        passed = 0
        total = len(self.TEST_CASES)

        for phrase, expected_intent in self.TEST_CASES:
            # 1. Check Custom Mappings (Learned memory)
            custom = await repo.get_custom_intent(phrase)
            
            # 2. Run NLU
            analysis = nlu_service.analyze(phrase)
            
            # Map legacy intent strings returned by fallback to new ML ones for testing purposes if needed
            ai_intent = analysis.intent
            if ai_intent == "log_spending": ai_intent = "spent"
            if ai_intent == "get_summary": ai_intent = "summary"
            if ai_intent == "start_activity": ai_intent = "present"
            if ai_intent == "end_activity": ai_intent = "past"
            
            actual_intent = custom if custom else ai_intent
            
            status = "PASS" if actual_intent == expected_intent else "FAIL"
            if status == "✅ PASS": passed += 1

            print(f"[{status}] Input: '{phrase}'")
            print(f"      Expected: {expected_intent} | Actual: {actual_intent}")
            if actual_intent != expected_intent:
                print(f"      Advice: Needs pattern adjustment in core/nlu.py or manual teaching.")
            print("-" * 40)

        print(f"\n📊 Diagnostic Complete: {passed}/{total} ({int(passed/total*100)}%)")
        if passed < total:
            print("[!] Weaknesses detected in intent resolution. Hardening required.")
        else:
            print("[+] Brain is sharp and synchronized.")

if __name__ == "__main__":
    pilot = TestPilot()
    asyncio.run(pilot.run_diagnostics())
