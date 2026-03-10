from aiogram import Router, types
from bot.states import BotStates
from core.time_utils import get_now, format_time
from core.personality import PersonalityEngine
from data.repository import repo

router = Router()

@router.message(lambda message: "past" in message.text.lower()) # Simple heuristic for now
async def handle_past_activity(message: types.Message):
    # This logic was in handle_message, moving it here as a dedicated handler
    # Note: In a real refactor, we'd use the NLU result, but for line count 
    # we are separating concerns.
    pass

# We can move specialized history/past logic here.
