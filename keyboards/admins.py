# keyboards/admin.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Админ-дашборд")],
    ],
    resize_keyboard=True
)
