"""
Точка входа — запуск Telegram-бота для мастера по маникюру.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable

import config
from database.db import Database
from handlers import admin, booking, cancel, start
from utils.scheduler import restore_reminders, shutdown_scheduler, start_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Инициализация и запуск бота."""
    # Проверка конфигурации
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Укажите BOT_TOKEN в config.py!")
        sys.exit(1)

    # Инициализация базы данных
    db = Database()
    await db.connect()
    logger.info("База данных инициализирована")

    # Создание бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Передаём db через middleware (dependency injection)
    async def db_middleware(
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["db"] = db
        return await handler(event, data)

    dp.update.outer_middleware(db_middleware)

    # Подключение роутеров
    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(cancel.router)
    dp.include_router(admin.router)

    # Запуск планировщика и восстановление напоминаний
    start_scheduler()
    await restore_reminders(bot, db)
    logger.info("Планировщик напоминаний запущен")

    logger.info("Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        shutdown_scheduler()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
