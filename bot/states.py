from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    waiting_for_confirmation = State()
    waiting_for_future_start = State()
    waiting_for_teach_intent = State()
