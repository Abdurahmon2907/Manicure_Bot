"""
Проверка подписки пользователя на Telegram-канал.
"""

import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import config

logger = logging.getLogger(__name__)


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """
    Проверить, подписан ли пользователь на канал.
    Использует метод getChatMember (бот должен быть администратором канала).
    """
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        # "chat not found" / "member list is inaccessible" — бот не добавлен
        # в канал администратором или CHANNEL_ID указан неверно
        logger.error("Не удалось проверить подписку %s на %s: %s", user_id, config.CHANNEL_ID, e)
        return False

    if member.status in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    ):
        return True
    # Ограниченный пользователь всё ещё может состоять в канале
    return member.status == ChatMemberStatus.RESTRICTED and bool(getattr(member, "is_member", False))
