from __future__ import annotations

import time
from typing import List, Optional, Sequence, Tuple

from ..database import get_connection


def add_user(user_id: int, username: Optional[str]) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
            (user_id, username or "unknown"),
        )
        conn.commit()


def update_username(user_id: int, username: Optional[str]) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))
        conn.commit()


def get_balance(user_id: int) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else 0


def update_balance(user_id: int, amount: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
        conn.commit()


def set_balance(user_id: int, new_balance: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET balance=? WHERE id=?", (new_balance, user_id))
        conn.commit()


def get_all_user_ids() -> List[int]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users")
        return [row[0] for row in cur.fetchall()]


def log_broadcast(text: str, sent: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO broadcast_logs (text, sent, timestamp) VALUES (?, ?, ?)",
            (text, sent, int(time.time())),
        )
        conn.commit()


def get_broadcast_logs(limit: int = 5) -> Sequence[Tuple[str, int, int]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT text, sent, timestamp FROM broadcast_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()


def set_balance_by_username(username: str, new_balance: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            return False
        cur.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
        conn.commit()
        return True


def get_user_id_by_username(username: str) -> Optional[int]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def get_top_users(limit: int = 3) -> Sequence[Tuple[int, Optional[str], int]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, balance FROM users ORDER BY balance DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()


def get_user_rank(user_id: int) -> Tuple[Optional[int], int]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        if not row:
            return None, 0
        balance = row[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE balance > ?", (balance,))
        higher = cur.fetchone()[0]
        return higher + 1, balance


def get_last_free_box(user_id: int) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT last_free_box FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else 0


def set_last_free_box(user_id: int, timestamp_value: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET last_free_box=? WHERE id=?", (timestamp_value, user_id))
        conn.commit()
