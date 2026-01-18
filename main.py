import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# =========================
# CONFIGURATION
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x}

TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "1"))
PAID_DAYS = int(os.getenv("PAID_DAYS", "30"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# =========================
# IN-MEMORY STORAGE
# =========================

@dataclass
class User:
    telegram_id: int
    is_trial_used: bool = False
    status: Optional[str] = None
    config: Optional[str] = None
    expires_at: Optional[datetime] = None
    menu_mode: str = "reply"  # reply | inline


USERS: Dict[int, User] = {}
PAYMENT_LOGS: list[dict] = []

# =========================
# PAYMENT
# =========================

class PaymentProvider(ABC):
    @abstractmethod
    async def create_payment(self, user_id: int, amount: int) -> str:
        pass

    @abstractmethod
    async def check_payment_status(self, payment_id: str) -> bool:
        pass


class DummyPaymentProvider(PaymentProvider):
    async def create_payment(self, user_id: int, amount: int) -> str:
        pid = f"payment_{user_id}_{int(datetime.utcnow().timestamp())}"
        PAYMENT_LOGS.append({"payment_id": pid, "user_id": user_id, "amount": amount})
        return pid

    async def check_payment_status(self, payment_id: str) -> bool:
        await asyncio.sleep(1)
        return True

# =========================
# SERVICE STUB
# =========================

class RemnawaveService:
    async def generate_trial_config(self, user_id: int) -> str:
        return f"TRIAL-CONFIG-{user_id}"

    async def generate_paid_config(self, user_id: int) -> str:
        return f"PAID-CONFIG-{user_id}"

# =========================
# FSM
# =========================

class BuyStates(StatesGroup):
    waiting_for_payment = State()

# =========================
# BOT
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

payment_provider = DummyPaymentProvider()
remna = RemnawaveService()

# =========================
# KEYBOARDS
# =========================

def inline_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Trial", callback_data="trial")
    kb.button(text="💳 Купить", callback_data="buy")
    kb.button(text="🔁 Reply меню", callback_data="reply_menu")
    kb.adjust(2, 1)
    return kb.as_markup()


def reply_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎁 Trial"),
                KeyboardButton(text="💳 Купить"),
            ],
            [
                KeyboardButton(text="ℹ️ Статус"),
                KeyboardButton(text="🔁 Inline меню"),
            ],
        ],
        resize_keyboard=True,
        persistent=True,
    )

# =========================
# COMMANDS
# =========================

@dp.message(Command("start"))
async def start(message: Message):
    USERS.setdefault(message.from_user.id, User(message.from_user.id))
    await message.answer("Главное меню:", reply_markup=reply_menu())


@dp.message(Command("menu"))
async def menu(message: Message):
    user = USERS.setdefault(message.from_user.id, User(message.from_user.id))

    if user.menu_mode == "reply":
        await message.answer("Меню:", reply_markup=reply_menu())
    else:
        await message.answer("Меню:", reply_markup=inline_menu())

# =========================
# MENU SWITCH
# =========================

@dp.message(F.text == "🔁 Inline меню")
async def to_inline(message: Message):
    user = USERS[message.from_user.id]
    user.menu_mode = "inline"

    await message.answer(
        "Переключено на inline-меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer("Выберите:", reply_markup=inline_menu())


@dp.callback_query(F.data == "reply_menu")
async def to_reply(callback: CallbackQuery):
    user = USERS[callback.from_user.id]
    user.menu_mode = "reply"

    await callback.message.answer(
        "Переключено на обычное меню",
        reply_markup=reply_menu(),
    )

# =========================
# TRIAL
# =========================

@dp.callback_query(F.data == "trial")
async def trial(callback: CallbackQuery):
    user = USERS[callback.from_user.id]

    if user.is_trial_used:
        await callback.message.answer("Trial уже использован")
        return

    user.is_trial_used = True
    user.status = "trial"
    user.config = await remna.generate_trial_config(user.telegram_id)
    user.expires_at = datetime.utcnow() + timedelta(days=TRIAL_DAYS)

    await callback.message.answer(
        f"<code>{user.config}</code>\nДо: {user.expires_at}",
        parse_mode="HTML",
    )


@dp.message(F.text == "🎁 Trial")
async def trial_reply(message: Message):
    await trial(
        CallbackQuery(
            id="trial_reply",
            from_user=message.from_user,
            chat_instance="reply",
            message=message,
            data="trial",
        )
    )

# =========================
# BUY
# =========================

@dp.callback_query(F.data == "buy")
async def buy(callback: CallbackQuery, state: FSMContext):
    pid = await payment_provider.create_payment(callback.from_user.id, 100)
    await state.update_data(payment_id=pid)
    await state.set_state(BuyStates.waiting_for_payment)

    await callback.message.answer(
        "Оплатите и нажмите кнопку",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]]
        ),
    )


@dp.message(F.text == "💳 Купить")
async def buy_reply(message: Message, state: FSMContext):
    await buy(
        CallbackQuery(
            id="buy_reply",
            from_user=message.from_user,
            chat_instance="reply",
            message=message,
            data="buy",
        ),
        state,
    )


@dp.callback_query(F.data == "paid", BuyStates.waiting_for_payment)
async def paid(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not await payment_provider.check_payment_status(data["payment_id"]):
        await callback.message.answer("Оплата не найдена")
        return

    user = USERS[callback.from_user.id]
    user.status = "paid"
    user.config = await remna.generate_paid_config(user.telegram_id)
    user.expires_at = datetime.utcnow() + timedelta(days=PAID_DAYS)

    await state.clear()

    await callback.message.answer(
        f"Оплата подтверждена\n<code>{user.config}</code>",
        parse_mode="HTML",
    )

# =========================
# STATUS
# =========================

@dp.message(F.text == "ℹ️ Статус")
async def status(message: Message):
    user = USERS.get(message.from_user.id)

    if not user or not user.status:
        await message.answer("Подписки нет")
        return

    await message.answer(f"{user.status} до {user.expires_at}")

# =========================
# ENTRYPOINT
# =========================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
