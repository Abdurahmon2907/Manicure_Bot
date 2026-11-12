"""
Админ-панель: управление расписанием и записями.
Доступ только для ADMIN_ID.
"""

from datetime import date

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import config
from database.db import Database
from keyboards.admin import admin_default_slots_kb, admin_panel_kb, admin_slots_kb
from keyboards.calendar import build_admin_calendar
from keyboards.main import back_to_menu_kb, main_menu_kb
from states.admin import AdminStates
from utils.messages import admin_schedule_text, channel_schedule_text, format_date
from utils.scheduler import cancel_reminder

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID


async def _deny_access(callback: CallbackQuery) -> None:
    await callback.answer("⛔ Доступ запрещён", show_alert=True)


# ── Вход в админ-панель ──────────────────────────────────────

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, state: FSMContext) -> None:
    """Главное меню админ-панели."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.clear()
    await callback.message.edit_text(
        "⚙️ <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Добавление рабочего дня ──────────────────────────────────

@router.callback_query(F.data == "admin_add_day")
async def admin_add_day_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбор даты для нового рабочего дня."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.set_state(AdminStates.choosing_date_add_day)
    today = date.today()
    kb = build_admin_calendar(today.year, today.month, prefix="admin_add")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для добавления рабочего дня:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_add_nav:"))
async def admin_add_day_navigate(callback: CallbackQuery) -> None:
    """Навигация по месяцам при добавлении рабочего дня."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    _, year, month = callback.data.split(":")
    kb = build_admin_calendar(int(year), int(month), prefix="admin_add")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для добавления рабочего дня:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_add_day:"))
