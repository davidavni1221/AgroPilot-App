"""seed_postgres.py without a PostgreSQL server: the create_engine call is pointed at a SQLite file.

The tables are defined once for both databases, so the drop, create and insert steps run for real.
The PostgreSQL-only parts are covered by test_seed_postgres.py when TEST_DATABASE_URL is set.
"""
import runpy
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import create_engine

import database
import seed_postgres

SERVICE_DIR = Path(__file__).resolve().parent.parent
EXPECTED = {"farms": 2, "plots": 4, "crops": 2, "soils": 3, "emitters": 4}


def counts(path):
    with sqlite3.connect(path) as conn:
        return {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in EXPECTED}


@pytest.fixture
def sqlite_engine(tmp_path, monkeypatch):
    """Makes create_engine (as seed_postgres calls it) return an engine on a SQLite file."""
    path = tmp_path / "seed.db"
    real_create_engine = create_engine
    monkeypatch.setattr(seed_postgres, "create_engine", lambda url: real_create_engine(f"sqlite:///{path}"))
    monkeypatch.setattr("sqlalchemy.create_engine", lambda url: real_create_engine(f"sqlite:///{path}"))
    return path


def test_seed_creates_expected_rows(sqlite_engine):
    seed_postgres.seed("postgresql://user:pw@localhost/registry")
    assert counts(sqlite_engine) == EXPECTED


def test_seed_twice_resets_to_the_same_rows(sqlite_engine):
    """It drops the tables first, so a second run does not duplicate or fail."""
    seed_postgres.seed("postgresql://user:pw@localhost/registry")
    seed_postgres.seed("postgresql://user:pw@localhost/registry")
    assert counts(sqlite_engine) == EXPECTED


def test_script_seeds_database_url(sqlite_engine, monkeypatch, capsys):
    monkeypatch.setattr(database, "database_url", lambda: "postgresql://user:pw@localhost/registry")
    runpy.run_path(str(SERVICE_DIR / "seed_postgres.py"), run_name="__main__")
    assert counts(sqlite_engine) == EXPECTED
    assert "Seeded" in capsys.readouterr().out


def test_script_without_database_url_exits_with_message(monkeypatch):
    monkeypatch.setattr(database, "database_url", lambda: None)
    with pytest.raises(SystemExit) as stopped:
        runpy.run_path(str(SERVICE_DIR / "seed_postgres.py"), run_name="__main__")
    assert stopped.value.code == "DATABASE_URL is not set."
