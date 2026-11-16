"""Build the registry tables in PostgreSQL. Destructive: drops the five tables first.

Usage, from services/registry-service:
    uv run python seed_postgres.py      # seeds DATABASE_URL
"""
from sqlalchemy import create_engine, insert

import database
from tables import crops, emitters, farms, metadata, plots, soils

CROPS = [("tomato", "Tomato"), ("bell-pepper", "Bell pepper")]
SOILS = [("sand", "Sand", 83), ("loam", "Loam", 175), ("clay-loam", "Clay loam", 200)]
EMITTERS = [
    ("dripnet-pc-0.6", "DripNet PC", 0.6),
    ("dripnet-pc-1.0", "DripNet PC", 1.0),
    ("dripnet-pc-1.6", "DripNet PC", 1.6),
    ("dripnet-pc-2.0", "DripNet PC", 2.0),
]
FARMS = [
    ("b7e2c0a0-3c1d-4f0a-9a11-0c5d2e6f1001", "Demo cooperative"),
    ("a9c1e4b2-6f70-4d8e-a144-3f8b5c904004", "East farm"),
]
PLOTS = [
    ("c8f3d1b0-4d2e-5a1b-8b22-1d6e3f702002", "b7e2c0a0-3c1d-4f0a-9a11-0c5d2e6f1001",
     "North block", 1000, "tomato", "2026-03-01", "loam", 1.5, 0.4, "dripnet-pc-1.0", 31.25, 34.79),
    ("d9a4e2c1-5e3f-4b6a-9c33-2e7f4a803003", "b7e2c0a0-3c1d-4f0a-9a11-0c5d2e6f1001",
     "East block", 800, "bell-pepper", "2026-04-12", "clay-loam", 1.5, 0.4, "dripnet-pc-1.6", 31.26, 34.80),
    ("e0b5f3d2-6f40-4c7b-8d44-3f8a5b914004", "a9c1e4b2-6f70-4d8e-a144-3f8b5c904004",
     "West block", 1500, "tomato", "2026-02-15", "sand", 1.5, 0.4, "dripnet-pc-0.6", 31.40, 34.60),
    ("f1c6a4e3-7051-4d8c-9e55-4a9b6c025005", "a9c1e4b2-6f70-4d8e-a144-3f8b5c904004",
     "Greenhouse", 400, "bell-pepper", "2026-05-01", "loam", 1.2, 0.3, "dripnet-pc-2.0", 31.41, 34.61),
]


PLOT_COLUMNS = ["id", "farm_id", "name", "area_m2", "crop_id", "planting_date", "soil_id",
                "row_spacing_m", "emitter_spacing_m", "emitter_id", "lat", "lon"]


def seed(url: str) -> None:
    engine = create_engine(database.driver_url(url))
    try:
        with engine.begin() as conn:
            metadata.drop_all(conn)
            metadata.create_all(conn)
            for table, columns, rows in [
                (crops, ["id", "name"], CROPS),
                (soils, ["id", "name", "available_water_mm_per_m"], SOILS),
                (emitters, ["id", "name", "flow_lph"], EMITTERS),
                (farms, ["id", "name"], FARMS),
                (plots, PLOT_COLUMNS, PLOTS),
            ]:
                conn.execute(insert(table), [dict(zip(columns, row)) for row in rows])
    finally:
        engine.dispose()


if __name__ == "__main__":
    url = database.database_url()
    if url is None:
        raise SystemExit("DATABASE_URL is not set.")
    seed(url)
    print("Seeded: 2 farms, 4 plots, 2 crops, 3 soils, 4 emitters")
