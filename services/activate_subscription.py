# services/activate_subscription.py
from datetime import datetime
from sqlalchemy import select
from db import async_session
from models import User
from tariffs import get_timedelta

async def activate_subscription(tg_id: int, tariff_key: str):
    async with async_session() as s:
        user = await s.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(tg_id=tg_id)
            s.add(user)

        now = datetime.utcnow()

        # если подписка ещё активна — продлеваем
        if user.subscription_until and user.subscription_until > now:
            user.subscription_until += get_timedelta(tariff_key)
        else:
            user.subscription_until = now + get_timedelta(tariff_key)

        user.is_active = True
        user.notified_expiring = False

        await s.commit()
