from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    telegram_id: int
    is_trial_used: bool = False
    status: Optional[str] = None  # trial | paid
    config: Optional[str] = None
    expires_at: Optional[datetime] = None
    menu_mode: str = "reply"  # reply | inline
