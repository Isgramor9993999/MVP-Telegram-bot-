from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from payments.yookassa import create_payment, check_payment_status

async def pay_command(message: types.Message) -> None:
    """Create a test YooKassa payment and return confirmation URL as an inline button."""
    amount = 1.00
    try:
        info = create_payment(amount, description=f"Bot payment for {message.from_user.id}", return_url="https://example.com/return")
        confirmation = info.get("confirmation")

        # Try several common shapes returned by the SDK
        url = None
        if isinstance(confirmation, dict):
            url = confirmation.get("confirmation_url") or confirmation.get("url") or (confirmation.get("confirmation") or {}).get("confirmation_url")
        else:
            url = getattr(confirmation, "confirmation_url", None) or getattr(confirmation, "url", None)

        if url:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Open payment", url=url)]])
            await message.answer(f"Пожалуйста, откройте ссылку для оплаты (сумма {amount} RUB):", reply_markup=kb)
            await message.answer(f"Payment id: {info.get('id')}")
        else:
            await message.answer(f"Платёж создан, но не удалось получить ссылку подтверждения. Статус: {info.get('status')}")
    except Exception as e:
        await message.answer(f"Ошибка при создании платежа: {e}")

async def check_command(message: types.Message) -> None:
    """Check payment status by id: /check <payment_id>"""
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("Использование: /check <payment_id>")
        return
    payment_id = parts[1]
    try:
        info = check_payment_status(payment_id)
        await message.answer(
            f"Payment {info.get('id')}\nstatus: {info.get('status')}\npaid: {info.get('paid')}\namount: {info.get('amount')} {info.get('currency')}"
        )
    except Exception as e:
        await message.answer(f"Ошибка при проверке статуса: {e}")

def register_payment_handlers(dp):
    dp.message.register(pay_command, Command("pay"))
    dp.message.register(check_command, Command("check"))