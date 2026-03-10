# 🤖 Mister Assistant - Activity Verification Script

import asyncio
from datetime import datetime, timedelta
from data.repository import repo
from core.activities import ActivityBrain

async def test_brain_logic():
    print("🧪 Testing Brain logic...")
    start = datetime.now() - timedelta(minutes=120)
    end = datetime.now()
    duration = ActivityBrain.calculate_duration(start, end)
    assert duration == 120
    
    is_flow = ActivityBrain.is_flow_session(duration, 0)
    assert is_flow is True
    
    from core.nlu import NLUEngine
    analysis = NLUEngine.analyze("spent 4500 on palm oil")
    assert analysis["intent"] == "spent"
    assert analysis["amount"] == 4500.0
    assert analysis["category"] == "Palm oil"
    print("✅ NLUEngine spending tests passed!")

async def test_repo_interaction():
    print("🧪 Testing Repository interactions...")
    # This assumes db is initialized
    try:
        activity = await repo.start_activity("test coding")
        assert activity.id is not None
        print(f"✅ Started activity: {activity.name}")
        
        active = await repo.get_active_activity()
        assert active.id == activity.id
        
        await repo.end_activity(activity.id, datetime.now(), {"is_flow": True})
        print("✅ Ended activity.")
    except Exception as e:
        print(f"❌ Repo test failed: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_brain_logic())
    # loop.run_until_complete(test_repo_interaction()) # Requires valid DB URL
