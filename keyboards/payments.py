# keyboards_payments.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Пользовательские кнопки
user_pay_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплатить через YooKassa")],
        [KeyboardButton(text="Оплатить через Stars")],
        [KeyboardButton(text="Пробный период")],
    ],
    resize_keyboard=True
)

# Админские кнопки статистики
admin_stats_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Статистика YooKassa День")],
        [KeyboardButton(text="Статистика YooKassa Месяц")],
        [KeyboardButton(text="Статистика YooKassa Всё")],
        [KeyboardButton(text="Статистика Stars")],
        [KeyboardButton(text="Пользователи Remnawave")],
    ],
    resize_keyboard=True
)
