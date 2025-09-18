from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..keyboards.inline import main_menu_keyboard
from ..services.users import get_balance, update_balance
from ..states import TopUp

router = Router()


@router.callback_query(F.data == "topup")
async def callback_topup(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text("💵 Введите сумму пополнения (целое число):")
    await state.set_state(TopUp.waiting_for_amount)


@router.message(TopUp.waiting_for_amount)
async def process_topup(message: Message, state: FSMContext) -> None:
    try:
        amount = int(message.text)
    except (TypeError, ValueError):
        await message.answer("❌ Нужно ввести число.")
        return
    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше 0.")
        return
    update_balance(message.from_user.id, amount)
    await state.clear()
    balance = get_balance(message.from_user.id)
    await message.answer(
        f"✅ Баланс пополнен на {amount}.\n💵 Текущий баланс: {balance}",
        reply_markup=main_menu_keyboard(balance),
    )
