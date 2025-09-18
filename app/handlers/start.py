from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from ..keyboards.inline import main_menu_keyboard, start_keyboard
from ..services.users import add_user, get_balance, update_username

router = Router()


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    add_user(message.from_user.id, message.from_user.username)
    update_username(message.from_user.id, message.from_user.username)
    await message.answer("👋 Привет! Добро пожаловать в Smoke Idle!", reply_markup=start_keyboard)


@router.callback_query(F.data == "start_game")
async def callback_start_game(callback: CallbackQuery) -> None:
    await callback.answer()
    balance = get_balance(callback.from_user.id)
    await callback.message.edit_text(
        f"🏠 Главное меню\n\n💵 Баланс: <b>{balance}</b>",
        reply_markup=main_menu_keyboard(balance),
        parse_mode='HTML'
    )