async def admin_add_day_select(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    """Дата выбрана — добавляем рабочий день и предлагаем слоты."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    day_str = callback.data.split(":")[1]
    selected = date.fromisoformat(day_str)

    added = await db.add_work_day(selected)
    await state.update_data(admin_day=day_str, added_slots=[])

    if added:
        text = (
            f"✅ Рабочий день <b>{format_date(selected)}</b> добавлен.\n\n"
            f"Выберите стандартные слоты или нажмите «✅ Готово»:"
        )
    else:
        text = (
            f"ℹ️ День <b>{format_date(selected)}</b> уже существует.\n\n"
            f"Добавьте слоты или нажмите «✅ Готово»:"
        )

    await state.set_state(AdminStates.entering_slot_time)
    await callback.message.edit_text(
        text,
        reply_markup=admin_default_slots_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_default_slot:"))
async def admin_add_default_slot(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    """Добавление стандартного слота при создании рабочего дня."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    # maxsplit=1: само время содержит ":" ("admin_default_slot:09:00")
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()
    day = date.fromisoformat(data["admin_day"])

    added = await db.add_time_slot(day, time_str)
    msg = f"✅ Слот {time_str} добавлен" if added else f"ℹ️ Слот {time_str} уже существует"
    await callback.answer(msg)


@router.callback_query(F.data == "admin_add_day_done")
async def admin_add_day_done(callback: CallbackQuery, state: FSMContext) -> None:
    """Завершение добавления рабочего дня."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.clear()
    await callback.message.edit_text(
        "✅ Рабочий день настроен!",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Добавление слота ───────────────────────────────────────────

@router.callback_query(F.data == "admin_add_slot")
async def admin_add_slot_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбор даты для добавления слота."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.set_state(AdminStates.choosing_date_add_slot)
    today = date.today()
    kb = build_admin_calendar(today.year, today.month, prefix="admin_slot")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для добавления слота:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_slot_nav:"))
async def admin_add_slot_navigate(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    _, year, month = callback.data.split(":")
    kb = build_admin_calendar(int(year), int(month), prefix="admin_slot")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для добавления слота:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_slot_day:"))
async def admin_add_slot_date(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Дата выбрана — запрос времени."""
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    day_str = callback.data.split(":")[1]
    await state.update_data(admin_day=day_str)
    await state.set_state(AdminStates.entering_slot_time)
    await callback.message.edit_text(
        "🕐 <b>Введите время слота в формате ЧЧ:ММ</b>\n(например, 14:30):",
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.entering_slot_time)
async def admin_enter_slot_time(
    message: Message, state: FSMContext, db: Database
) -> None:
    """Обработка введённого времени для нового слота."""
    if not _is_admin(message.from_user.id):
        return

    time_str = message.text.strip()
    # Валидация формата ЧЧ:ММ
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
        time_str = f"{h:02d}:{m:02d}"
    except ValueError:
        await message.answer("❌ Неверный формат. Введите время как ЧЧ:ММ (например, 14:30):")
        return

    data = await state.get_data()
    if "admin_day" not in data:
        await state.clear()
        await message.answer("❌ Ошибка. Начните заново.", reply_markup=admin_panel_kb())
        return

    day = date.fromisoformat(data["admin_day"])
    added = await db.add_time_slot(day, time_str)
    await state.clear()

    if added:
        await message.answer(
            f"✅ Слот <b>{time_str}</b> добавлен на {format_date(day)}",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            f"ℹ️ Слот <b>{time_str}</b> уже существует на эту дату",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )


# ── Удаление слота ─────────────────────────────────────────────

@router.callback_query(F.data == "admin_remove_slot")
async def admin_remove_slot_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.set_state(AdminStates.choosing_date_remove_slot)
    today = date.today()
    kb = build_admin_calendar(today.year, today.month, prefix="admin_rm_cal")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для удаления слота:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_rm_cal_nav:"))
async def admin_remove_slot_navigate(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    _, year, month = callback.data.split(":")
    kb = build_admin_calendar(int(year), int(month), prefix="admin_rm_cal")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для удаления слота:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_rm_cal_day:"))
async def admin_remove_slot_date(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    day_str = callback.data.split(":")[1]
    selected = date.fromisoformat(day_str)
    slots = await db.get_all_slots_for_date(selected)

    if not slots:
        await callback.answer("На эту дату нет слотов", show_alert=True)
        return

    await state.set_state(AdminStates.choosing_slot_to_remove)
    await callback.message.edit_text(
        f"🗑 <b>Выберите слот для удаления ({format_date(selected)}):</b>",
        reply_markup=admin_slots_kb(slots, "admin_rm"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_rm_slot:"))
async def admin_remove_slot_confirm(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    slot_id = int(callback.data.split(":")[1])
    removed = await db.remove_time_slot(slot_id)
    await state.clear()

    if removed:
        await callback.message.edit_text(
            "✅ Слот удалён.",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            "❌ Нельзя удалить занятый слот. Сначала отмените запись.",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )
    await callback.answer()


# ── Отмена записи клиента ─────────────────────────────────────

@router.callback_query(F.data == "admin_cancel_booking")
async def admin_cancel_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.set_state(AdminStates.choosing_date_cancel)
    today = date.today()
    kb = build_admin_calendar(today.year, today.month, prefix="admin_cancel_cal")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для отмены записи:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_cancel_cal_nav:"))
async def admin_cancel_navigate(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    _, year, month = callback.data.split(":")
    kb = build_admin_calendar(int(year), int(month), prefix="admin_cancel_cal")
    await callback.message.edit_text(
        "📅 <b>Выберите дату для отмены записи:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_cancel_cal_day:"))
async def admin_cancel_date(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    day_str = callback.data.split(":")[1]
    selected = date.fromisoformat(day_str)
    slots = await db.get_all_slots_for_date(selected)
    booked = [s for s in slots if s.get("booking_id")]

    if not booked:
        await callback.answer("На эту дату нет записей", show_alert=True)
        return

    await state.set_state(AdminStates.choosing_booking_to_cancel)
    await callback.message.edit_text(
        f"❌ <b>Выберите запись для отмены ({format_date(selected)}):</b>",
        reply_markup=admin_slots_kb(booked, "admin_cancel"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_cancel_bk:"))
async def admin_cancel_booking_confirm(
    callback: CallbackQuery, state: FSMContext, bot: Bot, db: Database
) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    booking_id = int(callback.data.split(":")[1])
    booking = await db.admin_cancel_booking(booking_id)
    await state.clear()

    if not booking:
        await callback.message.edit_text(
            "❌ Запись не найдена.",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    cancel_reminder(booking.get("reminder_job_id"))

    day = date.fromisoformat(booking["date"])

    # Уведомляем клиента
    try:
        await bot.send_message(
            booking["user_id"],
            f"❌ Ваша запись на {format_date(day)} в {booking['time']} "
            f"была отменена администратором.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    # Обновляем канал
    try:
        slots_info = await db.get_all_slots_for_date(day)
        await bot.send_message(
            config.SCHEDULE_CHANNEL_ID,
            channel_schedule_text(day, slots_info),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await callback.message.edit_text(
        f"✅ Запись <b>{booking['client_name']}</b> отменена.\n"
        f"Слот {booking['time']} снова доступен.",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Закрытие дня ───────────────────────────────────────────────

@router.callback_query(F.data == "admin_close_day")
async def admin_close_day_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.set_state(AdminStates.choosing_date_close)
    today = date.today()
    kb = build_admin_calendar(today.year, today.month, prefix="admin_close")
    await callback.message.edit_text(
        "🔒 <b>Выберите день для полного закрытия:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_close_nav:"))
async def admin_close_navigate(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    _, year, month = callback.data.split(":")
    kb = build_admin_calendar(int(year), int(month), prefix="admin_close")
    await callback.message.edit_text(
        "🔒 <b>Выберите день для полного закрытия:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_close_day:"))
async def admin_close_day_confirm(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    day_str = callback.data.split(":")[1]
    selected = date.fromisoformat(day_str)
    await db.close_work_day(selected)
    await state.clear()

    await callback.message.edit_text(
        f"🔒 День <b>{format_date(selected)}</b> полностью закрыт.",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Просмотр расписания ────────────────────────────────────────

@router.callback_query(F.data == "admin_view_schedule")
async def admin_view_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    await state.set_state(AdminStates.choosing_date_view)
    today = date.today()
    kb = build_admin_calendar(today.year, today.month, prefix="admin_view")
    await callback.message.edit_text(
        "📋 <b>Выберите дату для просмотра расписания:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_nav:"))
async def admin_view_navigate(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    _, year, month = callback.data.split(":")
    kb = build_admin_calendar(int(year), int(month), prefix="admin_view")
    await callback.message.edit_text(
        "📋 <b>Выберите дату для просмотра расписания:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_day:"))
async def admin_view_schedule(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    if not _is_admin(callback.from_user.id):
        await _deny_access(callback)
        return

    day_str = callback.data.split(":")[1]
    selected = date.fromisoformat(day_str)
    slots = await db.get_all_slots_for_date(selected)
    await state.clear()

    if not slots:
        text = f"📋 На <b>{format_date(selected)}</b> нет слотов."
    else:
        text = admin_schedule_text(selected, slots)

    await callback.message.edit_text(
        text,
        reply_markup=admin_panel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
