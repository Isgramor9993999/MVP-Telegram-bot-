import asyncio
from datetime import datetime

PAYMENT_LOGS = []  # хранение всех платежей (stub)

class PaymentProvider:
    async def create_payment(self, user_id: int, amount: int) -> str:
        raise NotImplementedError

    async def check_payment_status(self, payment_id: str) -> bool:
        raise NotImplementedError

class DummyPaymentProvider(PaymentProvider):
    async def create_payment(self, user_id: int, amount: int) -> str:
        payment_id = f"payment_{user_id}_{int(datetime.utcnow().timestamp())}"
        PAYMENT_LOGS.append({"payment_id": payment_id, "user_id": user_id, "amount": amount})
        return payment_id

    async def check_payment_status(self, payment_id: str) -> bool:
        await asyncio.sleep(0.1)
        return True  # всегда успешно
