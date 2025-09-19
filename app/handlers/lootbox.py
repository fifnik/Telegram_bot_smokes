import sqlite3
import random
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..keyboards.inline import main_menu_keyboard, boxes_menu_kb
from ..services.smokes import create_smoke
from ..services.users import (
    get_balance,
    get_last_free_box,
    set_last_free_box,
    update_balance,
)

router = Router()


# === Меню выбора боксов ===
@router.callback_query(F.data == "boxes")
async def cb_boxes(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🎁 Выберите лутбокс:",
        reply_markup=boxes_menu_kb()
    )


# === Универсальная функция покупки бокса ===
async def buy_box_generic(callback: CallbackQuery, price: int, rarity_table: list, DB_PATH=None):
    user_id = callback.from_user.id
    balance = get_balance(user_id)

    # Проверка на баланс
    if balance < price:
        await callback.answer("❌ Недостаточно средств!", show_alert=True)
        return

    # Списываем деньги, если бокс платный
    if price > 0:
        update_balance(user_id, -price)

    # Определяем редкость по шансам
    roll = random.randint(1, 100)
    acc = 0
    rarity = "обычная"
    for r, chance in rarity_table:
        acc += chance
        if roll <= acc:
            rarity = r
            break

    # Создаём сигару
    smoke_id = create_smoke(user_id, rarity=rarity)

    # Достаём инфу из БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, description FROM smokes WHERE id=?", (smoke_id,))
    row = cur.fetchone()
    conn.close()

    # Сообщение о награде
    if row:
        await callback.message.edit_text(
            f"🎉 Вы получили сигару:\n\n"
            f"🚬 {row[0]}\n"
            f"📜 {row[1]}\n\n"
            f"Редкость: {rarity}",
            reply_markup=main_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "⚠️ Ошибка при создании сигары.",
            reply_markup=main_menu_keyboard()
        )


# === Лутбоксы ===

@router.callback_query(F.data == "box_free")
async def free_box(callback: CallbackQuery):
    """Бесплатный бокс (раз в сутки)"""
    user_id = callback.from_user.id

    last_time = get_last_free_box(user_id)
    if last_time and time.time() - last_time < 86400:  # 24 часа
        await callback.answer("⏳ Бесплатный лутбокс доступен раз в сутки!", show_alert=True)
        return

    set_last_free_box(user_id, time.time())
    await buy_box_generic(callback, price=0, rarity_table=[
        ("😶‍🌫️ Обычная", 60),
        ("😨 Редкая", 25),
        ("😱 Легендарная", 9),
        ("🤩 Мифическая", 3),
        ("🤯 Интересная", 3)
    ])


@router.callback_query(F.data == "buy_box_common")
async def paid_box(callback: CallbackQuery):
    """Обычный платный бокс (500💰)"""
    await buy_box_generic(callback, price=50, rarity_table=[
        ("😶‍🌫️ Обычная", 60),
        ("😨 Редкая", 25),
        ("😱 Легендарная", 9),
        ("🤩 Мифическая", 3),
        ("🤯 Интересная", 2),
        ("🌿 Секретная", 1),
    ])


@router.callback_query(F.data == "buy_box_premium")
async def premium_box(callback: CallbackQuery):
    """Премиум бокс (2000💰)"""
    await buy_box_generic(callback, price=100, rarity_table=[
        ("😶‍🌫️ Обычная", 58),
        ("😨 Редкая", 25),
        ("😱 Легендарная", 9),
        ("🤩 Мифическая", 3),
        ("🤯 Интересная", 3),
        ("🌿 Секретная", 2)
    ])


@router.callback_query(F.data == "buy_box_elite")
async def vip_box(callback: CallbackQuery):
    """VIP бокс (5000💰)"""
    await buy_box_generic(callback, price=200, rarity_table=[
        ("😶‍🌫️ Обычная", 55),
        ("😨 Редкая", 25),
        ("😱 Легендарная", 9),
        ("🤩 Мифическая", 3),
        ("🤯 Интересная", 5),
        ("🌿 Секретная", 3)
    ])

@router.callback_query(F.data == "buy_box_event")
async def event_box(callback: CallbackQuery):
    """VIP бокс (5000💰)"""
    await buy_box_generic(callback, price=500, rarity_table=[
        ("😶‍🌫️ Обычная", 53),
        ("😨 Редкая", 25),
        ("😱 Легендарная", 9),
        ("🤩 Мифическая", 3),
        ("🤯 Интересная", 5),
        ("🌿 Секретная", 3),
        ('🔞 Ганджубас', 2)
    ])
