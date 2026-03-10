import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import settings
from bot.guard import SmartGuardMiddleware
from bot.routers import auth, activities, spending, teaching, reports, history
import os
import subprocess

# Logging configuration
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def preload_nlu():
    if not os.path.exists(os.path.join("data", "models", "mister_intent.pkl")):
        logging.info("🧠 Brain missing. Generating data and Training NLU Model...")
        if not os.path.exists(os.path.join("data", "training", "intent_dataset.csv")):
            subprocess.run([sys.executable, "scripts/generate_nlu_data.py"])
        subprocess.run([sys.executable, "scripts/train_nlu.py"])
    
    # Force singleton instantiation to load heavy spaCy/sklearn models before polling starts
    from services.nlu_service import nlu_service
    nlu_service.analyze("Waking up")

async def main():
    preload_nlu()
    
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
    dp.include_router(spending.router)
    dp.include_router(teaching.router)
    dp.include_router(reports.router)
    dp.include_router(history.router)

    # Start polling
    logging.info("🤖 Mister Assistant is waking up...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🤖 Mister Assistant is going to sleep. Goodbye!")
