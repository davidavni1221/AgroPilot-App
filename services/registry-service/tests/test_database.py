import pytest
from sqlalchemy import select

import database
from tables import crops


def test_backend_unset_is_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert database.database_url() is None
    assert database.backend() == "sqlite"


def test_backend_blank_is_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "   ")
    assert database.database_url() is None
    assert database.backend() == "sqlite"


@pytest.mark.parametrize("url", ["postgresql://u:p@h/db", "postgres://u:p@h/db"])
def test_backend_postgres_schemes(monkeypatch, url):
    monkeypatch.setenv("DATABASE_URL", url)
    assert database.backend() == "postgres"


def test_backend_unknown_scheme_raises_value_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://x")
    with pytest.raises(ValueError):
        database.backend()


def test_sqlite_connection_returns_dict_rows(db_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    gen = database.get_db()
    db = next(gen)
    try:
        row = db.execute(select(crops).where(crops.c.id == "tomato")).mappings().first()
        assert dict(row) == {
            "id": "tomato", "name": "Tomato", "kc_ini": 0.6, "kc_mid": 1.15, "kc_end": 0.8,
            "l_ini": 30, "l_dev": 40, "l_mid": 45, "l_late": 30, "root_depth_m": 0.7,
        }
    finally:
        gen.close()
