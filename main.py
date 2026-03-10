import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import settings
from bot.guard import SmartGuardMiddleware
from bot.routers import auth, activities

# Logging configuration
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Register Middleware
    dp.message.middleware(SmartGuardMiddleware())

    # Register Routers
    dp.include_router(auth.router)
    dp.include_router(activities.router)

    # Start polling
    logging.info("🤖 Mister Assistant is waking up...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🤖 Mister Assistant is going to sleep. Goodbye!")
