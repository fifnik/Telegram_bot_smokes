from __future__ import annotations

from typing import Optional, Sequence, Tuple

from ..database import get_connection


def add_to_market(smoke_id: int, price: int, owner_id: int) -> Tuple[bool, str]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT owner_id, is_for_sale FROM smokes WHERE id=?", (smoke_id,))
        row = cur.fetchone()
        if not row:
            return False, "Сигара не найдена."
        current_owner, is_for_sale = row
        if current_owner != owner_id:
            return False, "Сигара не принадлежит вам."
        if is_for_sale:
            return False, "Сигара уже выставлена."

        cur.execute("SELECT id FROM market WHERE smoke_id=?", (smoke_id,))
        if cur.fetchone():
            return False, "Сигара уже в маркете."

        try:
            cur.execute(
                "INSERT INTO market (smoke_id, price, owner_id) VALUES (?, ?, ?)",
                (smoke_id, price, owner_id),
            )
            cur.execute("UPDATE smokes SET is_for_sale=1 WHERE id=?", (smoke_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            return False, "Не удалось выставить сигару."
        return True, ""


def remove_from_market(smoke_id: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM market WHERE smoke_id=?", (smoke_id,))
        cur.execute("UPDATE smokes SET is_for_sale=0 WHERE id=?", (smoke_id,))
        conn.commit()


def get_market() -> Sequence[Tuple[int, int, str, str]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.smoke_id, m.price, u.username, s.name
            FROM market m
            JOIN smokes s ON m.smoke_id = s.id
            JOIN users u ON m.owner_id = u.id
            """
        )
        return cur.fetchall()


def get_market_item(smoke_id: int) -> Optional[Tuple[int, int, int, str, str]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.smoke_id, m.price, m.owner_id, s.name, s.description
            FROM market m
            JOIN smokes s ON m.smoke_id = s.id
            WHERE m.smoke_id=?
            """,
            (smoke_id,),
        )
        return cur.fetchone()
