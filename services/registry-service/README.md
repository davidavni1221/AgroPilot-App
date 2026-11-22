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
               text name
               double kc_ini
               double kc_mid
               double kc_end
               int    l_ini
               int    l_dev
               int    l_mid
               int    l_late
               double root_depth_m }
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
| POST | `/v1/crops` | 201 |
| GET | `/v1/crops`, `/v1/crops/{id}` | 200 |
| GET | `/v1/soils`, `/v1/soils/{id}` | 200 |
| GET | `/v1/emitters`, `/v1/emitters/{id}` | 200 |

Soils and emitters are read-only lists. Crops can also be added with `POST /v1/crops`, because a farmer knows the crop numbers the planner needs. Any other method on a catalogue route returns 405.

A crop is sent with its name and the FAO-56 numbers the planner uses: `kc_ini`, `kc_mid`, `kc_end` (0 to 2), `l_ini`, `l_dev`, `l_mid`, `l_late` (stage lengths in whole days, 1 to 365) and `root_depth_m` (0 to 3). The id is made from the name, so "Sweet corn" becomes `sweet-corn`. A name that gives an id that already exists returns 409 `CONFLICT`. A name with no letter or digit (a-z, 0-9) returns 422 `VALIDATION`. ET0 and rain are not sent. The weather service gets them from the plot's location.

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

### With a lot of text

The same method on PostgreSQL, but against a separate, throwaway database filled with long text: 1,002 farms with 2,000-character names, 2,004 plots with 1,000-character names, and 202 crops, 203 soils and 204 emitters with 1,000-character names. This is much heavier than the seed data, which has only a few short names. 0 errors in every row.

| Endpoint | PostgreSQL p95 | Response size |
|---|---|---|
| GET /v1/farms | 45.5 ms | 3.5 MB |
| GET /v1/farms/{id} | 5.2 ms | 3.6 KB |
| GET /v1/plots | 65.7 ms | 4.0 MB |
| GET /v1/plots/{id} | 6.0 ms | 2.0 KB |
| GET /v1/crops | 10.9 ms | 381 KB |
| GET /v1/crops/{id} | 5.7 ms | 1.9 KB |
| GET /v1/soils | 9.2 ms | 367 KB |
| GET /v1/soils/{id} | 5.1 ms | 1.8 KB |
| GET /v1/emitters | 8.2 ms | 364 KB |
| GET /v1/emitters/{id} | 6.6 ms | 1.8 KB |

Every route is still under 100 ms. The big lists grow with the response size: the plots list, at 4 MB, is the slowest at 65.7 ms. The service, the client and the database all ran on the same machine, so this does not include a network between them.

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
