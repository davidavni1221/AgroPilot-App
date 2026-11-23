# Changelog

## v1.1.0 - 2026-11-23

- Added `GET /v1/farms/{id}/summary` to registry-service. It returns `farm_id`, `plot_count` and `total_area_m2` for a farm, and `404 NOT_FOUND` for an unknown farm.

## v1.0.0 - 2026-11-22

- First version: registry-service (crops, soils, emitters, farms and plots on SQLite or PostgreSQL), planner-service, weather-service and the frontend.
