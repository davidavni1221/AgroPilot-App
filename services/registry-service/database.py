from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Literal

from sqlalchemy import Connection, create_engine, event, exc
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from config import get_settings

DB_PATH = Path(__file__).parent / "registry.db"

OPERATIONAL_ERRORS = (exc.OperationalError,)
INTEGRITY_ERRORS = (exc.IntegrityError,)
DATA_ERRORS = (exc.DataError,)


def database_url() -> str | None:
    return get_settings().database_url


def backend() -> Literal["sqlite", "postgres"]:
    return "sqlite" if database_url() is None else "postgres"


@lru_cache
def _engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        # NullPool: a new connection per request, like a plain sqlite3 file.
        engine = create_engine(url, poolclass=NullPool)

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _):
            # SQLite does not enforce foreign keys by default.
            dbapi_connection.execute("PRAGMA foreign_keys = ON")

        return engine
    return create_engine(url, connect_args={"connect_timeout": 5}, pool_pre_ping=True)


def engine() -> Engine:
    url = database_url()
    if url is None:
        # mode=rw: a missing file is an error, not a silently created empty database.
        return _engine(f"sqlite:///file:{DB_PATH}?mode=rw&uri=true")
    # "postgres://" is not understood by SQLAlchemy, and plain "postgresql://" would pick the psycopg2 driver.
    return _engine("postgresql+psycopg://" + url.split("://", 1)[1])


def get_db() -> Iterator[Connection]:
    with engine().connect() as connection:
        yield connection
