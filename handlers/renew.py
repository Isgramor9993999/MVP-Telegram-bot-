# handlers/renew.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.ux import tariffs_kb

router = Router()

@router.callback_query(F.data == "renew_subscription")
async def renew_subscription(callback: CallbackQuery):
    await callback.message.answer(
        "🔄 Выберите тариф для продления:",
        reply_markup=tariffs_kb
    )
    await callback.answer()
