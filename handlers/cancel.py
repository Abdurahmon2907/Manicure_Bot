"""
Отмена записи пользователем.
"""

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

import config
from database.db import Database
from keyboards.main import back_to_menu_kb, cancel_confirm_kb, main_menu_kb
from utils.messages import channel_schedule_text, format_date
from utils.scheduler import cancel_reminder

router = Router()


@router.callback_query(F.data == "cancel_booking")
async def ask_cancel_booking(callback: CallbackQuery, db: Database) -> None:
    """Запрос подтверждения отмены записи."""
    booking = await db.get_user_booking(callback.from_user.id)
    if not booking:
        await callback.message.edit_text(
            "📝 У вас нет активных записей для отмены.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    from datetime import date
    day = date.fromisoformat(booking["date"])
    await callback.message.edit_text(
        f"❓ Вы уверены, что хотите отменить запись?\n\n"
        f"📅 {format_date(day)}\n"
        f"🕐 {booking['time']}",
        reply_markup=cancel_confirm_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_cancel")
async def confirm_cancel(
    callback: CallbackQuery, bot: Bot, db: Database
) -> None:
    """Подтверждение отмены — освобождение слота и удаление напоминания."""
    booking = await db.cancel_booking(callback.from_user.id)
    if not booking:
        await callback.message.edit_text(
            "❌ Запись не найдена.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    # Удаляем задачу напоминания
    cancel_reminder(booking.get("reminder_job_id"))

    from datetime import date
    day = date.fromisoformat(booking["date"])

    await callback.message.edit_text(
        f"✅ Запись отменена.\n\n"
        f"📅 {format_date(day)}\n"
        f"🕐 {booking['time']}\n\n"
        f"Слот снова доступен для записи.",
        reply_markup=main_menu_kb(
            is_admin=(callback.from_user.id == config.ADMIN_ID)
        ),
        parse_mode="HTML",
    )

    # Обновляем канал расписания
    try:
        slots_info = await db.get_all_slots_for_date(day)
        await bot.send_message(
            config.SCHEDULE_CHANNEL_ID,
            channel_schedule_text(day, slots_info),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # Уведомляем администратора
    try:
        await bot.send_message(
            config.ADMIN_ID,
            f"❌ <b>Отмена записи</b>\n\n"
            f"👤 {booking['client_name']}\n"
            f"📞 {booking['phone']}\n"
            f"📅 {format_date(day)}\n"
            f"🕐 {booking['time']}",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await callback.answer("Запись отменена")
