from __future__ import annotations

import random
from typing import Optional, Sequence, Tuple

from ..database import get_connection

SMOKE_DESCRIPTIONS = [
    "Классическая сигара, идеально подходит для новичков.",
    "Аромат ванили и крепкого табака.",
    "Редкая сигара с насыщенным вкусом.",
    "Легендарная сигара, ценится среди коллекционеров.",
    "Сигара, приносящая удачу своему владельцу.",
    "Экзотическая сигара с мягким дымом.",
    "С лёгким дымом, дорогой друг.",
    "Получше всяких вейпов!",
    "Элитная сигара премиум-класса.",
]

RARITY_TABLE = [
    ("😶‍🌫️ Обычная", 70),
    ("😨 Редкая", 20),
    ("😱 Легендарная", 9),
    ("🤩 Мифическая", 1),
]


def roll_rarity() -> str:
    roll = random.randint(1, 100)
    cumulative = 0
    for rarity, chance in RARITY_TABLE:
        cumulative += chance
        if roll <= cumulative:
            return rarity
    return "🟢 Обычная"


def create_smoke(owner_id: int, rarity: Optional[str] = None) -> int:
    rarity_value = rarity or roll_rarity()
    description = random.choice(SMOKE_DESCRIPTIONS)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO smokes (owner_id, name, description, rarity) VALUES (?, ?, ?, ?)",
            (owner_id, "temp", description, rarity_value),
        )
        smoke_id = cur.lastrowid
        name = f"{rarity_value} сигара #{smoke_id}"
        cur.execute("UPDATE smokes SET name=? WHERE id=?", (name, smoke_id))
        conn.commit()
        return smoke_id


def get_user_smokes(user_id: int) -> Sequence[Tuple[int, str]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name FROM smokes WHERE owner_id=? AND is_for_sale=0",
            (user_id,),
        )
        return cur.fetchall()


def get_user_sale_smokes(user_id: int) -> Sequence[Tuple[int, str, int]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT s.id, s.name, m.price
            FROM smokes s
            JOIN market m ON s.id = m.smoke_id
            WHERE m.owner_id=? AND s.is_for_sale=1
            """,
            (user_id,),
        )
        return cur.fetchall()


def get_smoke(smoke_id: int) -> Optional[Tuple[int, int, str, str, int]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, owner_id, name, description, is_for_sale FROM smokes WHERE id=?",
            (smoke_id,),
        )
        return cur.fetchone()


def get_smoke_with_owner(
    smoke_id: int,
) -> Optional[Tuple[int, str, str, int, int, Optional[str], Optional[int]]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT s.id, s.name, s.description, s.owner_id, s.is_for_sale, u.username
            FROM smokes s
            LEFT JOIN users u ON s.owner_id = u.id
            WHERE s.id=?
            """,
            (smoke_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        price = None
        if row[4]:
            cur.execute("SELECT price FROM market WHERE smoke_id=?", (smoke_id,))
            price_row = cur.fetchone()
            price = price_row[0] if price_row else None
        return (*row, price)


def update_description(smoke_id: int, text: str) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE smokes SET description=? WHERE id=?", (text, smoke_id))
        conn.commit()


def transfer_smoke(smoke_id: int, new_owner_id: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE smokes SET owner_id=?, is_for_sale=0 WHERE id=?",
            (new_owner_id, smoke_id),
        )
        cur.execute("DELETE FROM market WHERE smoke_id=?", (smoke_id,))
        conn.commit()


def ensure_owner(smoke_id: int, user_id: int) -> bool:
    smoke = get_smoke(smoke_id)
    return bool(smoke and smoke[1] == user_id)
