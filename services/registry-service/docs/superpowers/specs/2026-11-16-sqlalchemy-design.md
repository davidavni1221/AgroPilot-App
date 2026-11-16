# Registry data access through SQLAlchemy: design

Date: 2026-11-16. Amends `2026-11-15-postgres-support-design.md`, which chose a thin `psycopg` adapter (approach 1) and rejected SQLAlchemy (approach 2).

## Why the change

P2 says "All data access goes through SQLAlchemy". The user decided to follow it. The earlier risk (changed responses) is covered by the existing 152 behavior tests, which run on both databases.

## Decisions

- **SQLAlchemy Core, not the ORM.** Tables and queries in Python, no mapped classes. Smallest change from the raw SQL.
- **Tables defined once** in `tables.py`. `create_all` builds an empty PostgreSQL database (FR-2.2). `schema_postgres.sql` is removed. SQLite is still built by `seed_registry.sh`.
- **Identical behavior kept:** ids use collation `"C"` on PostgreSQL (same sort as SQLite); decimals are `DOUBLE PRECISION`; `planting_date` stays text `YYYY-MM-DD`; the unique index on `(farm_id, md5(name))` stays (PostgreSQL only).
- **Settings** in `config.py` (pydantic-settings). `DATABASE_URL` unset means SQLite. An unknown scheme fails at startup.
- **Engine.** Cached per URL. SQLite: `mode=rw` (missing file is an error), foreign keys on, no pool. PostgreSQL: driver `psycopg`, 5 s connect timeout, pooled connections with pre-ping.
- **Errors.** SQLAlchemy `OperationalError` gives 503 + `Retry-After: 5`, `IntegrityError` gives the same 422 in `create_plot`, `DataError` gives 422.
- **Tests.** Unchanged behavior tests on both databases. Tests that used the old wrapper now use SQLAlchemy.

## Not changed

No API changes, no new endpoints, no Alembic (a seed step is enough for this task).
