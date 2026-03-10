from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states import BotStates
import re
from datetime import datetime

from core.nlu import NLUEngine
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
    analysis = NLUEngine.analyze(message.text)
    target_time = analysis.get("target_time")
    
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

@router.message()
async def handle_message(message: types.Message, state: FSMContext):
    try:
        # LOG CONVERSATION (Learning Phase)
        await repo.log_conversation(message.text, None)

        # 0. Check Custom Mappings first
        custom_intent = await repo.get_custom_intent(message.text)
        
        # 1. NLU Analysis
        analysis = NLUEngine.analyze(message.text)
        intent = custom_intent if custom_intent else analysis["intent"]
        activity = analysis["activity"]
        target_time = analysis["target_time"]
        certainty = analysis.get("certainty", 1.0)

        # 1.5 Ambiguity Check
        if certainty < 0.5 and not custom_intent:
            intent = "none"

        # 2. Intent Handling
        elif intent == "time":
            await message.answer(get_time_query_response())
        elif intent == "present":
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
        elif intent == "none":
            # TRIGGER TEACH ME FLOW
            await state.set_state(BotStates.waiting_for_teach_intent)
            await state.update_data(phrase=message.text)
            await message.answer(PersonalityEngine.get_teach_me_response(message.text))
        else:
            # Fallback for unexpected intents
            await message.answer(PersonalityEngine.get_confused_response(message.text))

    except Exception as e:
        import traceback
        print(f"[!] Router Error: {traceback.format_exc()}")
        await message.answer(PersonalityEngine.get_error_response(str(e)))
