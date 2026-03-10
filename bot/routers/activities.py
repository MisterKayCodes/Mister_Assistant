from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states import BotStates
import re

from core.nlu import NLUEngine
from core.personality import PersonalityEngine
from core.time_utils import get_now, format_time, get_time_query_response
from data.repository import repo
from services.scheduler import scheduler

router = Router()

@router.message(BotStates.waiting_for_teach_intent)
async def process_teaching(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phrase = data.get("phrase")
    text = message.text.lower().strip()
    
    # Heuristic: User says "means [intent]" or just "[intent]"
    intent_match = re.search(r"\b(means|signifies|is)\s+(\w+)", text)
    intent = intent_match.group(2) if intent_match else text.split()[-1]
    
    # Validate intent
    valid_intents = ["start", "stop", "spent", "time", "summary", "future", "past"]
    if intent not in valid_intents:
        await message.answer(f"Boss, '{intent}' isn't a valid intent. Try one of these: {', '.join(valid_intents)}")
        return

    await repo.add_custom_mapping(phrase, intent)
    await state.clear()
    await message.answer(PersonalityEngine.get_learned_response(phrase, intent))

@router.message(BotStates.waiting_for_confirmation)
async def wait_for_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = message.text.lower()
    
    if any(k in text for k in ["yes", "start", "yeah", "sure", "do it"]):
        await repo.start_activity(data['activity'])
        await state.clear()
        await message.answer(f"⏱️ Boom! Tracking **{data['activity']}** from {format_time()}. Let's go!")
    elif any(k in text for k in ["no", "cancel", "stop", "nevermind"]):
        await state.clear()
        await message.answer(PersonalityEngine.get_cancel_response())
    else:
        await message.answer("I need a 'yes' or 'no', Boss. Are we starting?")

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

        # 2. Intent Handling
        if intent == "cancel":
            num = scheduler.cancel_tasks(message.from_user.id)
            await state.clear()
            await message.answer(f"{PersonalityEngine.get_cancel_response()} (Cleared {num} reminders)")
            return

        if intent == "future":
            if not target_time:
                await message.answer("Boss, you said you'll do that... but **when**? I need a time (e.g., 'at 2pm' or 'in 10 mins').")
                return
            
            async def reminder_callback(type, tg_msg=message, act=activity, time_str=format_time(target_time)):
                if type == "warning":
                    await tg_msg.answer(PersonalityEngine.get_warning_response(act, time_str))
                else:
                    await tg_msg.answer(PersonalityEngine.get_start_future_response(act, time_str))

            await scheduler.schedule(message.from_user.id, target_time, reminder_callback)
            await message.answer(PersonalityEngine.get_future_response(activity, format_time(target_time)))

        elif intent == "start" or intent == "present":
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

        elif intent == "stop":
            active = await repo.get_active_activity()
            if not active:
                await message.answer("Nothing is currently being tracked, Boss.")
                return
            now = get_now()
            duration = int((now - active.start_time).total_seconds() / 60)
            await repo.end_activity(active.id, now, {})
            await message.answer(PersonalityEngine.get_activity_response(active.name, duration))

        elif intent == "past":
            now = get_now()
            start_time = now.replace(minute=now.minute - 30)
            activity_obj = await repo.start_activity(activity)
            activity_obj.start_time = start_time
            await repo.end_activity(activity_obj.id, now, {"duration_minutes": 30})
            await message.answer(f"✅ Logged **{activity}** as a 30m past session. I've got you covered!")

        elif intent == "time":
            await message.answer(get_time_query_response())
        elif intent == "summary":
            await _show_summary(message)
        else:
            # TRIGGER TEACH ME FLOW
            await state.set_state(BotStates.waiting_for_teach_intent)
            await state.update_data(phrase=message.text)
            await message.answer(PersonalityEngine.get_teach_me_response(message.text))

    except Exception as e:
        import traceback
        print(f"[!] Router Error: {traceback.format_exc()}")
        await message.answer(PersonalityEngine.get_error_response(str(e)))

async def _show_summary(message: types.Message):
    now = get_now()
    activities = await repo.get_daily_activities(now)
    text = f"📊 **Daily Report: {format_time(now)} (WAT)**\n\n"
    for act in activities:
        duration = f"{act.duration_minutes}m" if act.duration_minutes is not None else "..."
        text += f"- {act.name}: {duration}\n"
    await message.answer(text)
