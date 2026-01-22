# handlers/payments_and_stats.py
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, func
from db import async_session
from models import Payment, User
from payments.yookassa import create_payment
from services.remnawave import generate_config
from config import ADMINS

router = Router()

# ---------- USER ----------

@router.message(F.text == "💳 Оплатить YooKassa")
async def yookassa_pay(message: Message):
    url = await create_payment(message.from_user.id, 500)
    await message.answer(f"Перейдите для оплаты:\n{url}")

@router.message(F.text == "⭐ Оплатить Stars")
async def stars_pay(message: Message):
    await message.answer("Оплата Stars вызывается через invoice.")

# ---------- ADMIN ----------

@router.message(F.text == "📊 Платежи за сутки")
async def stats_day(message: Message):
    if message.from_user.id not in ADMINS:
        return
    async with async_session() as s:
        total = await s.scalar(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
            .where(Payment.created_at >= func.now() - text("interval '1 day'"))
        )
    await message.answer(f"За сутки: {total or 0}")

@router.message(F.text == "📊 Платежи за месяц")
async def stats_month(message: Message):
    if message.from_user.id not in ADMINS:
        return
    async with async_session() as s:
        total = await s.scalar(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
            .where(Payment.created_at >= func.now() - text("interval '30 day'"))
        )
    await message.answer(f"За месяц: {total or 0}")

@router.message(F.text == "📊 Платежи за всё время")
async def stats_all(message: Message):
    if message.from_user.id not in ADMINS:
        return
    async with async_session() as s:
        total = await s.scalar(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
        )
    await message.answer(f"Всего: {total or 0}")

@router.message(F.text == "👥 Пользователи")
async def users_stats(message: Message):
    if message.from_user.id not in ADMINS:
        return
    async with async_session() as s:
        total = await s.scalar(select(func.count(User.id)))
        active = await s.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        )
    await message.answer(f"Всего: {total}\nАктивных: {active}")
