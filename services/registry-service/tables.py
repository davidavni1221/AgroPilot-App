"""The registry tables, defined once for both SQLite and PostgreSQL."""
from sqlalchemy import Column, Double, ForeignKey, Index, Integer, MetaData, Table, Text, func

metadata = MetaData()

# Ids sort by byte value ("C" collation) on PostgreSQL, the same order SQLite uses.
IdType = Text().with_variant(Text(collation="C"), "postgresql")

farms = Table(
    "farms", metadata,
    Column("id", IdType, primary_key=True),
    Column("name", Text, nullable=False),
)

# Kc for the three stages, stage lengths in days and root depth: what the planner needs (FAO-56).
crops = Table(
    "crops", metadata,
    Column("id", IdType, primary_key=True),
    Column("name", Text, nullable=False),
    Column("kc_ini", Double, nullable=False),
    Column("kc_mid", Double, nullable=False),
    Column("kc_end", Double, nullable=False),
    Column("l_ini", Integer, nullable=False),
    Column("l_dev", Integer, nullable=False),
    Column("l_mid", Integer, nullable=False),
    Column("l_late", Integer, nullable=False),
    Column("root_depth_m", Double, nullable=False),
)

soils = Table(
    "soils", metadata,
    Column("id", IdType, primary_key=True),
    Column("name", Text, nullable=False),
    Column("available_water_mm_per_m", Integer, nullable=False),
)

emitters = Table(
    "emitters", metadata,
    Column("id", IdType, primary_key=True),
    Column("name", Text, nullable=False),
    Column("flow_lph", Double, nullable=False),
)

plots = Table(
    "plots", metadata,
    Column("id", IdType, primary_key=True),
    Column("farm_id", IdType, ForeignKey("farms.id"), nullable=False),
    Column("name", Text, nullable=False),
    Column("area_m2", Double, nullable=False),
    Column("crop_id", IdType, ForeignKey("crops.id"), nullable=False),
    Column("planting_date", Text, nullable=False),  # YYYY-MM-DD
    Column("soil_id", IdType, ForeignKey("soils.id"), nullable=False),
    Column("row_spacing_m", Double, nullable=False),
    Column("emitter_spacing_m", Double, nullable=False),
    Column("emitter_id", IdType, ForeignKey("emitters.id"), nullable=False),
    Column("lat", Double, nullable=False),
    Column("lon", Double, nullable=False),
)

# md5(name): a btree entry is capped at ~2.7 KB, so indexing the raw name would limit its length.
# PostgreSQL only. SQLite gets UNIQUE (farm_id, name) from seed_registry.sh.
Index("plots_farm_name_key", plots.c.farm_id, func.md5(plots.c.name), unique=True).ddl_if(dialect="postgresql")
