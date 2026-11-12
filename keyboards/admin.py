"""
Клавиатуры админ-панели.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_panel_kb() -> InlineKeyboardMarkup:
    """Главное меню админ-панели."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить рабочий день", callback_data="admin_add_day")],
        [InlineKeyboardButton(text="🕐 Добавить слот", callback_data="admin_add_slot")],
        [InlineKeyboardButton(text="🗑 Удалить слот", callback_data="admin_remove_slot")],
        [InlineKeyboardButton(text="❌ Отменить запись клиента", callback_data="admin_cancel_booking")],
        [InlineKeyboardButton(text="🔒 Закрыть день", callback_data="admin_close_day")],
        [InlineKeyboardButton(text="📋 Просмотр расписания", callback_data="admin_view_schedule")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")],
    ])


def admin_slots_kb(slots: list[dict], action_prefix: str) -> InlineKeyboardMarkup:
    """
    Клавиатура со слотами для админ-действий.
    action_prefix: 'admin_rm' для удаления, 'admin_cancel' для отмены записи.
    """
    rows = []
    for slot in slots:
        if action_prefix == "admin_rm":
            status = "🟢" if slot["is_available"] else "🔴"
            rows.append([
                InlineKeyboardButton(
                    text=f"{status} {slot['time']}",
                    callback_data=f"admin_rm_slot:{slot['id']}",
                )
            ])
        elif action_prefix == "admin_cancel" and slot.get("booking_id"):
            rows.append([
                InlineKeyboardButton(
                    text=f"❌ {slot['time']} — {slot['client_name']}",
                    callback_data=f"admin_cancel_bk:{slot['booking_id']}",
                )
            ])

    rows.append([
        InlineKeyboardButton(text="◀️ Админ-панель", callback_data="admin_panel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_default_slots_kb() -> InlineKeyboardMarkup:
    """Быстрый выбор стандартных слотов при добавлении рабочего дня."""
    import config
    rows = []
    row = []
    for t in config.DEFAULT_TIME_SLOTS:
        row.append(
            InlineKeyboardButton(text=t, callback_data=f"admin_default_slot:{t}")
        )
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([
        InlineKeyboardButton(text="✅ Готово", callback_data="admin_add_day_done"),
    ])
    rows.append([
        InlineKeyboardButton(text="◀️ Админ-панель", callback_data="admin_panel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
