from aiogram import Router, types
from core.parser import IntentEngine
from core.personality import PersonalityEngine
from core.time_utils import get_now, format_time, get_time_query_response
from data.repository import repo
from core.activities import ActivityBrain

router = Router()

@router.message()
async def handle_message(message: types.Message):
    try:
        # 1. Parse intent
        intent_data = IntentEngine.parse(message.text)
        
        if not intent_data:
            # Confusion 100 variations
            await message.answer(PersonalityEngine.get_confused_response(message.text))
            return

        intent = intent_data["intent"]

        # 2. Handle intents
        if intent == "start":
            activity_name = intent_data["activity"]
            active = await repo.get_active_activity()
            
            if active:
                if active.name.lower() == activity_name.lower():
                    await message.answer(f"Already tracking '{active.name}', Boss.")
                    return
                await _switch_activity(message, active, activity_name)
            else:
                await repo.start_activity(activity_name)
                await message.answer(f"⏱️ Got it! Tracking **{activity_name}** from {format_time()}. Let's kill it!")

        elif intent == "stop":
            active = await repo.get_active_activity()
            if not active:
                await message.answer("Nothing is currently being tracked, Boss.")
                return

            now = get_now()
            duration = int((now - active.start_time).total_seconds() / 60)
            await repo.end_activity(active.id, now, {})
            
            response = PersonalityEngine.get_activity_response(active.name, duration)
            await message.answer(response)

        elif intent == "spent":
            await repo.add_spending(intent_data["amount"], intent_data["category"])
            await message.answer(f"💸 Logged: ₦{intent_data['amount']} -> **{intent_data['category']}**. I'm keeping an eye on the bag!")

        elif intent == "time":
            await message.answer(get_time_query_response())

        elif intent == "summary":
            await _show_summary(message)

    except Exception as e:
        # SELF-AWARE ERROR HANDLING
        import traceback
        simplified_error = str(e)
        print(f"[!] INTERNAL ERROR: {traceback.format_exc()}")
        await message.answer(PersonalityEngine.get_error_response(simplified_error))

async def _switch_activity(message: types.Message, old_activity, new_name: str):
    now = get_now()
    duration = int((now - old_activity.start_time).total_seconds() / 60)
    
    await repo.end_activity(old_activity.id, now, {})
    await repo.start_activity(new_name)
    
    intro = PersonalityEngine.get_activity_response(old_activity.name, duration)
    await message.answer(f"{intro}\n\n⏱️ **Now tracking {new_name}** from {format_time()}. Keep the momentum!")

async def _show_summary(message: types.Message):
    now = get_now()
    activities = await repo.get_daily_activities(now)
    spending = await repo.get_daily_spending(now)

    if not activities and not spending:
        await message.answer("The vault is empty for today, Boss. Let's start something!")
        return

    text = f"📊 **Daily Report: {now.strftime('%Y-%m-%d')} (WAT)**\n\n"
    
    if activities:
        text += "📝 **Activities:**\n"
        for act in activities:
            duration = f"{act.duration_minutes}m" if act.duration_minutes is not None else "..."
            text += f"- {act.name}: {duration}\n"
    
    if spending:
        total = sum(s.amount for s in spending)
        text += f"\n💸 **Spending (Total: ₦{total}):**\n"
        for s in spending:
            text += f"- {s.category}: ₦{s.amount}\n"

    await message.answer(text)
