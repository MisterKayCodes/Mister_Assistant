from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states import BotStates
from data.repository import repo
from core.personality import PersonalityEngine

from core.nlu import NLUEngine

router = Router()

VALID_INTENTS = ["start", "stop", "spent", "time", "summary", "future", "past"]

@router.message(lambda message: NLUEngine.analyze(message.text)["intent"] == "none")
async def handle_unknown(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_teach_intent)
    await state.update_data(phrase=message.text)
    await message.answer(PersonalityEngine.get_teach_me_response(message.text))

@router.message(BotStates.waiting_for_teach_intent)
async def process_teaching(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phrase = data.get("phrase")
    text = message.text.lower().strip()
    
    intent = None
    for valid in VALID_INTENTS:
        if f"means {valid}" in text or f"is {valid}" in text or text == valid:
            intent = valid
            break
    
    if not intent:
        await message.answer(
            f"🤨 Boss, I need to know the **intent** for '{phrase}'.\n"
            f"Please say something like: 'means {VALID_INTENTS[0]}' or just '{VALID_INTENTS[1]}'.\n"
            f"Valid options: {', '.join(VALID_INTENTS)}"
        )
        return

    await repo.add_custom_mapping(phrase, intent)
    await state.clear()
    await message.answer(PersonalityEngine.get_learned_response(phrase, intent))
