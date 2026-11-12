"""
Конфигурация бота.
Заполните значения перед запуском.
"""

# Токен бота от @BotFather
BOT_TOKEN = "8810079229:AAHItOoewjoXmGnTu7beDxhQRPc8ZAXmDDg"

# Telegram ID администратора (мастера)
ADMIN_ID = 1538736674

# Канал для обязательной подписки (формат: @username или -100xxxxxxxxxx)
CHANNEL_ID = -1003849973564
CHANNEL_LINK = "https://t.me/+DoHR4jHhpdg4ZTBi"

# Канал для публикации расписания (формат: @username или -100xxxxxxxxxx)
SCHEDULE_CHANNEL_ID = "@your_schedule_channel"

# Путь к файлу базы данных SQLite
DATABASE_PATH = "bot.db"

# Количество дней вперёд для отображения расписания
SCHEDULE_DAYS_AHEAD = 31

# Стандартные временные слоты (используются при добавлении рабочего дня)
DEFAULT_TIME_SLOTS = [
    "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00",
    "17:00", "18:00",
]
