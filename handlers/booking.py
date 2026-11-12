"""
Обработчики процесса записи (FSM).
"""

from datetime import date, datetime

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import config
from database.db import Database
from handlers.subscription import require_subscription
from keyboards.booking import time_slots_kb
from keyboards.calendar import build_calendar
from keyboards.main import back_to_menu_kb, confirm_booking_kb, main_menu_kb
from states.booking import BookingStates
from utils.messages import (
    admin_new_booking_text,
    booking_confirm_text,
    booking_success_text,
    channel_schedule_text,
    format_date,
    my_booking_text,
)
from utils.scheduler import cancel_reminder, schedule_reminder
from utils.subscription import is_subscribed

router = Router()


@router.callback_query(F.data == "book")
async def start_booking(
    callback: CallbackQuery, state: FSMContext, bot: Bot, db: Database
) -> None:
    """Начало процесса записи — проверка подписки и показ календаря."""
    if not await require_subscription(callback, bot):
        return

    await _begin_booking(callback, state, db)


@router.callback_query(F.data == "check_subscription")
async def check_subscription(
    callback: CallbackQuery, state: FSMContext, bot: Bot, db: Database
) -> None:
    """Кнопка «Я подписался» — повторная проверка и переход к записи."""
    if not await is_subscribed(bot, callback.from_user.id):
        # Сообщение не меняем (иначе "message is not modified"), только уведомляем
        await callback.answer(
            "Вы ещё не подписаны на канал ❌\n"
            "Подпишитесь и нажмите кнопку ещё раз.",
            show_alert=True,
        )
        return

    await _begin_booking(callback, state, db, notice="Подписка подтверждена! ✅")


