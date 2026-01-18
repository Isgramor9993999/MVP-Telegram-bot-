from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
