from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states import BotStates
import re
from data.repository import repo

from services.nlu_service import nlu_service

router = Router()

@router.message(lambda message: nlu_service.analyze(message.text).intent == "log_spending")
async def handle_spending(message: types.Message, state: FSMContext):
    analysis = nlu_service.analyze(message.text)
    amount = analysis.amount
    category = analysis.category
    
    if not amount and not category:
        await state.set_state(BotStates.waiting_for_spending_amount)
        await message.answer("Boss, you mentioned spending. **How much** and **on what**?")
    elif not amount:
        await state.set_state(BotStates.waiting_for_spending_amount)
        await state.update_data(category=category)
        await message.answer(f"You spent money on **{category}**, but **how much**?")
    elif not category:
        await state.set_state(BotStates.waiting_for_spending_category)
        await state.update_data(amount=amount)
        await message.answer(f"You spent **{amount}**, but **on what**?")
    else:
        await repo.add_spending(amount, category)
        await message.answer(f"✅ Logged: **{amount}** on **{category}**. My records are updated.")

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
