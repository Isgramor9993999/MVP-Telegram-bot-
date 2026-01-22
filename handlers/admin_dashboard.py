# handlers/admin_dashboard.py
from aiogram import Router, F
from aiogram.types import Message
from services.admin_dashboard import get_admin_dashboard
import os
ADMIDS = os.getenv("ADMIN_IDS")
router = Router()

@router.message(F.text == "📊 Админ-дашборд")
async def admin_dashboard(message: Message):
    if message.from_user.id not in ADMIDS:
        return

    data = await get_admin_dashboard()

    text = (
        "📊 *Админ-дашборд*\n\n"
        f"👥 Пользователи:\n"
        f"— Всего: {data['total_users']}\n"
        f"— Активных: {data['active_users']}\n\n"
        f"💰 Доход:\n"
        f"— За сутки: {data['income_day']} ₽\n"
        f"— За месяц: {data['income_month']} ₽\n"
        f"— За всё время: {data['income_all']} ₽"
    )

    await message.answer(text, parse_mode="Markdown")
