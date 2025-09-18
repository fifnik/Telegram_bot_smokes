import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..keyboards.inline import gift_smokes_keyboard, main_menu_keyboard
from ..services.smokes import get_smoke, get_user_smokes, transfer_smoke
from ..services.users import get_user_id_by_username
from ..states import GiftSmoke

router = Router()


@router.callback_query(F.data == "gift")
async def callback_gift(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text("🎁 Введите username получателя (без @):")
    await state.set_state(GiftSmoke.waiting_for_username)


@router.message(GiftSmoke.waiting_for_username)
async def process_gift_username(message: Message, state: FSMContext) -> None:
    username = (message.text or "").strip().lstrip("@")
    if not username:
        await message.answer("❌ Укажите корректный username.")
        return
    receiver_id = get_user_id_by_username(username)
    if receiver_id is None:
        await message.answer("❌ Пользователь не найден. Попробуйте снова.")
        return
    if receiver_id == message.from_user.id:
        await message.answer("❌ Нельзя подарить самому себе.")
        return
    smokes = list(get_user_smokes(message.from_user.id))
    if not smokes:
        await message.answer("❌ У вас нет сигар для подарка.", reply_markup=main_menu_keyboard())
        await state.clear()
        return
    await state.update_data(receiver_id=receiver_id, receiver_username=username)
    await state.set_state(GiftSmoke.waiting_for_smoke)
    await message.answer(
        f"🎁 Выберите сигару, которую хотите подарить пользователю @{username}:",
        reply_markup=gift_smokes_keyboard(list(smokes), page=1),
    )


@router.callback_query(F.data.startswith("gift_page_"))
async def callback_gift_page(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    parts = callback.data.split("_")
    if len(parts) != 3 or not parts[-1].isdigit():
        return
    page = int(parts[-1])
    smokes = list(get_user_smokes(callback.from_user.id))
    await callback.message.edit_text(
        f"🎁 Выберите сигару (стр. {page}):",
        reply_markup=gift_smokes_keyboard(list(smokes), page=page),
    )


@router.callback_query(F.data.startswith("gift_smoke_"))
async def callback_gift_smoke(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    parts = callback.data.split("_")
    if len(parts) < 3 or not parts[-1].isdigit():
        await callback.answer("Ошибка данных.", show_alert=True)
        return
    smoke_id = int(parts[-1])
    data = await state.get_data()
    receiver_id = data.get("receiver_id")
    if receiver_id is None:
        await callback.message.answer("❌ Получатель не найден.")
        await state.clear()
        return
    smoke = get_smoke(smoke_id)
    if not smoke or smoke[1] != callback.from_user.id or smoke[4] == 1:
        await callback.message.answer("❌ Эта сигара недоступна для подарка.")
        return
    transfer_smoke(smoke_id, receiver_id)
    await state.clear()
    await callback.message.answer("✅ Сигара успешно подарена!", reply_markup=main_menu_keyboard())
    try:
        await callback.bot.send_message(receiver_id, f"🎁 Вам подарили сигару 🚬 {smoke[2]}! 🎉")
    except Exception:  # pragma: no cover - network errors
        logging.warning("Не удалось отправить уведомление получателю")
