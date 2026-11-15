# PostgreSQL support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the registry API on PostgreSQL (selected by `DATABASE_URL`) or on the local SQLite file, with identical behavior.

**Architecture:** `database.py` returns one small `Db` wrapper for both databases (converts `?` to `%s`, returns dict rows, exposes the driver error classes). `main.py` keeps its SQL and only changes type hints, one `COUNT`, list ordering and the error handlers. A PostgreSQL schema and seed script build the data. The test fixtures run the same endpoint tests on both databases.

**Tech Stack:** Python 3.12, FastAPI, `psycopg[binary]~=3.2`, `python-dotenv~=1.0`, pytest, Docker `postgres:16`.

**Spec:** `services/registry-service/docs/superpowers/specs/2026-11-15-postgres-support-design.md`

## Global Constraints

- Work in `services/registry-service`. Branch `postgres-migration` (already checked out).
- No API changes: same status codes, `application/problem+json`, `code` values `VALIDATION`/`NOT_FOUND`/`CONFLICT`/`UNAVAILABLE`, `Retry-After: 5` on 503, dates `YYYY-MM-DD`.
- `DATABASE_URL` unset or blank means SQLite `registry.db`. Schemes `postgresql://` and `postgres://` mean PostgreSQL. Any other scheme stops startup with a clear `ValueError`.
- One connection per request, no pool, no ORM, no migration tool.
- Decimal columns are `DOUBLE PRECISION`. `planting_date` stays `TEXT`. List queries end with `ORDER BY id`.
- Never commit `.env`, `CLAUDE.md` or `.claude/settings.json`. Stage files by explicit path.
- End every commit message with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- Run tests with `uv run pytest`. PostgreSQL tests run only when `TEST_DATABASE_URL` is set.

## Review Focus

1. `DATABASE_URL` points at a server that is down: expect 503 + `Retry-After: 5`, quickly (`connect_timeout=5`), not 500. (Task 4)
2. Wrong password or unknown database name: expect the same 503. (Task 4)
3. Decimal values round-trip exactly, for example `flow_lph` 0.6 and `lat` 31.25, not `0.6000000238`. (Task 4)
4. Hebrew text and emoji in a name round-trip unchanged. (Task 5)
5. A `name` containing the NUL character: SQLite accepts it, PostgreSQL refuses it. Expect 422 `VALIDATION`, never 500. (Task 2 maps `psycopg.DataError`, Task 4 tests it)
6. A blank `DATABASE_URL=` line in `.env` is treated as unset. (Task 1)

---

### Task 1: `Db` wrapper and database selection

**Files:**
- Modify: `database.py`, `pyproject.toml` (via `uv add`), `uv.lock`
- Test: `tests/test_database.py` (create)
- Also commit: `docs/superpowers/specs/2026-11-15-postgres-support-design.md`, this plan.

**Interfaces:**
- Produces in `database.py`:
  - `def database_url() -> str | None` (reads `os.environ["DATABASE_URL"]` at call time, `None` if unset or blank).
  - `def backend() -> Literal["sqlite", "postgres"]` (raises `ValueError` for any other scheme).
  - `class Db` with `execute(self, sql: str, params: Sequence = ()) -> Cursor`, `commit(self) -> None`, `close(self) -> None`.
  - `class Cursor` with `fetchone(self) -> dict | None`, `fetchall(self) -> list[dict]`.
  - `def get_db() -> Iterator[Db]` (FastAPI dependency).
  - `OPERATIONAL_ERRORS`, `INTEGRITY_ERRORS`, `DATA_ERRORS`: tuples of exception classes (`sqlite3` and `psycopg` ones; `DATA_ERRORS` holds only `psycopg.DataError`).
  - `def translate_placeholders(sql: str) -> str` (`%` becomes `%%`, then `?` becomes `%s`).
- Keeps: `DB_PATH` and the `mode=rw` SQLite open with `PRAGMA foreign_keys = ON`.

