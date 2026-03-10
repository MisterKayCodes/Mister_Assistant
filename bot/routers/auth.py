import secrets
import string
from aiogram import Router, types
from aiogram.filters import Command
from data.repository import repo

router = Router()

def generate_recovery_key(length: int = 24) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    existing_user = await repo.get_user_by_tg_id(user_id)
    
    if existing_user:
        await message.answer("Welcome back, Boss. I'm ready.")
        return

    # Registration logic (First user)
    recovery_key = generate_recovery_key()
    await repo.create_user(telegram_id=user_id, recovery_key=recovery_key)
    
    await message.answer(
        f"🤖 **Mister Assistant Initialized.**\n\n"
        f"You are now registered as my owner.\n"
        f"🗝️ **Master Recovery Key**: `{recovery_key}`\n\n"
        f"⚠️ *Save this key!* If you lose this account, you can use it to recover your data."
    )

@router.message(Command("recover"))
async def cmd_recover(message: types.Message, command: Command):
    if not command.args:
        await message.answer("Usage: `/recover <YOUR_KEY>`")
        return

    key = command.args.strip()
    success = await repo.recover_identity(key, message.from_user.id)
    
    if success:
        await message.answer("✅ **Identity Recovered.** All your data is now linked to this account.")
    else:
        await message.answer("❌ Invalid Recovery Key.")

