"""
Модуль работы с SQLite базой данных.
"""

import aiosqlite
from datetime import date, datetime, timedelta
from typing import Optional

import config


class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path

    async def connect(self) -> None:
        """Создание таблиц при первом подключении."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS work_days (
                    date TEXT PRIMARY KEY,
                    is_closed INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS time_slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    is_available INTEGER DEFAULT 1,
                    UNIQUE(date, time)
                );

                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    slot_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    reminder_job_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (slot_id) REFERENCES time_slots(id)
                );
            """)
            # Исправление слотов, сохранённых без минут ("09" -> "09:00")
            await db.execute(
                "UPDATE OR IGNORE time_slots SET time = time || ':00' WHERE time NOT LIKE '%:%'"
            )
            await db.execute(
                "UPDATE bookings SET time = time || ':00' WHERE time NOT LIKE '%:%'"
            )
            await db.commit()

    # ── Рабочие дни ──────────────────────────────────────────────

    async def add_work_day(self, day: date) -> bool:
        """Добавить рабочий день. Возвращает False, если день уже существует."""
        date_str = day.isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO work_days (date, is_closed) VALUES (?, 0)",
                    (date_str,),
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def close_work_day(self, day: date) -> None:
        """Полностью закрыть рабочий день."""
        date_str = day.isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE work_days SET is_closed = 1 WHERE date = ?",
                (date_str,),
            )
            await db.execute(
                "UPDATE time_slots SET is_available = 0 WHERE date = ?",
                (date_str,),
            )
            await db.commit()

    async def is_day_closed(self, day: date) -> bool:
        """Проверить, закрыт ли день."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT is_closed FROM work_days WHERE date = ?",
                (day.isoformat(),),
            )
            row = await cursor.fetchone()
            return bool(row and row[0])

    async def get_available_dates(
        self, start: date, end: date
    ) -> list[date]:
        """Получить даты с хотя бы одним свободным слотом."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT DISTINCT ts.date
                FROM time_slots ts
                JOIN work_days wd ON wd.date = ts.date
                WHERE ts.date BETWEEN ? AND ?
                  AND ts.is_available = 1
                  AND wd.is_closed = 0
                ORDER BY ts.date
                """,
                (start.isoformat(), end.isoformat()),
            )
            rows = await cursor.fetchall()
            return [date.fromisoformat(r[0]) for r in rows]

    # ── Временные слоты ──────────────────────────────────────────

    async def add_time_slot(self, day: date, time_str: str) -> bool:
        """Добавить временной слот на дату (создаёт рабочий день, если его нет)."""
        async with aiosqlite.connect(self.db_path) as db:
            # Автоматически создаём рабочий день, если его ещё нет
            await db.execute(
                "INSERT OR IGNORE INTO work_days (date, is_closed) VALUES (?, 0)",
                (day.isoformat(),),
            )
            try:
                await db.execute(
                    "INSERT INTO time_slots (date, time, is_available) VALUES (?, ?, 1)",
                    (day.isoformat(), time_str),
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def remove_time_slot(self, slot_id: int) -> bool:
        """Удалить слот, если он не занят записью."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id FROM bookings WHERE slot_id = ?", (slot_id,)
            )
            if await cursor.fetchone():
                return False
            await db.execute("DELETE FROM time_slots WHERE id = ?", (slot_id,))
            await db.commit()
            return True

    async def get_available_slots(self, day: date) -> list[dict]:
        """Получить свободные слоты на дату."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, time FROM time_slots
                WHERE date = ? AND is_available = 1
                ORDER BY time
                """,
                (day.isoformat(),),
            )
            rows = await cursor.fetchall()
            return [{"id": r[0], "time": r[1]} for r in rows]

    async def get_all_slots_for_date(self, day: date) -> list[dict]:
        """Получить все слоты на дату (для админ-панели)."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT ts.id, ts.time, ts.is_available,
                       b.client_name, b.phone, b.user_id, b.id as booking_id
                FROM time_slots ts
                LEFT JOIN bookings b ON b.slot_id = ts.id
                WHERE ts.date = ?
                ORDER BY ts.time
                """,
                (day.isoformat(),),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "time": r[1],
                    "is_available": bool(r[2]),
                    "client_name": r[3],
                    "phone": r[4],
                    "user_id": r[5],
                    "booking_id": r[6],
                }
                for r in rows
            ]

    async def set_slot_available(self, slot_id: int, available: bool) -> None:
        """Изменить доступность слота."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE time_slots SET is_available = ? WHERE id = ?",
                (int(available), slot_id),
            )
            await db.commit()

    async def get_slot_by_id(self, slot_id: int) -> Optional[dict]:
        """Получить слот по ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, date, time, is_available FROM time_slots WHERE id = ?",
                (slot_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "date": row[1],
                "time": row[2],
                "is_available": bool(row[3]),
            }

    # ── Записи ───────────────────────────────────────────────────

    async def get_user_booking(self, user_id: int) -> Optional[dict]:
        """Получить активную запись пользователя."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, slot_id, date, time, client_name, phone, reminder_job_id
                FROM bookings WHERE user_id = ?
                """,
                (user_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "slot_id": row[1],
                "date": row[2],
                "time": row[3],
                "client_name": row[4],
                "phone": row[5],
                "reminder_job_id": row[6],
            }

    async def create_booking(
        self,
        user_id: int,
        slot_id: int,
        day: date,
        time_str: str,
        client_name: str,
        phone: str,
        reminder_job_id: Optional[str] = None,
    ) -> Optional[int]:
        """
        Создать запись. Возвращает ID записи или None при ошибке.
        Один пользователь — одна запись (UNIQUE constraint на user_id).
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, что слот свободен
            cursor = await db.execute(
                "SELECT is_available FROM time_slots WHERE id = ?",
                (slot_id,),
            )
            slot = await cursor.fetchone()
            if not slot or not slot[0]:
                return None

            try:
                cursor = await db.execute(
                    """
                    INSERT INTO bookings
                        (user_id, slot_id, date, time, client_name, phone, reminder_job_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        slot_id,
                        day.isoformat(),
                        time_str,
                        client_name,
                        phone,
                        reminder_job_id,
                    ),
                )
                await db.execute(
                    "UPDATE time_slots SET is_available = 0 WHERE id = ?",
                    (slot_id,),
                )
                await db.commit()
                return cursor.lastrowid
            except aiosqlite.IntegrityError:
                return None

    async def cancel_booking(self, user_id: int) -> Optional[dict]:
        """
        Отменить запись пользователя.
        Возвращает данные отменённой записи (включая reminder_job_id и slot_id).
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, slot_id, date, time, client_name, phone, reminder_job_id
                FROM bookings WHERE user_id = ?
                """,
                (user_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return None

            booking = {
                "id": row[0],
                "slot_id": row[1],
                "date": row[2],
                "time": row[3],
                "client_name": row[4],
                "phone": row[5],
                "reminder_job_id": row[6],
            }

            await db.execute(
                "DELETE FROM bookings WHERE user_id = ?", (user_id,)
            )
            await db.execute(
                "UPDATE time_slots SET is_available = 1 WHERE id = ?",
                (booking["slot_id"],),
            )
            await db.commit()
            return booking

    async def admin_cancel_booking(self, booking_id: int) -> Optional[dict]:
        """Отменить запись администратором по ID записи."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, user_id, slot_id, date, time, client_name, phone, reminder_job_id
                FROM bookings WHERE id = ?
                """,
                (booking_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return None

            booking = {
                "id": row[0],
                "user_id": row[1],
                "slot_id": row[2],
                "date": row[3],
                "time": row[4],
                "client_name": row[5],
                "phone": row[6],
                "reminder_job_id": row[7],
            }

            await db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
            await db.execute(
                "UPDATE time_slots SET is_available = 1 WHERE id = ?",
                (booking["slot_id"],),
            )
            await db.commit()
            return booking

    async def update_reminder_job_id(
        self, booking_id: int, job_id: Optional[str]
    ) -> None:
        """Обновить ID задачи напоминания."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE bookings SET reminder_job_id = ? WHERE id = ?",
                (job_id, booking_id),
            )
            await db.commit()

    async def get_bookings_for_reminder_restore(self) -> list[dict]:
        """
        Получить записи, для которых нужно восстановить напоминания
        (визит более чем через 24 часа).
        """
        now = datetime.now()
        threshold = now + timedelta(hours=24)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, user_id, date, time, reminder_job_id
                FROM bookings
                """
            )
            rows = await cursor.fetchall()

        result = []
        for row in rows:
            booking_id, user_id, date_str, time_str, job_id = row
            visit_dt = datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )
            if visit_dt > threshold:
                result.append({
                    "id": booking_id,
                    "user_id": user_id,
                    "date": date_str,
                    "time": time_str,
                    "reminder_job_id": job_id,
                    "visit_datetime": visit_dt,
                })
        return result
