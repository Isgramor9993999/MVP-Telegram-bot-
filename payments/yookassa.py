"""YooKassa payment adapter (sandbox/test-ready).

This module provides a small wrapper around the `yookassa` SDK to create
and check test payments. Credentials are read from environment variables
so no secrets are stored in code. Example variables (place in `.env`):

YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET=your_secret_key

Notes:
 - Use YooKassa test credentials (sandbox) for testing payments.
 - The `create_payment` function returns a dict containing payment id,
   status and confirmation information (if available).
"""

from __future__ import annotations

import os
from typing import Dict, Optional

from dotenv import load_dotenv
from yookassa import Configuration, Payment


# Load environment variables from .env if present
load_dotenv()

# Read credentials from env (do NOT hardcode secrets)
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET = os.getenv("YOOKASSA_SECRET")

if not (YOOKASSA_SHOP_ID and YOOKASSA_SECRET):
    # We don't raise here because in some contexts user may only import the module.
    # Functions will raise if credentials are missing at call time.
    Configuration.account_id = None
    Configuration.secret_key = None
else:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET


def _ensure_configured() -> None:
    if not (Configuration.account_id and Configuration.secret_key):
        raise RuntimeError("YOOKASSA_SHOP_ID and YOOKASSA_SECRET must be set in environment")


def create_payment(
    amount: float,
    currency: str = "RUB",
    description: str = "Payment",
    return_url: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    capture: bool = True,
) -> Dict:
    """Create a payment in YooKassa (test/sandbox ready).

    Returns a dictionary with keys: id, status, amount, currency, confirmation
    (may include confirmation.url), and raw (the SDK Payment object as dict).
    """
    _ensure_configured()

    amount_value = f"{amount:.2f}"
    payload = {
        "amount": {"value": amount_value, "currency": currency},
        "confirmation": {"type": "redirect"},
        "capture": capture,
        "description": description,
    }
    if return_url:
        payload["confirmation"]["return_url"] = return_url
    if metadata:
        payload["metadata"] = metadata

    payment = Payment.create(payload)

    result = {
        "id": getattr(payment, "id", None),
        "status": getattr(payment, "status", None),
        "amount": amount_value,
        "currency": currency,
        "confirmation": getattr(payment, "confirmation", None),
        "raw": payment,
    }
    return result


def check_payment_status(payment_id: str) -> Dict:
    """Retrieve payment status from YooKassa by payment id.

    Returns a dict with keys: id, status, paid (bool), amount, currency, raw.
    """
    _ensure_configured()
    payment = Payment.find_one(payment_id)
    amt = None
    curr = None
    if getattr(payment, "amount", None):
        # Payment.amount may be an object or a dict depending on SDK version
        if isinstance(payment.amount, dict):
            amt = payment.amount.get("value")
            curr = payment.amount.get("currency")
        else:
            amt = getattr(payment.amount, "value", None)
            curr = getattr(payment.amount, "currency", None)

    return {
        "id": getattr(payment, "id", None),
        "status": getattr(payment, "status", None),
        "paid": getattr(payment, "paid", None),
        "amount": amt,
        "currency": curr,
        "raw": payment,
    }


if __name__ == "__main__":
    # Quick manual test (won't run during import). Replace return_url with a reachable URL
    # when testing redirect confirmation in a browser.
    try:
        print("Creating test payment (1.00 RUB)...")
        info = create_payment(1.00, description="Test payment", return_url="https://example.com/return")
        print("Payment created:")
        print("  id:", info.get("id"))
        print("  status:", info.get("status"))
        confirmation = info.get("confirmation")
        if confirmation:
            # SDK may return an object with dict-like access or attributes
            if isinstance(confirmation, dict):
                conf_url = (confirmation.get("confirmation_url")
                            or confirmation.get("url")
                            or (confirmation.get("confirmation") or {}).get("confirmation_url"))
            else:
                conf_url = getattr(confirmation, "confirmation_url", None) or getattr(confirmation, "url", None)
            print("  confirmation url:", conf_url)
    except Exception as e:
        print("YooKassa test payment failed:", e)
