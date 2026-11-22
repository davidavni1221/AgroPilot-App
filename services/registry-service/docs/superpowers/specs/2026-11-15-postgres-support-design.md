# PostgreSQL support for the registry service: design

Date: 2026-11-15. Status: draft, waiting for approval.

## Intent

Production runs on an existing PostgreSQL server. Local work and tests keep using the SQLite file `registry.db`. The app picks the database from `DATABASE_URL` in the `.env` file. The API must behave exactly as it does today.

## Goals

- Same status codes, same `application/problem+json` errors and `code` values, `Retry-After: 5` on 503.
- `DATABASE_URL=postgresql://...` selects PostgreSQL. Unset selects the local SQLite file.
- The 64 existing tests keep passing on SQLite, and the same behavior tests pass on PostgreSQL.
- Extra tests: very long text values and thousands of rows.
- p95 latency re-measured on PostgreSQL (NFR-1.1 target: 100 ms).
- README explains `DATABASE_URL`.

## Non-goals

- No API changes, no new endpoints, no new fields, no new limits (for example no `name` length limit).
- No connection pool, no migrations tool, no ORM.
- No data migration from SQLite to production (see "Decided together", question 1).

## Anti-goals

- A migration that passes tests but changes a response, for example a number that returns as `0.6000000238` instead of `0.6`.

## Constraints

- AGENTS.md: minimum code, surgical changes, errors only through `APIError` or the shared handlers.
- Rules file: every endpoint keeps tests, including invalid input.
- `.env` is git-ignored and holds the password. Never commit it.

## Approaches

1. **Thin adapter with `psycopg` (chosen).** `database.py` returns one wrapper for both databases. It turns `?` into `%s` for PostgreSQL and returns rows as dicts. Errors are mapped in one place. `main.py` changes very little. Trade-off: the SQL must stay simple enough to run on both.
2. SQLAlchemy Core. One library, but every endpoint is rewritten and a heavy dependency is added. Biggest risk to identical behavior.
3. Two separate implementations. Duplicated SQL that can drift apart.

## Decided together

1. The tables and seed rows are created by us (option B): a PostgreSQL schema file plus a seed step. The same step builds the local test database.
2. Build with approach 1.

## Design (my calls, marked)

- **Selection.** `database.py` reads `DATABASE_URL` (loaded from `.env` with `python-dotenv`). Scheme `postgresql://` uses PostgreSQL. Unset uses the SQLite file `registry.db`. (My call.)
- **Fallback.** Unset means SQLite, so a fresh clone still runs. An unknown scheme fails at startup with a clear message. (My call.)
- **Connections.** One connection per request, as today. No pool. (My call.)
- **Adapter.** A small class wraps the connection. `execute(sql, params)` accepts `?` and converts it to `%s` on PostgreSQL. `fetchone()` and `fetchall()` return dict-like rows, so `dict(row)` and `row["farm_id"]` in `main.py` keep working. (My call.)
- **Commit and close.** Same as today: `commit()` after writes, close in `finally`.
- **Errors.**
  - SQLite `OperationalError` stays 503 + `Retry-After: 5`.
  - PostgreSQL connection errors (`psycopg.OperationalError`, which includes a server that is down) become the same 503.
  - `IntegrityError` from either driver becomes the same 422 in `create_plot`.
  - The missing-SQLite-file behavior (`mode=rw`, 503) stays.
- **Schema.** `schema_postgres.sql` mirrors the SQLite tables: same columns and constraints, `UNIQUE (farm_id, name)`, foreign keys. Types: `TEXT`, `INTEGER`, `DOUBLE PRECISION` for decimal numbers (not `REAL`, which is 32-bit and would change values like `0.6`). `planting_date` stays `TEXT` in `YYYY-MM-DD` so responses are identical. (My call.)
- **Seed.** `seed_postgres.py` applies the schema and the same 15 rows to the database in `DATABASE_URL`. It drops and recreates the tables, so running it again resets the data, like `seed_registry.sh`. It is not run automatically in production. (My call.)
- **List order.** List queries get `ORDER BY id`, so both databases return a stable order. PostgreSQL does not promise insertion order, and the SQLite order is already unspecified when an index is used. (My call.)
- **Tests.** The existing fixtures keep building SQLite. A second set of fixtures runs the same endpoint tests against PostgreSQL when `TEST_DATABASE_URL` is set, and skips them when it is not. Each PostgreSQL test resets the data through `seed_postgres.py`. New tests: a 1 MB `name` value, and 5000 rows through the list endpoints. (My call.)
- **Measurement.** Same method as NFR-1.1: 10 rps, 30 s per route, p95 at `ceil(0.95 * n)`, on PostgreSQL in Docker. Result added to the README table.
- **Docs.** README: how to set `DATABASE_URL`, how to run the PostgreSQL seed and tests. AGENTS.md: mention both databases.

## Left to the builder

- Exact wrapper class shape and names.
- Pytest marker or skip mechanism for the PostgreSQL tests.
- Wording of error messages for a bad `DATABASE_URL`.

## Open check (builder review)

I read this as a builder would. Nothing blocks planning. The calls marked above are mine, so please check them.
