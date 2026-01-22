# payments_telegram_stars.py
#Принимает оплату через Telegram Stars
#Сохраняет платёж
#Уведомляет пользователя
#Даёт агрегированную статистику

from aiogram import Router
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from sqlalchemy import select, func
from db import PaymentModel, async_session

router = Router()

@router.message(commands=["buy_stars"])
async def send_stars_invoice(message: Message):
    await message.answer_invoice(
        title="Покупка услуги",
        description="Доступ к сервису",
        payload="stars_payment",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Услуга", amount=100)]
    )

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(content_types=["successful_payment"])
async def stars_success(message: Message):
    async with async_session() as session:
        session.add(PaymentModel(
            user_id=message.from_user.id,
            provider="telegram_stars",
            amount=message.successful_payment.total_amount,
            payment_id=message.successful_payment.telegram_payment_charge_id,
            status="success"
        ))
        await session.commit()

    await message.answer("✅ Оплата через Telegram Stars прошла успешно.")

async def stars_stats(period: str):
    async with async_session() as session:
        result = await session.scalar(
            select(func.sum(PaymentModel.amount))
            .where(PaymentModel.provider == "telegram_stars")
            .where(PaymentModel.status == "success")
        )
    return result or 0