- [ ] **Step 1: Add dependencies** with `uv add "psycopg[binary]~=3.2" "python-dotenv~=1.0"`. Check `uv run python -c "import psycopg, dotenv"` prints nothing.
- [ ] **Step 2: Write failing tests** in `tests/test_database.py`: `test_translate_placeholders` (`"a = ? AND b LIKE '%x'"` gives `"a = %s AND b LIKE '%%x'"`), `test_backend_unset_is_sqlite`, `test_backend_blank_is_sqlite`, `test_backend_postgres_schemes` (both `postgresql://u:p@h/db` and `postgres://u:p@h/db`), `test_backend_unknown_scheme_raises_value_error` (`mysql://x`), `test_sqlite_wrapper_returns_dict_rows` (use the seeded `db_path` fixture, `fetchone()` of `SELECT id, name FROM crops WHERE id = ?` equals `{"id": "tomato", "name": "Tomato"}`). Tests set the environment with `monkeypatch.setenv` / `delenv`.
- [ ] **Step 3: Run** `uv run pytest tests/test_database.py -v`. Expected: FAIL (names missing).
- [ ] **Step 4: Implement** the interfaces above in `database.py`. SQLite path: same open call as today, wrapped. PostgreSQL path: `psycopg.connect(url, row_factory=dict_row, connect_timeout=5)`. Call `load_dotenv()` once at import (it must not override variables already set). `get_db` closes the connection in `finally`.
- [ ] **Step 5: Run** `uv run pytest tests/test_database.py -v`. Expected: PASS. Do not run the full suite yet: `main.py` still expects `sqlite3.Row` until Task 2.
- [ ] **Step 6: Commit** `git add database.py pyproject.toml uv.lock tests/test_database.py docs/superpowers` then `git commit -m "feat: add Db wrapper and DATABASE_URL selection"`.

### Task 2: Port `main.py`

**Files:**
- Modify: `main.py` (imports, type hints, handlers, `delete_farm`, list queries)
- Test: `tests/test_api.py` (append)

**Interfaces:**
- Consumes: `Db`, `get_db`, `OPERATIONAL_ERRORS`, `INTEGRITY_ERRORS`, `DATA_ERRORS`, `backend` from `database`.
- Produces: every route takes `db: Db = Depends(get_db)`.

- [ ] **Step 1: Write failing tests** appended to `tests/test_api.py`: `test_list_endpoints_are_sorted_by_id` (for `/v1/crops`, `/v1/soils`, `/v1/emitters`, `/v1/farms`, `/v1/plots`: the ids equal `sorted(ids)`). The `COUNT` change in `delete_farm` is covered by the existing delete tests.
- [ ] **Step 2: Run** `uv run pytest tests/test_api.py -k sorted -v`. Expected: FAIL for at least `/v1/plots` or `/v1/farms`, unless the seed order already matches. If it passes by luck, keep the test and continue.
- [ ] **Step 3: Implement.** Replace `sqlite3.Connection` hints with `Db`. Append `ORDER BY id` to the five list queries (the `farm_id` filter query too). In `delete_farm`, use `SELECT COUNT(*) AS n ...` and read `["n"]`. Register the 503 handler for each class in `OPERATIONAL_ERRORS` (same body and `Retry-After: 5`). In `create_plot` catch `INTEGRITY_ERRORS` (message unchanged). Add a handler for `DATA_ERRORS` returning 422 `VALIDATION`, title `Unprocessable Entity`, detail `Invalid value`. Call `backend()` once at import so a bad `DATABASE_URL` stops startup.
- [ ] **Step 4: Run** `uv run pytest -v`. Expected: all pass, still on SQLite.
- [ ] **Step 5: Commit** `git add main.py tests/test_api.py`, message `feat: port main.py to the Db wrapper`.

### Task 3: PostgreSQL schema and seed

**Files:**
- Create: `schema_postgres.sql`, `seed_postgres.py`
- Test: `tests/test_seed_postgres.py` (create)

**Interfaces:**
- Produces: `def seed(url: str) -> None` in `seed_postgres.py` (drops the five tables, applies `schema_postgres.sql`, inserts the same 15 rows as `seed_registry.sh`). Running `uv run python seed_postgres.py` seeds the database in `DATABASE_URL`.

- [ ] **Step 1: Create the test database** (one time): `docker exec registry-pg createdb -U postgres registry_test`. Export `TEST_DATABASE_URL=postgresql://postgres:<password>@127.0.0.1:5432/registry_test`. Tests must never use the `registry` database, because seeding drops tables.
- [ ] **Step 2: Write failing test** `test_seed_creates_expected_rows` (skip when `TEST_DATABASE_URL` is unset): after `seed(url)`, row counts are 2 farms, 4 plots, 2 crops, 3 soils, 4 emitters, and the plot `North block` has `area_m2` 1000.0 and `planting_date` `2026-03-01`. Add `test_seed_matches_sqlite_seed`: the ids and names of every table equal those from the SQLite seed built by `seed_registry.sh`.
- [ ] **Step 3: Run** `uv run pytest tests/test_seed_postgres.py -v`. Expected: FAIL (module missing).
- [ ] **Step 4: Implement** the schema (same columns, `PRIMARY KEY`, `REFERENCES`, `UNIQUE (farm_id, name)`; `INTEGER` for `available_water_mm_per_m`, `DOUBLE PRECISION` for decimals, `TEXT` otherwise) and `seed(url)` using `psycopg`. Rows are copied from `seed_registry.sh`.
- [ ] **Step 5: Run** the same command. Expected: PASS.
- [ ] **Step 6: Commit** `git add schema_postgres.sql seed_postgres.py tests/test_seed_postgres.py`, message `feat: add PostgreSQL schema and seed`.

