# services/admin_dashboard.py
from sqlalchemy import select, func
from datetime import datetime, timedelta
from db import async_session
from models import User, Payment

async def get_admin_dashboard():
    now = datetime.utcnow()

    async with async_session() as s:
        total_users = await s.scalar(select(func.count(User.id)))
        active_users = await s.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        )

        income_day = await s.scalar(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
            .where(Payment.created_at >= now - timedelta(days=1))
        )

        income_month = await s.scalar(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
            .where(Payment.created_at >= now - timedelta(days=30))
        )

        income_all = await s.scalar(
            select(func.sum(Payment.amount))
            .where(Payment.status == "success")
        )

    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "income_day": income_day or 0,
        "income_month": income_month or 0,
        "income_all": income_all or 0,
    }
