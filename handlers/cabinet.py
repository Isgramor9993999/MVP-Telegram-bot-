# handlers/cabinet.py (обновление)
from keyboards.ux import main_menu_kb, renew_kb
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from datetime import datetime
from db import async_session
from models import User
router = Router()

@router.message(F.text == "👤 Личный кабинет")
async def user_cabinet(message: Message):
    async with async_session() as s:
        user = await s.scalar(select(User).where(User.tg_id == message.from_user.id))

    if not user or not user.subscription_until:
        await message.answer(
            "📦 Подписка отсутствует.\nВыберите тариф для активации.",
            reply_markup=main_menu_kb
        )
        return

    now = datetime.utcnow()
    active = user.subscription_until > now
    status = "🟢 Активна" if active else "🔴 Истекла"

    text = (
        "👤 *Личный кабинет*\n\n"
        f"Статус: {status}\n"
        f"Действует до: {user.subscription_until:%d.%m.%Y}\n"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_kb
    )

    # кнопка продления
    await message.answer(
        "Хотите продлить подписку?",
        reply_markup=renew_kb
    )
