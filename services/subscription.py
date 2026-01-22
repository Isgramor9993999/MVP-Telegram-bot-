# services/subscription.py
from datetime import datetime, timedelta
from sqlalchemy import select
from db import async_session
from models import User

async def check_subscriptions(bot):
    now = datetime.utcnow()
    notify_time = now + timedelta(hours=24)

    async with async_session() as s:
        users = (await s.execute(
            select(User).where(User.is_active == True)
        )).scalars().all()

        for user in users:
            if not user.subscription_until:
                continue

            # Уведомление за 24 часа
            if (
                not user.notified_expiring
                and now < user.subscription_until <= notify_time
            ):
                await bot.send_message(
                    user.tg_id,
                    "⚠️ Подписка истекает через 24 часа.\n"
                    "Продлите её, чтобы не потерять доступ."
                )
                user.notified_expiring = True

            # Деактивация
            if user.subscription_until <= now:
                user.is_active = False
                user.config = None
                user.notified_expiring = False

        await s.commit()
