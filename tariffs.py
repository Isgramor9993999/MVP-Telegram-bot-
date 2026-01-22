# tariffs.py
from datetime import timedelta

TARIFFS = {
    "1m": {
        "title": "1 месяц",
        "days": 30,
        "price": 500,
    },
    "6m": {
        "title": "6 месяцев",
        "days": 180,
        "price": 2500,
    },
    "1y": {
        "title": "1 год",
        "days": 365,
        "price": 4500,
    },
}

def get_timedelta(tariff_key: str) -> timedelta:
    return timedelta(days=TARIFFS[tariff_key]["days"])
