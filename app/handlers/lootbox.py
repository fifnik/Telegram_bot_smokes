import time

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..keyboards.inline import main_menu_keyboard
from ..services.smokes import create_smoke, get_smoke
from ..services.users import get_balance, get_last_free_box, set_last_free_box, update_balance

router = Router()


@router.callback_query(F.data == "free_box")
async def callback_free_box(callback: CallbackQuery) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    now = int(time.time())
    last = get_last_free_box(user_id)
    if now - last < 86400:
        remain = 86400 - (now - last)
        hours = remain // 3600
        minutes = (remain % 3600) // 60
        await callback.message.edit_text(
            f"⏳ Бесплатный лутбокс будет доступен через {hours}ч {minutes}м.",
            reply_markup=main_menu_keyboard(),
        )
        return
    smoke_id = create_smoke(user_id)
    set_last_free_box(user_id, now)
    smoke = get_smoke(smoke_id)
    name, description = (smoke[2], smoke[3]) if smoke else (f"Сигара #{smoke_id}", "Описание недоступно")
    await callback.message.edit_text(
        f"🎁 Вы открыли бесплатный лутбокс!\nВам выпала {name}\n📝 {description}",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "buy_box")
async def callback_buy_box(callback: CallbackQuery) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    price = 500
    balance = get_balance(user_id)
    if balance < price:
        await callback.message.edit_text(
            "❌ Недостаточно денег для покупки лутбокса.",
            reply_markup=main_menu_keyboard(),
        )
        return
    update_balance(user_id, -price)
    smoke_id = create_smoke(user_id)
    smoke = get_smoke(smoke_id)
    name, description = (smoke[2], smoke[3]) if smoke else (f"Сигара #{smoke_id}", "Описание недоступно")
    await callback.message.edit_text(
        f"💰 Вы купили лутбокс за {price}💵!\nВам выпала {name}\n📝 {description}",
        reply_markup=main_menu_keyboard(),
    )
