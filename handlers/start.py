"""
Обработчики команды /start, главного меню, прайсов и портфолио.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import config
from keyboards.main import back_to_menu_kb, main_menu_kb, portfolio_kb
from utils.messages import prices_text, welcome_text

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обработка команды /start."""
    await state.clear()
    name = message.from_user.first_name or "друг"
    await message.answer(
        welcome_text(name),
        reply_markup=main_menu_kb(is_admin=_is_admin(message.from_user.id)),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в главное меню."""
    await state.clear()
    name = callback.from_user.first_name or "друг"
    await callback.message.edit_text(
        welcome_text(name),
        reply_markup=main_menu_kb(is_admin=_is_admin(callback.from_user.id)),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "prices")
async def show_prices(callback: CallbackQuery) -> None:
    """Показать прайс-лист (без FSM)."""
    await callback.message.edit_text(
        prices_text(),
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "portfolio")
async def show_portfolio(callback: CallbackQuery) -> None:
    """Показать портфолио с inline-кнопкой (без FSM)."""
    await callback.message.edit_text(
        "🖼 <b>Портфолио мастера</b>\n\n"
        "Нажмите кнопку ниже, чтобы посмотреть работы:",
        reply_markup=portfolio_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery) -> None:
    """Пустой callback для неактивных кнопок календаря."""
    await callback.answer()
