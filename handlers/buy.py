from datetime import datetime, timedelta
from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from storage import USERS
from config import PAID_DAYS
from services.remnawave import RemnawaveService
from payments.dummy import DummyPaymentProvider
from states import BuyStates

payment_provider = DummyPaymentProvider()
remna = RemnawaveService()

def register_buy_handlers(dp):

    @dp.callback_query(F.data == "buy")
    async def buy(callback: CallbackQuery, state: FSMContext):
        pid = await payment_provider.create_payment(callback.from_user.id, 100)
        await state.update_data(payment_id=pid)
        await state.set_state(BuyStates.waiting_for_payment)
        await callback.message.answer(
            "Оплатите и нажмите кнопку",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]]
            ),
        )

    @dp.message(F.text == "💳 Купить")
    async def buy_reply(message: Message, state: FSMContext):
        await buy(
            CallbackQuery(
                id="buy_reply",
                from_user=message.from_user,
                chat_instance="reply",
                message=message,
                data="buy",
            ),
            state,
        )

    @dp.callback_query(F.data == "paid", BuyStates.waiting_for_payment)
    async def paid(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        if not await payment_provider.check_payment_status(data["payment_id"]):
            await callback.message.answer("Оплата не найдена")
            return
        user = USERS[callback.from_user.id]
        user.status = "paid"
        user.config = await remna.generate_paid_config(user.telegram_id)
        user.expires_at = datetime.utcnow() + timedelta(days=PAID_DAYS)
        await state.clear()
        await callback.message.answer(f"Оплата подтверждена\n<code>{user.config}</code>", parse_mode="HTML")
