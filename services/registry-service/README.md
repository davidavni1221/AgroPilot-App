# registry-service

FastAPI service that stores farms, plots, and the read-only catalogues (crops, soils, emitters) for AgroPilot.

Data is kept in one SQLite file, `registry.db`, which is created by a seed script and is not tracked by git. The service can also use PostgreSQL (see Database).

## Setup

Requirements: `uv`, and the `sqlite3` command-line tool (`sudo apt install sqlite3`).

```bash
uv sync
bash seed_registry.sh          # creates registry.db with 15 seed rows
```

Run the service:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Check it: http://127.0.0.1:8000/health returns `{"status": "ok"}`. Interactive docs are at http://127.0.0.1:8000/docs.

Run the tests:

```bash
uv run pytest
```

The tests build a fresh database from the seed script for each test, so they never change `registry.db`.

## Database

The service picks its database from `DATABASE_URL`:

- Not set (or empty): SQLite, using `registry.db`.
- `postgresql://USER:PASSWORD@HOST:5432/DBNAME`: PostgreSQL.

Put the value in a `.env` file in this folder. `.env` is git-ignored. `.env.example` shows the format.

To seed PostgreSQL:

```bash
uv run python seed_postgres.py
```

This drops and recreates the tables in the database named by `DATABASE_URL`, so everything in them is lost.

To run the tests on PostgreSQL as well, create a separate database and point `TEST_DATABASE_URL` at it. Its name must be `registry_test`. Never use the real database, because every test reseeds it.

```bash
createdb registry_test
```

If PostgreSQL runs in Docker, create it with `docker exec registry-pg createdb -U postgres registry_test` instead. Then run:

```bash
TEST_DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/registry_test uv run pytest
```

Without `TEST_DATABASE_URL`, the PostgreSQL tests are skipped and only the SQLite tests run.

Known difference: PostgreSQL cannot store or compare the NUL character (`\x00`). Inside an id, path or query value it gives 422 `VALIDATION` on PostgreSQL, where SQLite gives 404, an empty list, or a field-specific 422. It is junk input, and the response is still `application/problem+json`.

## Data model

`plots` is the central table. Each plot has exactly one farm, crop, soil and emitter. One farm, crop, soil or emitter can be used by many plots. A plot name is unique within its farm.

```mermaid
erDiagram
    farms    ||--o{ plots : "has"
    crops    ||--o{ plots : "is grown in"
    soils    ||--o{ plots : "describes"
    emitters ||--o{ plots : "waters"

    farms    { text id PK
               text name }
    crops    { text id PK
               text name }
    soils    { text id PK
               text name
               int  available_water_mm_per_m }
    emitters { text id PK
               text name
               double flow_lph }
    plots    { text id PK
               text farm_id FK
               text crop_id FK
               text soil_id FK
               text emitter_id FK
               text name
               double area_m2
               text planting_date
               double row_spacing_m
               double emitter_spacing_m
               double lat
               double lon }
```

The tables are defined in `tables.py`. Dates are `YYYY-MM-DD`.

## Endpoints

| Method | Path | Success |
|---|---|---|
| POST | `/v1/farms` | 201 |
| GET | `/v1/farms` | 200 |
| GET | `/v1/farms/{id}` | 200 |
| PATCH | `/v1/farms/{id}` | 200 |
| DELETE | `/v1/farms/{id}` | 204 |
| POST | `/v1/plots` | 201 |
| GET | `/v1/plots` (optional `?farm_id=`) | 200 |
| GET | `/v1/plots/{id}` | 200 |
| PATCH | `/v1/plots/{id}` | 200 |
| DELETE | `/v1/plots/{id}` | 204 |
| GET | `/v1/crops`, `/v1/crops/{id}` | 200 |
| GET | `/v1/soils`, `/v1/soils/{id}` | 200 |
| GET | `/v1/emitters`, `/v1/emitters/{id}` | 200 |

Catalogue routes are read-only. Any other method on them returns 405.

## Errors

Every error is `application/problem+json` (RFC 9457) with a `code` field, one of:

- `VALIDATION`: bad field, unknown crop/soil/emitter/farm, wrong method (422 or 405).
- `NOT_FOUND`: unknown id or route (404).
- `CONFLICT`: duplicate plot name in one farm, or deleting a farm that still has plots (409).
- `UNAVAILABLE`: database file missing or unusable (503, with `Retry-After: 5`).

Example:

```json
{
  "type": "about:blank",
  "title": "Unprocessable Entity",
  "status": 422,
  "detail": "Unknown emitter",
  "code": "VALIDATION"
}
```

## Performance

Measured at 10 requests per second for 30 seconds per endpoint (about 300 requests each), against a copy of the seed database, from a single local client, with 0 errors:

| Endpoint | SQLite p95 | PostgreSQL p95 |
|---|---|---|
| GET /v1/farms | 11.1 ms | 28.0 ms |
| GET /v1/farms/{id} | 12.2 ms | 25.0 ms |
| GET /v1/plots | 12.8 ms | 25.9 ms |
| GET /v1/plots/{id} | 11.9 ms | 28.0 ms |
| GET /v1/crops | 10.9 ms | 24.7 ms |
| GET /v1/crops/{id} | 11.4 ms | 26.0 ms |
| GET /v1/soils | 12.1 ms | 25.2 ms |
| GET /v1/soils/{id} | 11.7 ms | 26.0 ms |
| GET /v1/emitters | 12.2 ms | 25.0 ms |
| GET /v1/emitters/{id} | 11.9 ms | 25.9 ms |

The PostgreSQL numbers were measured the same way, through SQLAlchemy, against a local PostgreSQL server (apt package, WSL) on the same machine, with 0 errors. The SQLite column is from the earlier measurement, before the move to SQLAlchemy, and has not been re-measured.

The target is p95 at or below 100 ms.

## Layout

- `main.py`: routes, validation rules, and error handling.
- `models.py`: request and response shapes.
- `config.py`: settings (`DATABASE_URL`), read with pydantic-settings and checked at startup.
- `tables.py`: the table definitions, shared by SQLite and PostgreSQL (SQLAlchemy Core).
- `database.py`: the SQLAlchemy engine for `DATABASE_URL`, one connection per request, and the database error classes.
- `seed_postgres.py`: creates the tables from `tables.py` in an empty PostgreSQL database and loads the same seed rows (drops them first).
- `seed_registry.sh`: builds `registry.db` with the catalogues, two farms, and four plots.
- `tests/`: automated tests.
- `docs/judgment-log.md`: decisions taken during the build, and why.
