from datetime import datetime, timedelta
from aiogram import F
from aiogram.types import CallbackQuery, Message
from storage import USERS
from models import User
from config import TRIAL_DAYS
from services.remnawave import RemnawaveService

remna = RemnawaveService()

def register_trial_handlers(dp):

    @dp.callback_query(F.data == "trial")
    async def trial(callback: CallbackQuery):
        user = USERS[callback.from_user.id]
        if user.is_trial_used:
            await callback.message.answer("Trial уже использован")
            return
        user.is_trial_used = True
        user.status = "trial"
        user.config = await remna.generate_trial_config(user.telegram_id)
        user.expires_at = datetime.utcnow() + timedelta(days=TRIAL_DAYS)
        await callback.message.answer(f"<code>{user.config}</code>\nДо: {user.expires_at}", parse_mode="HTML")

    @dp.message(F.text == "🎁 Trial")
    async def trial_reply(message: Message):
        await trial(
            CallbackQuery(
                id="trial_reply",
                from_user=message.from_user,
                chat_instance="reply",
                message=message,
                data="trial",
            )
        )
