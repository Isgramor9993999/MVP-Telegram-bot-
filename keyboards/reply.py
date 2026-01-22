# keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплатить YooKassa")],
        [KeyboardButton(text="⭐ Оплатить Stars")],
    ],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Платежи за сутки")],
        [KeyboardButton(text="📊 Платежи за месяц")],
        [KeyboardButton(text="📊 Платежи за всё время")],
        [KeyboardButton(text="👥 Пользователи")],
    ],
    resize_keyboard=True
)
