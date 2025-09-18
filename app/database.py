from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import settings


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    path = Path(settings.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                last_free_box INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS smokes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER,
                name TEXT,
                description TEXT DEFAULT 'Обычная сигара',
                is_for_sale INTEGER DEFAULT 0,
                rarity TEXT DEFAULT '🟢 Обычная'
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS market (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smoke_id INTEGER UNIQUE,
                price INTEGER,
                owner_id INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS broadcast_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                sent INTEGER,
                timestamp INTEGER
            )
            """
        )
        conn.commit()
        _apply_migrations(conn)


def _apply_migrations(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(smokes)")
    columns = {row[1] for row in cur.fetchall()}
    if "is_for_sale" not in columns:
        cur.execute("ALTER TABLE smokes ADD COLUMN is_for_sale INTEGER DEFAULT 0")
    if "rarity" not in columns:
        cur.execute("ALTER TABLE smokes ADD COLUMN rarity TEXT DEFAULT '🟢 Обычная'")

    cur.execute("PRAGMA table_info(users)")
    user_columns = {row[1] for row in cur.fetchall()}
    if "last_free_box" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN last_free_box INTEGER DEFAULT 0")

    conn.commit()
