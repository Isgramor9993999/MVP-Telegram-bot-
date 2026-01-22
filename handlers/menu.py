from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.payments import user_pay_kb, admin_stats_kb
from keyboards import inline_menu, reply_menu
from storage import USERS
from models import User
import os
ADMIDS = os.getenv("ADMIN_IDS")
def register_menu_handlers(dp):

    @dp.message(commands=["start"])
    async def cmd_start(message: Message):
        if message.from_user.id in ADMIDS:  # ADMINS — список ID администраторов
            await message.answer("Вы администратор. Выберите действие:", reply_markup=admin_stats_kb)
        else:
            await message.answer("Выберите оплату:", reply_markup=user_pay_kb)

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
