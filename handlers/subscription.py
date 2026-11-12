"""
Проверка подписки на канал перед записью.
"""

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from keyboards.main import subscription_kb
from utils.subscription import is_subscribed


async def require_subscription(callback: CallbackQuery, bot: Bot) -> bool:
    """
    Проверить подписку пользователя.
    Если не подписан — показать сообщение и вернуть False.
    """
    if await is_subscribed(bot, callback.from_user.id):
        return True

    try:
        await callback.message.edit_text(
            "📢 <b>Для записи необходимо подписаться на канал</b>\n\n"
            "Подпишитесь и нажмите «✅ Я подписался».",
            reply_markup=subscription_kb(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        # Сообщение уже показано (message is not modified)
        pass
    await callback.answer()
    return False
