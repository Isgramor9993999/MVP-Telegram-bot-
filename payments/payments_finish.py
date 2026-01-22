# handlers/payments_finish.py
from services.activate_subscription import activate_subscription
from services.remnawave import generate_config

async def on_payment_success(tg_id: int, tariff_key: str, bot):
    await activate_subscription(tg_id, tariff_key)

    config = await generate_config(tg_id)

    await bot.send_message(
        tg_id,
        "✅ Подписка активирована.\n"
        "Ваш конфиг:\n"
        f"{config}"
    )
