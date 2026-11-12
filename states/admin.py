"""FSM-состояния админ-панели."""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Состояния администратора."""

    choosing_date_add_day = State()       # Выбор даты для добавления рабочего дня
    choosing_date_add_slot = State()      # Выбор даты для добавления слота
    entering_slot_time = State()          # Ввод времени нового слота
    choosing_date_remove_slot = State()   # Выбор даты для удаления слота
    choosing_slot_to_remove = State()     # Выбор слота для удаления
    choosing_date_close = State()         # Выбор даты для закрытия
    choosing_date_view = State()          # Выбор даты для просмотра
    choosing_date_cancel = State()        # Выбор даты для отмены записи
    choosing_booking_to_cancel = State()  # Выбор записи для отмены
