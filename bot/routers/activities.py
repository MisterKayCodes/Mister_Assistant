from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states import BotStates
import re
from datetime import datetime

from services.nlu_service import nlu_service
from core.personality import PersonalityEngine
from core.time_utils import get_now, format_time, get_time_query_response
from data.repository import repo
from services.scheduler import scheduler

router = Router()

@router.message(BotStates.waiting_for_time)
async def process_time_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    activity = data.get("activity", "something productive")
    
    # Analyze the new message for time
    analysis = nlu_service.analyze(message.text)
    target_time = analysis.target_time
    
    if not target_time:
        await message.answer(f"Boss, I still don't see a clear time in '{message.text}'. Try something like 'at 5pm' or 'in 20 mins'.")
        return

    # Transition to confirmation
    await state.set_state(BotStates.waiting_for_confirmation)
    await state.update_data(
        action="schedule",
        activity=activity,
        target_time=target_time.isoformat()
    )
    await message.answer(f"🤔 Just to be sure, Boss: You want me to schedule **{activity}** for {format_time(target_time)}? (Yes/No)")

@router.message(BotStates.waiting_for_confirmation)
async def wait_for_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = message.text.lower()
    action = data.get("action", "start")
    
    if any(k in text for k in ["yes", "start", "yeah", "sure", "do it"]):
        if action == "schedule":
            activity = data['activity']
            target_time = datetime.fromisoformat(data['target_time'])
            
            async def reminder_callback(type, tg_msg=message, act=activity, time_str=format_time(target_time)):
                if type == "warning":
                    await tg_msg.answer(PersonalityEngine.get_warning_response(act, time_str))
                else:
                    await tg_msg.answer(PersonalityEngine.get_start_future_response(act, time_str))

            await scheduler.schedule(message.from_user.id, target_time, reminder_callback)
            await state.clear()
            await message.answer(PersonalityEngine.get_future_response(activity, format_time(target_time)))
        else:
            await repo.start_activity(data['activity'])
            await state.clear()
            await message.answer(f"⏱️ Boom! Tracking **{data['activity']}** from {format_time()}. Let's go!")
    elif any(k in text for k in ["no", "cancel", "stop", "nevermind"]):
        await state.clear()
        await message.answer(PersonalityEngine.get_cancel_response())
    else:
        await message.answer("I need a 'yes' or 'no', Boss. Should I proceed?")

@router.message(lambda message: nlu_service.analyze(message.text).intent == "cancel")
async def handle_cancel(message: types.Message, state: FSMContext):
    num = scheduler.cancel_tasks(message.from_user.id)
    await state.clear()
    await message.answer(f"{PersonalityEngine.get_cancel_response()} (Cleared {num} reminders)")

@router.message(lambda message: nlu_service.analyze(message.text).intent == "future")
async def handle_future(message: types.Message, state: FSMContext):
    analysis = nlu_service.analyze(message.text)
    activity = analysis.activity
    target_time = analysis.target_time
    
    if not target_time:
        await state.set_state(BotStates.waiting_for_time)
        await state.update_data(activity=activity)
        await message.answer(f"Boss, you said you'll **{activity}**, but **when**? I need a time (e.g., 'at 2pm' or 'in 10 mins').")
        return
    
    await state.set_state(BotStates.waiting_for_confirmation)
    await state.update_data(
        action="schedule",
        activity=activity,
        target_time=target_time.isoformat()
    )
    await message.answer(f"🤔 Just to be sure, Boss: You want me to schedule **{activity}** for {format_time(target_time)}? (Yes/No)")

@router.message(lambda message: nlu_service.analyze(message.text).intent == "start_activity")
async def handle_start(message: types.Message, state: FSMContext):
    analysis = nlu_service.analyze(message.text)
    activity = analysis.activity
    active = await repo.get_active_activity()
    
    if active and active.name.lower() != activity.lower():
        now = get_now()
        duration = int((now - active.start_time).total_seconds() / 60)
        await repo.end_activity(active.id, now, {})
        await repo.start_activity(activity)
        intro = PersonalityEngine.get_activity_response(active.name, duration)
        await message.answer(f"{intro}\n\n⏱️ **Now tracking {activity}** from {format_time()}.")
    elif not active:
        await repo.start_activity(activity)
        await message.answer(f"⏱️ Got it! Tracking **{activity}** from {format_time()}.")
    else:
        await message.answer(f"Already tracking **{activity}**, Boss!")

@router.message(lambda message: nlu_service.analyze(message.text).intent == "end_activity")
async def handle_stop(message: types.Message):
    active = await repo.get_active_activity()
    if not active:
        await message.answer("Nothing is currently being tracked, Boss.")
        return
    now = get_now()
    duration = int((now - active.start_time).total_seconds() / 60)
    await repo.end_activity(active.id, now, {})
    await message.answer(PersonalityEngine.get_activity_response(active.name, duration))

@router.message(lambda message: nlu_service.analyze(message.text).intent == "past")
async def handle_past(message: types.Message):
    analysis = nlu_service.analyze(message.text)
    activity = analysis.activity
    now = get_now()
    start_time = now.replace(minute=now.minute - 30)
    activity_obj = await repo.start_activity(activity)
    activity_obj.start_time = start_time
    await repo.end_activity(activity_obj.id, now, {"duration_minutes": 30})
    await message.answer(f"✅ Logged **{activity}** as a 30m past session. I've got you covered!")

@router.message(lambda message: nlu_service.analyze(message.text).intent == "time")
async def handle_time(message: types.Message):
    await message.answer(get_time_query_response())
