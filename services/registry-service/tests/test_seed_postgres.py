import os
import sqlite3
import subprocess
from pathlib import Path

import psycopg
import pytest

from seed_postgres import seed

SERVICE_DIR = Path(__file__).resolve().parent.parent
TABLES = ["farms", "plots", "crops", "soils", "emitters"]

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL is not set"
)


@pytest.fixture
def url():
    url = os.environ["TEST_DATABASE_URL"]
    seed(url)
    return url


def test_seed_creates_expected_rows(url):
    with psycopg.connect(url) as conn:
        counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in TABLES}
        plot = conn.execute(
            "SELECT area_m2, planting_date FROM plots WHERE name = 'North block'"
        ).fetchone()
    assert counts == {"farms": 2, "plots": 4, "crops": 2, "soils": 3, "emitters": 4}
    assert plot == (1000.0, "2026-03-01")


def test_seed_matches_sqlite_seed(url, tmp_path):
    path = tmp_path / "registry.db"
    subprocess.run(["bash", "seed_registry.sh", str(path)], check=True, cwd=SERVICE_DIR, capture_output=True)
    lite = sqlite3.connect(path)
    with psycopg.connect(url) as conn:
        for table in TABLES:
            sql = f"SELECT id, name FROM {table} ORDER BY id"
            assert conn.execute(sql).fetchall() == lite.execute(sql).fetchall(), table


def test_id_columns_use_c_collation(url):
    with psycopg.connect(url) as conn:
        rows = conn.execute(
            "SELECT table_name, column_name, collation_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND (column_name = 'id' OR column_name LIKE '%\\_id')"
        ).fetchall()
    assert len(rows) == 9  # 5 id columns + 4 *_id columns in plots
    assert [r for r in rows if r[2] != "C"] == []


def test_ids_sort_bytewise(url):
    ids = ["a-b", "a_b", "B", "a", "A1", "a1"]
    with psycopg.connect(url) as conn:
        for i in ids:
            conn.execute("INSERT INTO crops (id, name) VALUES (%s, 'x')", (i,))
        got = [r[0] for r in conn.execute("SELECT id FROM crops WHERE name = 'x' ORDER BY id").fetchall()]
        conn.rollback()
    assert got == sorted(ids)
