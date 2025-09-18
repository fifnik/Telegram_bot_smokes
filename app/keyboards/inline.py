from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..utils.pagination import paginate


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="▶️ Начать", callback_data="start_game")]]
)


def main_menu_keyboard(balance: int | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    buttons = [
        ('💰 Пополнить', 'topup'),
        ('🏆 Leaders', 'leaders'),
        ('🚬 Smokes', 'smokes'),
        ('🛒 Shop', 'shop'),
        ('🎁 Бесплатный лутбокс', 'free_box'),
        ('💰 Купить лутбокс (500💵)', 'buy_box'),
        ('🎁 Подарить', 'gift')
    ]

    for text, call_data in buttons:
        builder.button(text=text, callback_data=call_data)

    builder.adjust(2, 2, 2, 1)

    markup = builder.as_markup()
    return markup

def gift_smokes_keyboard(smokes: list[tuple[int, str]], page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    items, total = paginate(smokes, page, per_page)
    for smoke_id, name in items:
        keyboard.append(
            [InlineKeyboardButton(text=f"🚬 {name}", callback_data=f"gift_smoke_{smoke_id}")]
        )
    pages = (total + per_page - 1) // per_page or 1
    nav_row: list[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"gift_page_{page-1}"))
    if page < pages:
        nav_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"gift_page_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="start_game")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def smokes_page_keyboard(
    smokes: list[tuple[int, str]],
    sale_smokes: list[tuple[int, str, int]],
    page: int,
    per_page: int = 5,
) -> InlineKeyboardMarkup:
    combined: list[tuple] = [("inv", sid, name) for sid, name in smokes]
    combined.extend(("sale", sid, name, price) for sid, name, price in sale_smokes)
    keyboard: list[list[InlineKeyboardButton]] = []
    items, total = paginate(combined, page, per_page)
    for item in items:
        if item[0] == "inv":
            _, sid, name = item
            keyboard.append(
                [InlineKeyboardButton(text=f"🚬 {name}", callback_data=f"my_smoke_{sid}")]
            )
        else:
            _, sid, name, price = item
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"🚬 {name} [В продаже {price}💵]",
                        callback_data=f"market_{sid}",
                    ),
                    InlineKeyboardButton(text="❌ Снять", callback_data=f"unsell_{sid}"),
                ]
            )
    pages = (total + per_page - 1) // per_page or 1
    nav_row: list[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"smokes_page_{page-1}"))
    if page < pages:
        nav_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"smokes_page_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start_game")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def smoke_item_keyboard(smoke_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💵 Продать", callback_data=f"sell_{smoke_id}")],
            [InlineKeyboardButton(text="✏️ Изменить описание (100💵)", callback_data=f"change_desc_{smoke_id}")],
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="smokes")],
        ]
    )


def market_item_keyboard(smoke_id: int, owner: bool) -> InlineKeyboardMarkup:
    if owner:
        inline_keyboard = [
            [InlineKeyboardButton(text="❌ Снять с продажи", callback_data=f"remove_{smoke_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="shop")],
        ]
    else:
        inline_keyboard = [
            [InlineKeyboardButton(text="💵 Купить", callback_data=f"buyitem_{smoke_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="shop")],
        ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def market_page_keyboard(items: list[tuple[int, int, str, str]], page: int, per_page: int = 5) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    page_items, total = paginate(items, page, per_page)
    for smoke_id, price, username, name in page_items:
        username_display = username or "unknown"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"🚬 {name} — {price}💵 (от @{username_display})",
                    callback_data=f"market_{smoke_id}",
                )
            ]
        )
    pages = (total + per_page - 1) // per_page or 1
    nav_row: list[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"market_page_{page-1}"))
    if page < pages:
        nav_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"market_page_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start_game")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
