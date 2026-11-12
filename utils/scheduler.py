"""
Планировщик напоминаний через APScheduler.
"""

from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from database.db import Database


# Глобальный экземпляр планировщика
scheduler = AsyncIOScheduler()


def make_job_id(booking_id: int) -> str:
    """Сформировать уникальный ID задачи напоминания."""
    return f"reminder_{booking_id}"


async def send_reminder(bot: Bot, user_id: int, time_str: str) -> None:
    """Отправить напоминание пользователю за 24 часа до визита."""
    text = (
        f"Напоминаем, что вы записаны на наращивание ресниц завтра в <b>{time_str}</b>.\n"
        f"Ждём вас ❤️"
    )
    try:
        await bot.send_message(user_id, text, parse_mode="HTML")
    except Exception:
        pass  # Пользователь мог заблокировать бота


def schedule_reminder(
    bot: Bot,
    booking_id: int,
    user_id: int,
    visit_datetime: datetime,
    time_str: str,
) -> str | None:
    """
    Запланировать напоминание за 24 часа до визита.
    Возвращает job_id или None, если до визита менее 24 часов.
    """
    remind_at = visit_datetime - timedelta(hours=24)
    if remind_at <= datetime.now():
        return None

    job_id = make_job_id(booking_id)
    scheduler.add_job(
        send_reminder,
        trigger=DateTrigger(run_date=remind_at),
        args=[bot, user_id, time_str],
        id=job_id,
        replace_existing=True,
    )
    return job_id


def cancel_reminder(job_id: str | None) -> None:
    """Удалить запланированное напоминание."""
    if not job_id:
        return
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass


async def restore_reminders(bot: Bot, db: Database) -> None:
    """
    Восстановить задачи напоминаний из базы данных при старте бота.
    """
    bookings = await db.get_bookings_for_reminder_restore()
    for booking in bookings:
        job_id = schedule_reminder(
            bot=bot,
            booking_id=booking["id"],
            user_id=booking["user_id"],
            visit_datetime=booking["visit_datetime"],
            time_str=booking["time"],
        )
        if job_id and job_id != booking.get("reminder_job_id"):
            await db.update_reminder_job_id(booking["id"], job_id)


def start_scheduler() -> None:
    """Запустить планировщик."""
    if not scheduler.running:
        scheduler.start()


def shutdown_scheduler() -> None:
    """Остановить планировщик."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
