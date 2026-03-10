from aiogram import Router, types
from core.time_utils import get_now, format_time
from data.repository import repo

router = Router()

@router.message(lambda message: "summary" in message.text.lower() or "report" in message.text.lower())
async def cmd_summary(message: types.Message):
    await show_summary(message)

async def show_summary(message: types.Message):
    now = get_now()
    activities = await repo.get_daily_activities(now)
    text = f"📊 **Daily Report: {format_time(now)} (WAT)**\n\n"
    for act in activities:
        duration = f"{act.duration_minutes}m" if act.duration_minutes is not None else "..."
        text += f"- {act.name}: {duration}\n"
    
    # Financials
    spending = await repo.get_daily_spending(now)
    if spending:
        total = sum(s.amount for s in spending)
        text += f"\n💰 **Spending Total: {total:,.2f}**\n"
        for s in spending:
            text += f"- {s.category}: {s.amount:,.2f}\n"

    await message.answer(text)
