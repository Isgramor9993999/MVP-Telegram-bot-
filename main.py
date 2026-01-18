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
# IN-MEMORY STORAGE (DEMO)
# =========================

@dataclass
class User:
    telegram_id: int
    is_trial_used: bool = False
    status: Optional[str] = None  # trial | paid
    config: Optional[str] = None
    expires_at: Optional[datetime] = None


USERS: Dict[int, User] = {}
PAYMENT_LOGS: list[dict] = []

# =========================
# PAYMENT SYSTEM (ABSTRACTION)
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
        payment_id = f"payment_{user_id}_{int(datetime.utcnow().timestamp())}"
        PAYMENT_LOGS.append(
            {"payment_id": payment_id, "user_id": user_id, "amount": amount}
        )
        return payment_id

    async def check_payment_status(self, payment_id: str) -> bool:
        await asyncio.sleep(1)
        return True  # always successful (stub)

# =========================
# REMNAWAVE SERVICE (STUB)
# =========================

class RemnawaveService:
    async def generate_trial_config(self, user_id: int) -> str:
        return f"TRIAL-CONFIG-FOR-{user_id}"

    async def generate_paid_config(self, user_id: int) -> str:
        return f"PAID-CONFIG-FOR-{user_id}"

    async def revoke_config(self, config: str) -> None:
        return

# =========================
# FSM
# =========================

class BuyStates(StatesGroup):
    waiting_for_payment = State()

# =========================
# BOT SETUP
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

payment_provider = DummyPaymentProvider()
remna = RemnawaveService()

# =========================
# KEYBOARDS
# =========================

def main_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Trial", callback_data="trial")
    kb.button(text="💳 Купить", callback_data="buy")
    kb.adjust(2)
    return kb.as_markup()

def admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👥 Пользователи", callback_data="admin_users")
    kb.button(text="📜 Платежи", callback_data="admin_payments")
    kb.adjust(1)
    return kb.as_markup()

# =========================
# HANDLERS
# =========================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    USERS.setdefault(message.from_user.id, User(telegram_id=message.from_user.id))
    await message.answer(
        "Добро пожаловать.\nВыберите действие:",
        reply_markup=main_keyboard(),
    )

# -------- TRIAL --------

@dp.callback_query(F.data == "trial")
async def get_trial(callback: CallbackQuery):
    user = USERS[callback.from_user.id]

    if user.is_trial_used:
        await callback.message.answer("Trial уже был использован.")
        return

    config = await remna.generate_trial_config(user.telegram_id)

    user.is_trial_used = True
    user.status = "trial"
    user.config = config
    user.expires_at = datetime.utcnow() + timedelta(days=TRIAL_DAYS)

    await callback.message.answer(
        f"Ваш trial-конфиг:\n\n<code>{config}</code>\n\n"
        f"Действителен до: {user.expires_at}",
        parse_mode="HTML",
    )

# -------- BUY --------

@dp.callback_query(F.data == "buy")
async def buy(callback: CallbackQuery, state: FSMContext):
    payment_id = await payment_provider.create_payment(
        callback.from_user.id, amount=100
    )
    await state.update_data(payment_id=payment_id)
    await state.set_state(BuyStates.waiting_for_payment)

    await callback.message.answer(
        "Оплата создана.\nНажмите кнопку после оплаты.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]
            ]
        ),
    )

@dp.callback_query(F.data == "paid", BuyStates.waiting_for_payment)
async def check_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment_id = data["payment_id"]

    if not await payment_provider.check_payment_status(payment_id):
        await callback.message.answer("Оплата не найдена.")
        return

    user = USERS[callback.from_user.id]
    config = await remna.generate_paid_config(user.telegram_id)

    user.status = "paid"
    user.config = config
    user.expires_at = datetime.utcnow() + timedelta(days=PAID_DAYS)

    await state.clear()

    await callback.message.answer(
        f"Оплата подтверждена.\n\nВаш конфиг:\n<code>{config}</code>",
        parse_mode="HTML",
    )

# =========================
# ADMIN PANEL
# =========================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("Админ-панель:", reply_markup=admin_keyboard())

@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    text = "\n".join(
        f"{u.telegram_id} | {u.status}" for u in USERS.values()
    ) or "Пользователей нет"
    await callback.message.answer(text)

@dp.callback_query(F.data == "admin_payments")
async def admin_payments(callback: CallbackQuery):
    text = "\n".join(str(p) for p in PAYMENT_LOGS) or "Платежей нет"
    await callback.message.answer(text)

# =========================
# ENTRYPOINT
# =========================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
