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


def test_ids_sort_bytewise(url):
    with psycopg.connect(url) as conn:
        ids = [r[0] for r in conn.execute("SELECT id FROM emitters ORDER BY id").fetchall()]
    assert ids == sorted(ids)
