<<<<<<< HEAD
# Telegram-бот для мастера по маникюру

Бот для записи клиентов с inline-календарём, админ-панелью, проверкой подписки на канал и автонапоминаниями.

## Структура проекта

```
.
├── bot.py                  # Точка входа, запуск бота
├── config.py               # Настройки (токен, ID админа, каналы)
├── requirements.txt        # Зависимости Python
├── bot.db                  # База SQLite (создаётся автоматически)
├── database/
│   ├── __init__.py
│   └── db.py               # Работа с SQLite
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start, главное меню, прайсы, портфолио
│   ├── subscription.py     # Проверка подписки на канал
│   ├── booking.py          # Процесс записи (FSM)
│   ├── cancel.py           # Отмена записи пользователем
│   └── admin.py            # Админ-панель (FSM)
├── keyboards/
│   ├── __init__.py
│   ├── main.py             # Главное меню
│   ├── calendar.py         # Inline-календарь
│   ├── booking.py          # Клавиатура слотов
│   └── admin.py            # Клавиатуры админ-панели
├── states/
│   ├── __init__.py
│   ├── booking.py          # FSM-состояния записи
│   └── admin.py            # FSM-состояния админки
└── utils/
    ├── __init__.py
    ├── subscription.py     # getChatMember — проверка подписки
    ├── scheduler.py        # APScheduler — напоминания за 24ч
    └── messages.py         # HTML-форматирование сообщений
```

## Установка

### 1. Требования

- Python 3.10 или выше
- Telegram-бот (создайте через [@BotFather](https://t.me/BotFather))
- Telegram-канал для обязательной подписки
- Telegram-канал для публикации расписания

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка config.py

Откройте `config.py` и заполните:

| Параметр | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ADMIN_ID` | Ваш Telegram ID (узнайте через [@userinfobot](https://t.me/userinfobot)) |
| `CHANNEL_ID` | ID или @username канала для подписки |
| `CHANNEL_LINK` | Ссылка на канал (https://t.me/...) |
| `SCHEDULE_CHANNEL_ID` | ID или @username канала для расписания |

**Важно:** добавьте бота администратором в оба канала, чтобы он мог проверять подписку и публиковать сообщения.

### 4. Запуск

```bash
python bot.py
```

## Использование

### Для клиентов

1. `/start` — главное меню
2. **Записаться** — выбор даты → времени → имя → телефон → подтверждение
3. **Моя запись** — просмотр текущей записи
4. **Отменить запись** — отмена с освобождением слота
5. **Прайсы** — прайс-лист
6. **Портфолио** — ссылка на Pinterest

### Для администратора

Кнопка **Админ-панель** (видна только ADMIN_ID):

- **Добавить рабочий день** — выбор даты + стандартные слоты
- **Добавить слот** — произвольное время на дату
- **Удалить слот** — удаление свободного слота
- **Отменить запись клиента** — отмена с уведомлением клиента
- **Закрыть день** — полное закрытие дня
- **Просмотр расписания** — расписание на выбранную дату

## Особенности

- Один пользователь — одна активная запись
- При отмене слот автоматически освобождается
- Напоминание за 24 часа (APScheduler, восстанавливается после перезапуска)
- Обязательная подписка на канал перед записью
- Расписание формируется на 31 день вперёд
- HTML-форматирование всех сообщений
=======
# Manicure Booking Telegram Bot 💅

A feature-rich Telegram bot designed to automate appointment booking and schedule management for manicure services.

### Features

- **Appointment Booking:** Interactive calendar with available dates and time slots.
- **Automated Scheduling:** Monthly availability management with automatic slot reservation.
- **Customer Management:** Collects customer names and phone numbers.
- **Booking Cancellation:** Allows customers to cancel appointments and makes cancelled slots available again.
- **Admin Panel:** Manage working days, time slots, appointments, and daily schedules.
- **Appointment Notifications:** Automatically sends booking details to the administrator and updates a dedicated Telegram channel.
- **Automated Reminders:** Sends appointment reminders 24 hours before scheduled visits.
- **Service Pricing:** Displays available services and their prices.
- **Portfolio:** Provides direct access to the service portfolio.
- **Channel Subscription Verification:** Requires users to subscribe to a specified Telegram channel before booking.

### Tech Stack

- Python
- aiogram
- SQLite
- APScheduler
- FSM (Finite State Machine)
- Telegram Bot API
- HTML message formatting

### Key Highlights

- Structured, modular project architecture.
- Database-backed appointment management.
- Prevention of duplicate bookings and multiple active appointments per customer.
- Automatic restoration of scheduled reminders after bot restarts.
- Role-based administrator access.
- Interactive inline keyboard interface.

**Purpose:** To simplify appointment management, reduce manual communication, and provide a convenient booking experience for both customers and service providers.
>>>>>>> 0dd1d096b6033f822d114052f8c8f236e96e3629
