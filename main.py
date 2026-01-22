import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
from handlers import register_all_handlers
from states import BuyStates
from scheduler import subscription_scheduler
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
asyncio.create_task(subscription_scheduler())





async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()


    # register other handlers from project
    try:
        register_all_handlers(dp)
    except Exception:
        # it's okay if the project doesn't have additional handlers wired yet
        pass

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# main.py