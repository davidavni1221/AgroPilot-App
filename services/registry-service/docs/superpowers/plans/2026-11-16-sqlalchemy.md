# Plan: move registry data access to SQLAlchemy

Each step ends with `uv run pytest` green on SQLite and PostgreSQL (`TEST_DATABASE_URL` set).

1. `config.py` with pydantic-settings; `database.py` reads `DATABASE_URL` from it. (commit 3925b40)
2. `tables.py` and a SQLAlchemy engine in `database.py`; map SQLAlchemy errors.
3. Port every query in `main.py` to Core expressions; update tests that used the old wrapper. (commit 6538290)
4. `seed_postgres.py` builds the tables from `tables.py`; remove `schema_postgres.sql`.
5. README, handoff and design docs.
6. Measure p95 on PostgreSQL (10 rps, 30 s per route) and update the README table.
