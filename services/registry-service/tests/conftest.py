import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

import database
from main import app
from seed_postgres import seed

SERVICE_DIR = Path(__file__).resolve().parent.parent
SEED_SCRIPT = SERVICE_DIR / "seed_registry.sh"


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """בונה מסד חדש מ-seed לכל בדיקה, כך שהבדיקות לא משנות את registry.db האמיתי."""
    path = tmp_path / "registry.db"
    subprocess.run(["bash", str(SEED_SCRIPT), str(path)], check=True, cwd=SERVICE_DIR, capture_output=True)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database, "DB_PATH", path)
    return path


@pytest.fixture(params=["sqlite", "postgres"])
def client(request, monkeypatch):
    if request.param == "sqlite":
        request.getfixturevalue("db_path")
    else:
        url = os.environ.get("TEST_DATABASE_URL")
        if not url:
            pytest.skip("TEST_DATABASE_URL is not set")
        if urlsplit(url).path != "/registry_test":
            pytest.fail("TEST_DATABASE_URL must point to the registry_test database (seeding drops tables)")
        monkeypatch.setenv("DATABASE_URL", url)
        seed(url)
    with TestClient(app) as test_client:
        yield test_client
