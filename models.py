# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from db import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    is_active = Column(Boolean, default=False)
    config = Column(String, nullable=True)

    subscription_until = Column(DateTime, nullable=True)
    notified_expiring = Column(Boolean, default=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)      # yookassa / stars
    payment_id = Column(String, unique=True)
    amount = Column(Integer)
    status = Column(String)                        # pending / success
    created_at = Column(DateTime, server_default=func.now())
