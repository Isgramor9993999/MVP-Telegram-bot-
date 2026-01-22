# handlers/tariffs.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.ux import tariffs_kb
from tariffs import TARIFFS
from payments.yookassa import create_payment

router = Router()

@router.message(F.text == "💳 Купить подписку")
async def choose_tariff(message: Message):
    await message.answer(
        "📦 Выберите тариф:",
        reply_markup=tariffs_kb
    )

@router.callback_query(F.data.startswith("tariff_"))
async def tariff_selected(callback: CallbackQuery):
    tariff_key = callback.data.replace("tariff_", "")
    tariff = TARIFFS[tariff_key]

    pay_url = await create_payment(
        user_id=callback.from_user.id,
        amount=tariff["price"],
        tariff_key=tariff_key
    )

    await callback.message.answer(
        f"Вы выбрали: *{tariff['title']}*\n"
        f"Сумма: {tariff['price']}₽\n\n"
        f"Перейдите для оплаты:\n{pay_url}",
        parse_mode="Markdown"
    )
    await callback.answer()
