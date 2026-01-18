import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x}
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET = os.getenv("YOOKASSA_SECRET")
TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "1"))
PAID_DAYS = int(os.getenv("PAID_DAYS", "30"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
