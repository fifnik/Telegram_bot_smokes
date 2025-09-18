from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..keyboards.inline import main_menu_keyboard, smoke_item_keyboard, smokes_page_keyboard
from ..services.market import add_to_market, get_market_item, remove_from_market
from ..services.smokes import create_smoke, get_smoke, get_user_sale_smokes, get_user_smokes, update_description
from ..services.users import get_balance, update_balance
from ..states import ChangeDescription, SellSmoke

router = Router()


@router.callback_query(F.data == "smokes")
async def callback_smokes(callback: CallbackQuery) -> None:
    await callback.answer()
    smokes = list(get_user_smokes(callback.from_user.id))
    sale_smokes = list(get_user_sale_smokes(callback.from_user.id))
    if not smokes and not sale_smokes:
        new_id = create_smoke(callback.from_user.id)
        await callback.message.edit_text(f"🎉 Вы получили первую сигару! 🚬 #{new_id}")
        smokes = list(get_user_smokes(callback.from_user.id))
        sale_smokes = list(get_user_sale_smokes(callback.from_user.id))
    await callback.message.edit_text(
        "🚬 Ваши Smokes (стр. 1):",
        reply_markup=smokes_page_keyboard(smokes, sale_smokes, page=1),
    )


@router.callback_query(F.data.startswith("smokes_page_"))
async def callback_smokes_page(callback: CallbackQuery) -> None:
    await callback.answer()
    page = int(callback.data.split("_")[-1])
    smokes = list(get_user_smokes(callback.from_user.id))
    sale_smokes = list(get_user_sale_smokes(callback.from_user.id))
    await callback.message.edit_text(
        f"🚬 Ваши Smokes (стр. {page}):",
        reply_markup=smokes_page_keyboard(smokes, sale_smokes, page=page),
    )


@router.callback_query(F.data.startswith("my_smoke_"))
async def callback_my_smoke(callback: CallbackQuery) -> None:
    await callback.answer()
    smoke_id = int(callback.data.split("_")[-1])
    smoke = get_smoke(smoke_id)
    if not smoke or smoke[1] != callback.from_user.id:
        await callback.message.edit_text("❌ Эта сигара не принадлежит вам.")
        return
    _, _, name, description, is_for_sale = smoke
    if is_for_sale:
        item = get_market_item(smoke_id)
        price = item[1] if item else "?"
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Снять с продажи", callback_data=f"unsell_{smoke_id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="smokes")],
            ]
        )
        await callback.message.edit_text(
            f"🚬 <b>{name}</b>\n\n📝 {description}\n\n💵 На продаже: {price}💵",
            reply_markup=markup,
            parse_mode='HTML'
        )
    else:
        await callback.message.edit_text(
            f"🚬 <b>{name}</b>\n\n📝 {description}",
            reply_markup=smoke_item_keyboard(smoke_id),
            parse_mode='HTML'
        )


@router.callback_query(F.data.startswith("sell_"))
async def callback_sell_smoke(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    smoke_id = int(callback.data.split("_")[-1])
    smoke = get_smoke(smoke_id)
    if not smoke or smoke[1] != callback.from_user.id:
        await callback.message.answer("❌ Сигара не найдена или не ваша.")
        return
    if smoke[4] == 1:
        await callback.message.answer("❌ Сигара уже выставлена.")
        return
    await state.update_data(smoke_id=smoke_id)
    await callback.message.answer("💵 Введите цену для сигары (целое число):")
    await state.set_state(SellSmoke.waiting_for_price)


@router.message(SellSmoke.waiting_for_price)
async def process_sell_price(message: Message, state: FSMContext) -> None:
    try:
        price = int(message.text)
    except (TypeError, ValueError):
        await message.answer("❌ Нужно число.")
        return
    if price <= 0:
        await message.answer("❌ Цена должна быть больше 0.")
        return
    data = await state.get_data()
    smoke_id = data.get("smoke_id")
    if smoke_id is None:
        await message.answer("❌ Внутренняя ошибка.")
        await state.clear()
        return
    success, error_message = add_to_market(smoke_id, price, message.from_user.id)
    await state.clear()
    if not success:
        await message.answer(f"❌ Не удалось: {error_message}")
        return
    await message.answer(
        f"✅ Сигара #{smoke_id} выставлена за {price}💵.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("unsell_"))
async def callback_unsell(callback: CallbackQuery) -> None:
    await callback.answer()
    smoke_id = int(callback.data.split("_")[-1])
    item = get_market_item(smoke_id)
    if not item:
        await callback.message.answer("❌ Сигара не найдена в маркете.")
        return
    _, _, seller_id, _, _ = item
    if seller_id != callback.from_user.id:
        await callback.message.answer("⛔ Это не ваша сигара.")
        return
    remove_from_market(smoke_id)
    smokes = list(get_user_smokes(callback.from_user.id))
    sale_smokes = list(get_user_sale_smokes(callback.from_user.id))
    await callback.message.edit_text(
        "🚬 Ваши Smokes (стр. 1):",
        reply_markup=smokes_page_keyboard(smokes, sale_smokes, page=1),
    )


@router.callback_query(F.data.startswith("change_desc_"))
async def callback_change_description(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    smoke_id = int(callback.data.split("_")[-1])
    smoke = get_smoke(smoke_id)
    if not smoke or smoke[1] != callback.from_user.id:
        await callback.message.answer("❌ Эта сигара не принадлежит вам.")
        return
    balance = get_balance(callback.from_user.id)
    if balance < 100:
        await callback.message.answer("❌ Недостаточно средств для изменения описания (нужно 100💵).")
        return
    update_balance(callback.from_user.id, -100)
    await state.update_data(smoke_id=smoke_id)
    await callback.message.answer("✏️ Введите новое описание для сигары:")
    await state.set_state(ChangeDescription.waiting_for_text)


@router.message(ChangeDescription.waiting_for_text)
async def process_change_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    smoke_id = data.get("smoke_id")
    if smoke_id is None:
        await message.answer("❌ Внутренняя ошибка.")
        await state.clear()
        return
    text = (message.text or "").strip()
    if len(text) < 3:
        await message.answer("❌ Описание слишком короткое.")
        return
    if len(text) > 200:
        await message.answer("❌ Описание слишком длинное (макс. 200 символов).")
        return
    update_description(smoke_id, text)
    await state.clear()
    await message.answer(f"✅ Описание для сигары #{smoke_id} успешно изменено!", reply_markup=main_menu_keyboard())
