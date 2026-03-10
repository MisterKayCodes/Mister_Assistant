from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from data.repository import repo
from config import settings

class SmartGuardMiddleware(BaseMiddleware):
    """
    The Guard (Security).
    Only allows the registered owner to interact with the bot.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        owner = await repo.get_user_by_tg_id(user_id)

        # If no owner exists yet, allow the first user (First-come-first-served setup)
        # or check against a pre-configured ID if available.
        all_users = await repo.get_user_by_tg_id(user_id) # This is a placeholder for a 'get_any_user' check
        
        # Logic: If DB is empty, the first one to /start becomes owner.
        # If DB has owner, only that owner can pass.
        
        # Simplified for MVP:
        registered_owner = await repo.get_user_by_tg_id(user_id)
        if registered_owner or await repo.is_vault_empty():
            return await handler(event, data)

        # Ignore everyone else but log it
        import logging
        logging.info(f"🛡️ SmartGuard: Ignored message from unauthorized user {user_id}")
        return