async def _begin_booking(
    callback: CallbackQuery, state: FSMContext, db: Database, notice: str | None = None
) -> None:
    """Проверка активной записи и показ календаря (после проверки подписки)."""
    # Проверка: один пользователь — одна запись
    existing = await db.get_user_booking(callback.from_user.id)
    if existing:
        await callback.message.edit_text(
            "⚠️ У вас уже есть активная запись.\n"
            "Сначала отмените её, чтобы записаться снова.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
        await callback.answer(notice)
        return

    await state.set_state(BookingStates.choosing_date)
    await _show_booking_calendar(callback, db)
    await callback.answer(notice)


async def _show_booking_calendar(
    callback: CallbackQuery, db: Database, year: int | None = None, month: int | None = None
) -> None:
    """Отобразить календарь с доступными датами."""
    today = date.today()
    year = year or today.year
    month = month or today.month

    from datetime import timedelta
    end = today + timedelta(days=config.SCHEDULE_DAYS_AHEAD)
    available = await db.get_available_dates(today, end)
    available_set = set(available)

    kb = build_calendar(year, month, available_set, prefix="cal")
    await callback.message.edit_text(
        "📅 <b>Выберите дату записи:</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("cal_nav:"))
async def navigate_calendar(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    """Навигация по месяцам в календаре записи."""
    _, year, month = callback.data.split(":")
    await _show_booking_calendar(callback, db, int(year), int(month))
    await callback.answer()


@router.callback_query(F.data.startswith("cal_day:"))
async def choose_date(
    callback: CallbackQuery, state: FSMContext, db: Database
) -> None:
    """Выбор даты — показ доступных слотов."""
    day_str = callback.data.split(":")[1]
    selected = date.fromisoformat(day_str)

    slots = await db.get_available_slots(selected)
    if not slots:
        await callback.answer("Нет свободных слотов на эту дату", show_alert=True)
        return

    await state.update_data(selected_date=day_str)
    await state.set_state(BookingStates.choosing_time)

    await callback.message.edit_text(
        f"🕐 <b>Выберите время на {format_date(selected)}:</b>",
        reply_markup=time_slots_kb(slots),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("slot:"))
async def choose_time(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    """Выбор временного слота."""
    slot_id = int(callback.data.split(":")[1])
    slot = await db.get_slot_by_id(slot_id)

    if not slot or not slot["is_available"]:
        await callback.answer("Этот слот уже занят", show_alert=True)
        return

    await state.update_data(slot_id=slot_id, selected_time=slot["time"])
    await state.set_state(BookingStates.entering_name)

    await callback.message.edit_text(
        "👤 <b>Введите ваше имя:</b>",
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BookingStates.entering_name)
async def enter_name(message: Message, state: FSMContext) -> None:
    """Получение имени клиента."""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите имя ещё раз:")
        return

    await state.update_data(client_name=name)
    await state.set_state(BookingStates.entering_phone)
    await message.answer(
        "📞 <b>Введите ваш номер телефона:</b>",
        parse_mode="HTML",
    )


@router.message(BookingStates.entering_phone)
async def enter_phone(message: Message, state: FSMContext) -> None:
    """Получение номера телефона."""
    phone = message.text.strip()
    # Простая валидация телефона
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 10:
        await message.answer("❌ Некорректный номер. Введите телефон ещё раз:")
        return

    await state.update_data(phone=phone)
    await state.set_state(BookingStates.confirming)

    data = await state.get_data()
    selected = date.fromisoformat(data["selected_date"])

    await message.answer(
        booking_confirm_text(selected, data["selected_time"], data["client_name"], phone),
        reply_markup=confirm_booking_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "confirm_booking", BookingStates.confirming)
async def confirm_booking(
    callback: CallbackQuery, state: FSMContext, bot: Bot, db: Database
) -> None:
    """Подтверждение и сохранение записи."""
    data = await state.get_data()
    user_id = callback.from_user.id
    selected = date.fromisoformat(data["selected_date"])
    time_str = data["selected_time"]
    slot_id = data["slot_id"]

    # Планируем напоминание
    visit_dt = datetime.strptime(
        f"{data['selected_date']} {time_str}", "%Y-%m-%d %H:%M"
    )

    booking_id = await db.create_booking(
        user_id=user_id,
        slot_id=slot_id,
        day=selected,
        time_str=time_str,
        client_name=data["client_name"],
        phone=data["phone"],
    )

    if not booking_id:
        await callback.message.edit_text(
            "❌ Не удалось записаться. Возможно, слот уже занят или у вас есть запись.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
        await state.clear()
        await callback.answer()
        return

    # Планирование напоминания за 24 часа
    job_id = schedule_reminder(bot, booking_id, user_id, visit_dt, time_str)
    if job_id:
        await db.update_reminder_job_id(booking_id, job_id)

    await state.clear()

    # Уведомление пользователю
    await callback.message.edit_text(
        booking_success_text(selected, time_str),
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML",
    )

    # Уведомление администратору
    try:
        await bot.send_message(
            config.ADMIN_ID,
            admin_new_booking_text(
                data["client_name"], data["phone"], selected, time_str, user_id
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # Публикация в канал расписания
    try:
        slots_info = await db.get_all_slots_for_date(selected)
        await bot.send_message(
            config.SCHEDULE_CHANNEL_ID,
            channel_schedule_text(selected, slots_info),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await callback.answer("Запись подтверждена! ✅")


@router.callback_query(F.data == "confirm_booking")
async def confirm_booking_expired(callback: CallbackQuery, state: FSMContext) -> None:
    """Подтверждение без активной сессии (например, бот был перезапущен)."""
    await state.clear()
    await callback.message.edit_text(
        "⌛ Сессия записи устарела. Пожалуйста, начните запись заново.",
        reply_markup=main_menu_kb(is_admin=callback.from_user.id == config.ADMIN_ID),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "my_booking")
async def show_my_booking(callback: CallbackQuery, db: Database) -> None:
    """Показать текущую запись пользователя."""
    booking = await db.get_user_booking(callback.from_user.id)
    if not booking:
        await callback.message.edit_text(
            "📝 У вас нет активных записей.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
    else:
        day = date.fromisoformat(booking["date"])
        await callback.message.edit_text(
            my_booking_text(day, booking["time"], booking["client_name"]),
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
    await callback.answer()
