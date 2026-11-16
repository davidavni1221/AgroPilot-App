import sqlite3
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Literal

import psycopg
from psycopg.rows import dict_row

from config import get_settings

DB_PATH = Path(__file__).parent / "registry.db"

OPERATIONAL_ERRORS = (sqlite3.OperationalError, psycopg.OperationalError)
INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg.IntegrityError)
DATA_ERRORS = (psycopg.DataError,)


def database_url() -> str | None:
    return get_settings().database_url


def backend() -> Literal["sqlite", "postgres"]:
    return "sqlite" if database_url() is None else "postgres"


def translate_placeholders(sql: str) -> str:
    return sql.replace("%", "%%").replace("?", "%s")


class Cursor:
    def __init__(self, cur):
        self._cur = cur

    def fetchone(self) -> dict | None:
        row = self._cur.fetchone()
        return None if row is None else dict(row)

    def fetchall(self) -> list[dict]:
        return [dict(r) for r in self._cur.fetchall()]


class Db:
    def __init__(self, conn, is_postgres: bool):
        self._conn = conn
        self._is_postgres = is_postgres

    def execute(self, sql: str, params: Sequence = ()) -> Cursor:
        if self._is_postgres:
            return Cursor(self._conn.execute(translate_placeholders(sql), params))
        return Cursor(self._conn.execute(sql, params))

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _connect() -> Db:
    if backend() == "postgres":
        conn = psycopg.connect(database_url(), row_factory=dict_row, connect_timeout=5)
        return Db(conn, True)
    # mode=rw: אם הקובץ חסר, להיכשל במקום ליצור מסד ריק בשקט
    conn = sqlite3.connect(DB_PATH.as_uri() + "?mode=rw", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # SQLite לא אוכף מפתחות זרים כברירת מחדל; בלי זה אפשר ליצור חלקה לחווה שלא קיימת
    conn.execute("PRAGMA foreign_keys = ON")
    return Db(conn, False)


def get_db() -> Iterator[Db]:
    db = _connect()
    try:
        yield db
    finally:
        db.close()
