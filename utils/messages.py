"""
Форматирование сообщений (HTML).
"""

from datetime import date
from html import escape


MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]

WEEKDAYS_RU = [
    "Понедельник", "Вторник", "Среда", "Четверг",
    "Пятница", "Суббота", "Воскресенье",
]


def format_date(d: date) -> str:
    """Красивое форматирование даты: «15 июля 2026, Пятница»."""
    weekday = WEEKDAYS_RU[d.weekday()]
    return f"{d.day} {MONTHS_RU[d.month]} {d.year}, {weekday}"


def welcome_text(name: str) -> str:
    """Приветственное сообщение."""
    return (
        f"💅 <b>Добро пожаловать, {name}!</b>\n\n"
        f"Я бот для записи к мастеру по маникюру.\n"
        f"Выберите действие в меню ниже:"
    )


def prices_text() -> str:
    """Текст прайс-листа."""
    return (
        "💰 <b>Прайс-лист</b>\n\n"
        "Френч — <b>1000₽</b>\n"
        "Квадрат — <b>500₽</b>"
    )


def booking_confirm_text(
    day: date, time_str: str, client_name: str, phone: str
) -> str:
    """Текст подтверждения записи."""
    return (
        "📋 <b>Подтверждение записи</b>\n\n"
        f"📅 Дата: <b>{format_date(day)}</b>\n"
        f"🕐 Время: <b>{time_str}</b>\n"
        f"👤 Имя: <b>{escape(client_name)}</b>\n"
        f"📞 Телефон: <b>{escape(phone)}</b>\n\n"
        "Всё верно?"
    )


def booking_success_text(day: date, time_str: str) -> str:
    """Сообщение об успешной записи."""
    return (
        "✅ <b>Вы успешно записаны!</b>\n\n"
        f"📅 {format_date(day)}\n"
        f"🕐 {time_str}\n\n"
        "Ждём вас! 💅"
    )


def admin_new_booking_text(
    client_name: str, phone: str, day: date, time_str: str, user_id: int
) -> str:
    """Уведомление администратору о новой записи."""
    return (
        "🆕 <b>Новая запись!</b>\n\n"
        f"👤 {escape(client_name)}\n"
        f"📞 {escape(phone)}\n"
        f"📅 {format_date(day)}\n"
        f"🕐 {time_str}\n"
        f"🆔 User ID: <code>{user_id}</code> · "
        f"<a href=\"tg://user?id={user_id}\">Написать клиенту</a>"
    )


def channel_schedule_text(day: date, slots_info: list[dict]) -> str:
    """Сообщение в канал расписания."""
    lines = [f"📅 <b>Расписание на {format_date(day)}</b>\n"]
    for slot in slots_info:
        if slot.get("client_name"):
            lines.append(
                f"🕐 {slot['time']} — {escape(slot['client_name'])} ({escape(slot['phone'])})"
            )
        elif slot["is_available"]:
            lines.append(f"🕐 {slot['time']} — <i>свободно</i>")
        else:
            lines.append(f"🕐 {slot['time']} — <i>занято</i>")
    return "\n".join(lines)


def admin_schedule_text(day: date, slots_info: list[dict]) -> str:
    """Расписание дня для админ-панели: кто, когда и контакты."""
    booked = [s for s in slots_info if s.get("client_name")]
    free = [s for s in slots_info if not s.get("client_name") and s["is_available"]]

    lines = [
        f"📋 <b>Расписание на {format_date(day)}</b>",
        f"Записей: <b>{len(booked)}</b> · Свободно: <b>{len(free)}</b>\n",
    ]
    for slot in slots_info:
        if slot.get("client_name"):
            lines.append(
                f"🔴 <b>{slot['time']}</b> — ЗАНЯТО\n"
                f"     👤 {escape(slot['client_name'])}\n"
                f"     📞 {escape(slot['phone'])}\n"
                f"     💬 <a href=\"tg://user?id={slot['user_id']}\">Написать клиенту</a>"
            )
        elif slot["is_available"]:
            lines.append(f"🟢 <b>{slot['time']}</b> — свободно")
        else:
            lines.append(f"⚫ <b>{slot['time']}</b> — недоступно")
    return "\n".join(lines)


def my_booking_text(day: date, time_str: str, client_name: str) -> str:
    """Информация о текущей записи пользователя."""
    return (
        "📝 <b>Ваша запись</b>\n\n"
        f"📅 {format_date(day)}\n"
        f"🕐 {time_str}\n"
        f"👤 {escape(client_name)}"
    )
