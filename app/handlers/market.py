from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..keyboards.inline import market_item_keyboard, market_page_keyboard, main_menu_keyboard
from ..services.market import get_market, get_market_item, remove_from_market
from ..services.smokes import transfer_smoke
from ..services.users import get_balance, update_balance

router = Router()


@router.callback_query(F.data == "shop")
async def callback_shop(callback: CallbackQuery) -> None:
    await callback.answer()
    items = list(get_market())
    if not items:
        await callback.message.edit_text("🛒 Маркет пуст.", reply_markup=main_menu_keyboard())
        return
    await callback.message.edit_text(
        "🛒 Маркет сигар (стр. 1):",
        reply_markup=market_page_keyboard(items, page=1),
    )


@router.callback_query(F.data.startswith("market_page_"))
async def callback_market_page(callback: CallbackQuery) -> None:
    await callback.answer()
    page = int(callback.data.split("_")[-1])
    items = list(get_market())
    await callback.message.edit_text(
        f"🛒 Маркет сигар (стр. {page}):",
        reply_markup=market_page_keyboard(items, page=page),
    )


@router.callback_query(F.data.startswith("market_"))
async def callback_market_item(callback: CallbackQuery) -> None:
    await callback.answer()
    parts = callback.data.split("_")
    if len(parts) < 2 or parts[1] == "page" or not parts[-1].isdigit():
        return
    smoke_id = int(parts[-1])
    item = get_market_item(smoke_id)
    if not item:
        await callback.message.edit_text("❌ Сигара недоступна.", reply_markup=main_menu_keyboard())
        return
    _, price, owner_id, name, description = item
    is_owner = callback.from_user.id == owner_id
    await callback.message.edit_text(
        f"🚬 <b>{name}</b>\n\n📝 {description}\n💵 Цена: {price}",
        reply_markup=market_item_keyboard(smoke_id, is_owner),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith("buyitem_"))
async def callback_buy(callback: CallbackQuery) -> None:
    await callback.answer()
    parts = callback.data.split("_")
    if len(parts) != 2 or not parts[1].isdigit():
        await callback.answer("Неверные данные.", show_alert=True)
        return
    smoke_id = int(parts[1])
    item = get_market_item(smoke_id)
    if not item:
        await callback.message.answer("❌ Эта сигара уже куплена.")
        return
    _, price, owner_id, name, description = item
    buyer_id = callback.from_user.id
    if buyer_id == owner_id:
        await callback.message.answer("❌ Вы не можете купить свою же сигару.")
        return
    balance = get_balance(buyer_id)
    if balance < price:
        await callback.message.answer("❌ У вас недостаточно денег.")
        return
    update_balance(buyer_id, -price)
    update_balance(owner_id, price)
    transfer_smoke(smoke_id, buyer_id)
    await callback.message.answer(f"✅ Вы купили 🚬 {name} #{smoke_id} за {price}💵!")
    try:
        buyer_username = callback.from_user.username or str(buyer_id)
        await callback.bot.send_message(
            owner_id,
            f"💸 Ваша сигара 🚬 {name} была куплена @{buyer_username} за {price}💵. Деньги зачислены.",
        )
    except Exception:  # pragma: no cover - network errors
        pass


@router.callback_query(F.data.startswith("remove_"))
async def callback_remove_from_market(callback: CallbackQuery) -> None:
    await callback.answer()
    smoke_id = int(callback.data.split("_")[-1])
    item = get_market_item(smoke_id)
    if not item:
        await callback.message.answer("❌ Сигара не найдена.")
        return
    _, _, owner_id, name, _ = item
    if owner_id != callback.from_user.id:
        await callback.message.answer("⛔ Вы не продавец этой сигары.")
        return
    remove_from_market(smoke_id)
    await callback.message.answer(f"✅ Сигара 🚬 {name} снята с продажи.")
