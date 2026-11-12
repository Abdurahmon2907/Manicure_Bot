"""
Клавиатуры для процесса записи.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def time_slots_kb(slots: list[dict]) -> InlineKeyboardMarkup:
    """Клавиатура с доступными временными слотами."""
    rows = []
    row = []
    for slot in slots:
        row.append(
            InlineKeyboardButton(
                text=slot["time"],
                callback_data=f"slot:{slot['id']}",
            )
        )
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="book"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
