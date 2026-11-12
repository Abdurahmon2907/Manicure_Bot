"""
Inline-календарь для выбора даты.
"""

import calendar
from datetime import date, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

MONTHS_RU = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]

WEEKDAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def build_calendar(
    year: int,
    month: int,
    available_dates: set[date],
    prefix: str = "cal",
    show_past: bool = False,
) -> InlineKeyboardMarkup:
    """
    Построить inline-календарь.
    prefix — префикс callback_data для различения контекстов (book, admin).
    available_dates — множество дат, доступных для выбора.
    """
    today = date.today()
    max_date = today + timedelta(days=config.SCHEDULE_DAYS_AHEAD)

    # Заголовок с навигацией по месяцам
    header_row = []
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    # Кнопка «назад» по месяцам (не раньше текущего месяца)
    if date(prev_year, prev_month, 1) >= date(today.year, today.month, 1):
        header_row.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"{prefix}_nav:{prev_year}:{prev_month}",
            )
        )
    else:
        header_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))

    header_row.append(
        InlineKeyboardButton(
            text=f"{MONTHS_RU[month - 1]} {year}",
            callback_data="noop",
        )
    )

    # Кнопка «вперёд» (не дальше max_date)
    if date(next_year, next_month, 1) <= max_date.replace(day=1) or (
        next_year == max_date.year and next_month <= max_date.month
    ):
        header_row.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"{prefix}_nav:{next_year}:{next_month}",
            )
        )
    else:
        header_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))

    rows = [header_row]

    # Дни недели
    rows.append([
        InlineKeyboardButton(text=day, callback_data="noop")
        for day in WEEKDAYS_SHORT
    ])

    # Дни месяца
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        week_row = []
        for day_num in week:
            if day_num == 0:
                week_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
                continue

            current = date(year, month, day_num)
            # Прошедшие даты и даты за пределами диапазона — неактивны
            if not show_past and current < today:
                week_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
            elif current > max_date:
                week_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
            elif current in available_dates:
                week_row.append(
                    InlineKeyboardButton(
                        text=str(day_num),
                        callback_data=f"{prefix}_day:{current.isoformat()}",
                    )
                )
            else:
                # День без свободных слотов — показываем, но неактивен
                week_row.append(
                    InlineKeyboardButton(text=f"·{day_num}", callback_data="noop")
                )
        rows.append(week_row)

    # Кнопка «Назад»
    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_admin_calendar(
    year: int,
    month: int,
    prefix: str = "admin_cal",
) -> InlineKeyboardMarkup:
    """
    Календарь для админ-панели — все будущие даты доступны для выбора.
    """
    today = date.today()
    max_date = today + timedelta(days=config.SCHEDULE_DAYS_AHEAD)

    header_row = []
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    if date(prev_year, prev_month, 1) >= date(today.year, today.month, 1):
        header_row.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"{prefix}_nav:{prev_year}:{prev_month}",
            )
        )
    else:
        header_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))

    header_row.append(
        InlineKeyboardButton(
            text=f"{MONTHS_RU[month - 1]} {year}",
            callback_data="noop",
        )
    )

    if date(next_year, next_month, 1) <= max_date.replace(day=1) or (
        next_year == max_date.year and next_month <= max_date.month
    ):
        header_row.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"{prefix}_nav:{next_year}:{next_month}",
            )
        )
    else:
        header_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))

    rows = [header_row]
    rows.append([
        InlineKeyboardButton(text=day, callback_data="noop")
        for day in WEEKDAYS_SHORT
    ])

    cal = calendar.monthcalendar(year, month)
    for week in cal:
        week_row = []
        for day_num in week:
            if day_num == 0:
                week_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
                continue

            current = date(year, month, day_num)
            if current < today or current > max_date:
                week_row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
            else:
                week_row.append(
                    InlineKeyboardButton(
                        text=str(day_num),
                        callback_data=f"{prefix}_day:{current.isoformat()}",
                    )
                )
        rows.append(week_row)

    rows.append([
        InlineKeyboardButton(text="◀️ Админ-панель", callback_data="admin_panel"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)
