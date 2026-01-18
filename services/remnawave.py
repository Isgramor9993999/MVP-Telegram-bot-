# services/remnawave.py

class RemnawaveService:
    async def generate_trial_config(self, user_id: int) -> str:
        return f"TRIAL-CONFIG-{user_id}"

    async def generate_paid_config(self, user_id: int) -> str:
        return f"PAID-CONFIG-{user_id}"

    async def revoke_config(self, config: str) -> None:
        """Stub: отключить конфиг"""
        return
