import re
from datetime import datetime
from aiogram import Router, F, types
from aiogram.filters import Command
from data.repository import repo
from core.activities import ActivityBrain
from services.event_bus import event_bus

router = Router()

@router.message(F.text.lower().startswith("starting "))
async def cmd_starting(message: types.Message):
    activity_name = message.text[9:].strip()
    if not activity_name:
        await message.answer("Starting what? (e.g., 'starting coding')")
        return

    # Check if there's already an active activity
    active = await repo.get_active_activity()
    if active:
        # If it's the same, ignore or notify
        if active.name.lower() == activity_name.lower():
            await message.answer(f"Already tracking '{active.name}'.")
            return
        
        # If different, treat as 'now'
        await _switch_activity(message, active, activity_name)
    else:
        await repo.start_activity(activity_name)
        await message.answer(f"⏱️ Tracking **{activity_name}** from {datetime.now().strftime('%H:%M')}")

@router.message(F.text.lower().startswith("now "))
async def cmd_now(message: types.Message):
    activity_name = message.text[4:].strip()
    active = await repo.get_active_activity()
    
    if active:
        await _switch_activity(message, active, activity_name)
    else:
        await repo.start_activity(activity_name)
        await message.answer(f"⏱️ Tracking **{activity_name}** from {datetime.now().strftime('%H:%M')}")

@router.message(F.text.lower() == "done")
async def cmd_done(message: types.Message):
    active = await repo.get_active_activity()
    if not active:
        await message.answer("Nothing is currently being tracked.")
        return

    now = datetime.now()
    duration = ActivityBrain.calculate_duration(active.start_time, now)
    
    # Simple context prompt (MVP: just closing it)
    await repo.end_activity(active.id, now, {})
    
    await message.answer(
        f"✅ Finished **{active.name}**.\n"
        f"⏱️ Duration: {duration} minutes.\n"
        f"Want to log a mood or breakthrough? (Or just starting something new?)"
    )

async def _switch_activity(message: types.Message, old_activity, new_name: str):
    now = datetime.now()
    duration = ActivityBrain.calculate_duration(old_activity.start_time, now)
    
    await repo.end_activity(old_activity.id, now, {})
    await repo.start_activity(new_name)
    
    await message.answer(
        f"🔄 '{old_activity.name}' was {duration}m.\n"
        f"⏱️ Now tracking **{new_name}** from {now.strftime('%H:%M')}"
    )

@router.message(F.text.lower().startswith("spent "))
async def cmd_spent(message: types.Message):
    data = ActivityBrain.parse_spending_input(message.text)
    if not data:
        await message.answer("Usage: 'spent 5000 on lunch'")
        return

    await repo.add_spending(data["amount"], data["category"])
    await message.answer(f"💸 Logged: ₦{data['amount']} -> **{data['category']}**.")

@router.message(F.text.lower().startswith("summary"))
@router.message(Command("summary"))
async def cmd_summary(message: types.Message):
    now = datetime.now()
    activities = await repo.get_daily_activities(now)
    spending = await repo.get_daily_spending(now)

    if not activities and not spending:
        await message.answer("Nothing logged for today yet, Boss.")
        return

    text = f"📊 **Daily Report: {now.strftime('%Y-%m-%d')}**\n\n"
    
    if activities:
        text += "📝 **Activities:**\n"
        for act in activities:
            duration = "..."
            if act.end_time:
                duration = f"{ActivityBrain.calculate_duration(act.start_time, act.end_time)}m"
            text += f"- {act.name}: {duration}\n"
    
    if spending:
        total = sum(s.amount for s in spending)
        text += f"\n💸 **Spending (Total: ₦{total}):**\n"
        for s in spending:
            text += f"- {s.category}: ₦{s.amount}\n"

    await message.answer(text)
