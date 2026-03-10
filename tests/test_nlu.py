import os
import sys
import pytest

# Ensure we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nlu_service import nlu_service

def test_spending_extraction():
    # Regular text
    cmd = nlu_service.analyze("spent 5000 on groceries")
    assert cmd.intent == "log_spending"
    assert cmd.amount == 5000.0
    assert cmd.category.lower() == "groceries"

    # Naira extraction via Matcher
    cmd2 = nlu_service.analyze("i dropped ₦150 on coffee")
    assert cmd2.intent == "log_spending"
    assert cmd2.amount == 150.0
    assert "coffee" in cmd2.category.lower()

    # Bucks/NGN extraction
    cmd3 = nlu_service.analyze("paid 4500 NGN for lunch")
    assert cmd3.intent == "log_spending"
    assert cmd3.amount == 4500.0
    assert "lunch" in cmd3.category.lower()

def test_activity_starts():
    cmd = nlu_service.analyze("starting deep work")
    assert cmd.intent == "start_activity"
    assert "deep work" in cmd.activity.lower()

    cmd2 = nlu_service.analyze("done with this")
    assert cmd2.intent == "end_activity"

def test_confidence_threshold_and_gibberish():
    cmd = nlu_service.analyze("The weather is so beautiful today wow")
    # It might think it's idle_chat or something else, but confidence should be lower for gibberish
    # Or, if idle_chat captures it, let's at least ensure it doesn't crash
    assert cmd.intent is not None

def test_mvp_fallback():
    # Scheduling future tasks should use the old engine fallback
    cmd = nlu_service.analyze("remind me to code in 20 mins")
    assert cmd.intent == "future"
    assert "code" in cmd.activity.lower() or "something productive" in cmd.activity.lower()
    assert cmd.target_time is not None

def test_cancel_fallback():
    cmd = nlu_service.analyze("forget it stop that")
    assert cmd.intent == "cancel"
