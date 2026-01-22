# scheduler.py
import asyncio
from services.subscription import check_subscriptions

async def subscription_scheduler(bot):
    while True:
        await check_subscriptions(bot)
        await asyncio.sleep(3600)  # проверка каждый час
