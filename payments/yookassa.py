# payments_yookassa.py
#Создаёт платёж YooKassa
#Обрабатывает webhook
#Уведомляет пользователя
#Даёт администратору статистику за день / месяц / всё время

import os
import uuid
from datetime import datetime, timedelta
from yookassa import Configuration, Payment
from aiogram import Router, Bot
from aiogram.types import Message
from sqlalchemy import select, func
from db import PaymentModel, async_session

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")

router = Router()

async def create_yookassa_payment(user_id: int, amount: int, description: str):
    payment = Payment.create({
        "amount": {"value": f"{amount}.00", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/your_bot"},
        "capture": True,
        "description": description,
        "metadata": {"user_id": user_id},
    }, uuid.uuid4())

    async with async_session() as session:
        session.add(PaymentModel(
            user_id=user_id,
            provider="yookassa",
            amount=amount,
            payment_id=payment.id,
            status="pending"
        ))
        await session.commit()

    return payment.confirmation.confirmation_url

async def process_yookassa_webhook(data: dict, bot: Bot):
    payment_id = data["object"]["id"]
    status = data["object"]["status"]

    if status != "succeeded":
        return

    async with async_session() as session:
        payment = await session.scalar(
            select(PaymentModel).where(PaymentModel.payment_id == payment_id)
        )
        payment.status = "success"
        await session.commit()

    await bot.send_message(
        payment.user_id,
        "✅ Оплата успешно получена. Услуга активирована."
    )

async def get_payments_stats(period: str):
    now = datetime.utcnow()
    delta = {
        "day": timedelta(days=1),
        "month": timedelta(days=30),
        "all": timedelta(days=3650)
    }[period]

    async with async_session() as session:
        result = await session.scalar(
            select(func.sum(PaymentModel.amount))
            .where(PaymentModel.created_at >= now - delta)
            .where(PaymentModel.status == "success")
        )
    return result or 0
