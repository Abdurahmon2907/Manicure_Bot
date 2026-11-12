"""FSM-состояния процесса записи."""

from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    """Состояния пользовательской записи."""

    choosing_date = State()      # Выбор даты
    choosing_time = State()      # Выбор времени
    entering_name = State()      # Ввод имени
    entering_phone = State()     # Ввод телефона
    confirming = State()         # Подтверждение