### Task 4: Run the API tests on both databases

**Files:**
- Modify: `tests/conftest.py`, `tests/test_api.py` (two sqlite-only tests)
- Test: `tests/test_api.py` (append backend tests)

**Interfaces:**
- Produces: fixture `client` parametrized with `["sqlite", "postgres"]`. The `postgres` case skips when `TEST_DATABASE_URL` is unset, otherwise sets `DATABASE_URL` to it and calls `seed(url)`. The `sqlite` case builds the temporary database as today and always `delenv("DATABASE_URL", raising=False)`, so a developer's `.env` never leaks into the SQLite run. `db_path` also deletes `DATABASE_URL`. The FK test and the missing-file test keep using `db_path` and are SQLite-only.

- [ ] **Step 1: Write failing tests** appended to `tests/test_api.py`, using `client`: `test_float_values_round_trip` (`GET /v1/emitters/dripnet-pc-0.6` has `flow_lph == 0.6`; the North block plot has `lat == 31.25`), `test_nul_character_in_name_is_422_validation` (`POST /v1/farms` with `{"name": "a\u0000b"}`: on PostgreSQL expect 422 `VALIDATION`; on SQLite expect 201, so assert `status in (201, 422)` and never 500).
  Separate tests that do not use `client`: `test_postgres_server_down_returns_503` (set `DATABASE_URL=postgresql://postgres:x@127.0.0.1:1/registry`, call any GET, expect 503, `code` `UNAVAILABLE`, `Retry-After: 5`), `test_postgres_wrong_password_returns_503` (skip without `TEST_DATABASE_URL`; same URL with the password replaced), `test_blank_database_url_uses_sqlite` (set `DATABASE_URL=""`, `GET /v1/farms` returns 200 on the seeded SQLite file).
- [ ] **Step 2: Run** `uv run pytest -v`. Expected: FAIL on the new tests (fixture not yet parametrized).
- [ ] **Step 3: Implement** the fixture changes in `conftest.py`. Keep `TestClient(app)`.
- [ ] **Step 4: Run** `uv run pytest -v` with `TEST_DATABASE_URL` set. Expected: every old test runs twice (SQLite and PostgreSQL) and passes. Then run without `TEST_DATABASE_URL`. Expected: SQLite tests pass, PostgreSQL ones show as skipped.
- [ ] **Step 5: Commit** `git add tests/conftest.py tests/test_api.py`, message `test: run API tests on SQLite and PostgreSQL`.

### Task 5: Long text, many rows, docs, latency

**Files:**
- Test: `tests/test_api.py` (append)
- Modify: `README.md`, `AGENTS.md`, `.env.example` (create, no password)

- [ ] **Step 1: Write tests** using `client`: `test_long_text_values_round_trip` (a 1,000,000-character farm `name` through `POST /v1/farms` then `GET /v1/farms/{id}` is identical; a farm name `"חוות שלום 🌱"` round-trips unchanged), `test_thousands_of_rows` (insert 5,000 farms through `database.get_db()` with one commit; `GET /v1/farms` returns 5,002 items, sorted by id, status 200).
- [ ] **Step 2: Run** `uv run pytest -v` (with `TEST_DATABASE_URL`). Expected: PASS. If the 1 MB request is rejected anywhere, report it instead of adding a limit (the spec forbids new limits).
- [ ] **Step 3: Update docs.** README: how to set `DATABASE_URL`, seed PostgreSQL with `uv run python seed_postgres.py`, run the PostgreSQL tests with `TEST_DATABASE_URL`. `AGENTS.md`: one line saying both databases are supported. `.env.example`: `DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME` as a comment-only example.
- [ ] **Step 4: Measure p95** on PostgreSQL with the NFR-1.1 method (10 rps, 30 s per GET route, p95 at `ceil(0.95 * n)`), seeded `registry` database, service started with `uv run uvicorn main:app --host 127.0.0.1 --port 8000`. Use a throwaway script in the scratchpad, not in the repo. Add a second column to the README performance table. Expected: every route under 100 ms. Report the numbers, including any miss.
- [ ] **Step 5: Commit** `git add README.md AGENTS.md .env.example tests/test_api.py`, message `docs: document DATABASE_URL, PostgreSQL tests and latency`.
