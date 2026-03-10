from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states import BotStates
import re
from data.repository import repo

router = Router()

@router.message(BotStates.waiting_for_spending_amount)
async def process_spending_amount(message: types.Message, state: FSMContext):
    text = message.text.strip()
    amount_match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not amount_match:
        await message.answer("Boss, I need a number for the amount. How much did you spend?")
        return
    
    amount = float(amount_match.group(1))
    data = await state.get_data()
    category = data.get("category")
    
    if not category:
        await state.update_data(amount=amount)
        await state.set_state(BotStates.waiting_for_spending_category)
        await message.answer(f"Got it: **{amount}**. Now, what did you spend it on?")
    else:
        await repo.add_spending(amount, category)
        await state.clear()
        await message.answer(f"✅ Logged: **{amount}** on **{category}**. Your wallet is a bit lighter, but your records are perfect!")

@router.message(BotStates.waiting_for_spending_category)
async def process_spending_category(message: types.Message, state: FSMContext):
    category = message.text.strip().capitalize()
    data = await state.get_data()
    amount = data.get("amount")
    
    if not amount:
        await state.update_data(category=category)
        await state.set_state(BotStates.waiting_for_spending_amount)
        await message.answer(f"Okay, **{category}**. And how much was that?")
    else:
        await repo.add_spending(amount, category)
        await state.clear()
        await message.answer(f"✅ Logged: **{amount}** on **{category}**. Tracked!")
