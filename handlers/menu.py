from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards import inline_menu, reply_menu
from storage import USERS
from models import User

def register_menu_handlers(dp):

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

    @dp.message(F.text == "🔁 Inline меню")
    async def to_inline(message: Message):
        user = USERS[message.from_user.id]
        user.menu_mode = "inline"
        await message.answer("Переключено на inline-меню", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите:", reply_markup=inline_menu())

    @dp.callback_query(F.data == "reply_menu")
    async def to_reply(callback: CallbackQuery):
        user = USERS[callback.from_user.id]
        user.menu_mode = "reply"
        await callback.message.answer("Переключено на обычное меню", reply_markup=reply_menu())
