# Changelog

## v1.2.0 - 2026-11-28

- Added plot photos to registry-service. `POST /v1/plots/{id}/photo` stores one photo per plot in S3 under `{farm_id}/{plot_id}/photo` and returns `plot_id`, `key` and `content_type`. `GET /v1/plots/{id}/photo` returns the photo. Only JPEG, PNG and WebP up to 5 MB. An S3 failure returns `503 UNAVAILABLE`.

## v1.1.0 - 2026-11-23

- Added `GET /v1/farms/{id}/summary` to registry-service. It returns `farm_id`, `plot_count` and `total_area_m2` for a farm, and `404 NOT_FOUND` for an unknown farm.

## v1.0.0 - 2026-11-22

- First version: registry-service (crops, soils, emitters, farms and plots on SQLite or PostgreSQL), planner-service, weather-service and the frontend.
