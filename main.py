import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import register_all_handlers
from aiogram.fsm.state import State, StatesGroup

class BuyStates(StatesGroup):
    waiting_for_payment = State()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    register_all_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
# main.py