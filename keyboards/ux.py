# keyboards/ux.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Личный кабинет")],
        [KeyboardButton(text="💳 Купить подписку")],
    ],
    resize_keyboard=True
)

tariffs_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц — 500₽", callback_data="tariff_1m")],
        [InlineKeyboardButton(text="6 месяцев — 2500₽", callback_data="tariff_6m")],
        [InlineKeyboardButton(text="1 год — 4500₽", callback_data="tariff_1y")],
    ]
)
renew_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Продлить подписку", callback_data="renew_subscription")]
    ]
)