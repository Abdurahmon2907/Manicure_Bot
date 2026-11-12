"""
Главное меню и вспомогательные клавиатуры.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config


def main_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Главное меню пользователя."""
    buttons = [
        [InlineKeyboardButton(text="📅 Записаться", callback_data="book")],
        [InlineKeyboardButton(text="📝 Моя запись", callback_data="my_booking")],
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data="cancel_booking")],
        [InlineKeyboardButton(text="💰 Прайсы", callback_data="prices")],
        [InlineKeyboardButton(text="🖼 Портфолио", callback_data="portfolio")],
    ]
    if is_admin:
        buttons.append(
            [InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscription_kb() -> InlineKeyboardMarkup:
    """Кнопки для проверки подписки на канал."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=config.CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")],
    ])


def portfolio_kb() -> InlineKeyboardMarkup:
    """Кнопка с ссылкой на портфолио."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Смотреть портфолио",
            url="https://ru.pinterest.com/crystalwithluv/_created/",
        )],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")],
    ])


def confirm_booking_kb() -> InlineKeyboardMarkup:
    """Подтверждение записи."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_menu"),
        ],
    ])


def cancel_confirm_kb() -> InlineKeyboardMarkup:
    """Подтверждение отмены записи."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, отменить", callback_data="confirm_cancel"),
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"),
        ],
    ])
