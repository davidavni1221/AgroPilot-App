CREATE TABLE farms (
  id   TEXT COLLATE "C" PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE crops (
  id   TEXT COLLATE "C" PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE soils (
  id                         TEXT COLLATE "C" PRIMARY KEY,
  name                       TEXT NOT NULL,
  available_water_mm_per_m   INTEGER NOT NULL
);

CREATE TABLE emitters (
  id       TEXT COLLATE "C" PRIMARY KEY,
  name     TEXT NOT NULL,
  flow_lph DOUBLE PRECISION NOT NULL
);

CREATE TABLE plots (
  id                 TEXT COLLATE "C" PRIMARY KEY,
  farm_id            TEXT COLLATE "C" NOT NULL REFERENCES farms(id),
  name               TEXT NOT NULL,
  area_m2            DOUBLE PRECISION NOT NULL,
  crop_id            TEXT COLLATE "C" NOT NULL REFERENCES crops(id),
  planting_date      TEXT NOT NULL,
  soil_id            TEXT COLLATE "C" NOT NULL REFERENCES soils(id),
  row_spacing_m      DOUBLE PRECISION NOT NULL,
  emitter_spacing_m  DOUBLE PRECISION NOT NULL,
  emitter_id         TEXT COLLATE "C" NOT NULL REFERENCES emitters(id),
  lat                DOUBLE PRECISION NOT NULL,
  lon                DOUBLE PRECISION NOT NULL
);

-- md5(name): a btree entry is capped at ~2.7 KB, so indexing the raw name would limit its length.
CREATE UNIQUE INDEX plots_farm_name_key ON plots (farm_id, md5(name));
