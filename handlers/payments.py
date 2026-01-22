# handlers_payments.py
from aiogram import Router, F
from aiogram.types import Message
from payments.yookassa import create_yookassa_payment, get_payments_stats
from payments.payments_telegram_stars import stars_stats
from services.remnawave import users_stats

router = Router()

# Пользовательские действия
@router.message(F.text == "Оплатить через YooKassa")
async def pay_yookassa(message: Message):
    url = await create_yookassa_payment(message.from_user.id, 500, "Услуга")
    await message.answer(f"Перейдите по ссылке для оплаты:\n{url}")

@router.message(F.text == "Оплатить через Stars")
async def pay_stars(message: Message):
    await message.answer("Выберете сумму и произведите оплату через встроенный механизм Telegram.")

@router.message(F.text == "Пробный период")
async def trial_period(message: Message):
    await message.answer("Пробный конфиг активирован. Конфигурация отправлена.")
    # сюда можно интегрировать trial-логику

# Админские действия
@router.message(F.text == "Статистика YooKassa День")
async def stat_yk_day(message: Message):
    val = await get_payments_stats("day")
    await message.answer(f"YooKassa сегодня: {val}")

@router.message(F.text == "Статистика YooKassa Месяц")
async def stat_yk_month(message: Message):
    val = await get_payments_stats("month")
    await message.answer(f"YooKassa за месяц: {val}")

@router.message(F.text == "Статистика YooKassa Всё")
async def stat_yk_all(message: Message):
    val = await get_payments_stats("all")
    await message.answer(f"YooKassa за всё время: {val}")

@router.message(F.text == "Статистика Stars")
async def stat_stars(message: Message):
    val = await stars_stats("all")
    await message.answer(f"Stars общая: {val}")

@router.message(F.text == "Пользователи Remnawave")
async def stat_remnawave(message: Message):
    stats = await users_stats()
    await message.answer(f"Всего: {stats['total_users']}, Активных: {stats['active_users']}")
