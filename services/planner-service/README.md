# planner-service

Answers the grower's question: should I water this plot today, and for how many minutes? It reads the plot from registry-service and the forecast from weather-service, and calculates a day-by-day plan. It talks to them over HTTP only.

Every number in a plan comes from `engine.py`: plain functions, no network, no AI model. The formulas, the units and three cases calculated by hand are in the skill `.claude/skills/irrigation-calc-reference/SKILL.md`. The sources (FAO-56) are in `docs/research/fao56.md`.

## Run it

From `services/planner-service`:

```bash
uv sync
cp .env.example .env      # every variable is required
uv run uvicorn main:app --host 127.0.0.1 --port 8002
uv run pytest
```

registry-service (port 8000) and weather-service (port 8001) must be running for a plan. If a variable is missing, the service stops at startup and lists the missing names.

## API

`GET /v1/plots/{id}/plan?days={days}`: `days` is 1 to 7 (default 7). The first day is today. `days` is checked before any other service is called.

```json
{
  "plot_id": "c8f3d1b0-4d2e-5a1b-8b22-1d6e3f702002",
  "crop_id": "bell-pepper",
  "bucket_capacity_mm": 41.5,
  "stale": false,
  "days": [
    {
      "date": "2026-08-20",
      "et0_mm": 6.0,
      "rain_mm": 0.0,
      "kc": 1.05,
      "etc_mm": 6.3,
      "need_mm": 0.0,
      "litres": 0.0,
      "run_minutes": 0.0,
      "bucket_end_mm": 35.2,
      "stale": false
    },
    {
      "date": "2026-08-23",
      "et0_mm": 6.0,
      "rain_mm": 0.0,
      "kc": 1.05,
      "etc_mm": 6.3,
      "need_mm": 18.9,
      "litres": 7560.0,
      "run_minutes": 204.1,
      "bucket_end_mm": 35.2,
      "stale": false
    }
  ]
}
```

(Two of the seven days are shown. This is the pepper-on-sand case from the skill: 400 m², rows 1.2 m, emitters 0.3 m apart, 2 L/h.)

| Field | Meaning |
|---|---|
| `et0_mm`, `rain_mm` | From the forecast, unchanged |
| `kc` | Crop coefficient for that day of the crop's season |
| `etc_mm` | Water the crop uses that day: `kc × et0_mm` |
| `need_mm` | Irrigation depth to apply that day, mm over the plot. 0 means no irrigation |
| `litres` | `need_mm × area_m2` |
| `run_minutes` | How long to run the drip system. 0 on a day with no irrigation. The day stays in the list |
| `bucket_end_mm` | Water in the root zone at the end of the day |
| `stale` | `true` when the forecast is stale (every day, then) |
| `bucket_capacity_mm` | The size of the bucket: soil water per metre times root depth |

Numbers are rounded for display only (minutes to 0.1, mm to 0.01). The frontend shows whole minutes.

`GET /health` returns `{"status": "ok"}`.

## Errors

`application/problem+json` with a `code`.

| Status | Code | When |
|---|---|---|
| 422 | `VALIDATION` | `days` outside 1 to 7 or not a number. Also a plot whose crop has no irrigation parameters, or planted after the forecast starts |
| 404 | `NOT_FOUND` | Unknown plot |
| 503 | `UPSTREAM_UNAVAILABLE` | registry-service or weather-service is down, does not answer in time, or sends something unusable. The `detail` names the service, for example `weather-service is not reachable` |

A stale forecast still gives a plan, with `stale: true` on every day. A missing, late or invalid answer from another service never turns into a plan: there is no day list in a 503, and the planner never fills in zeros.

## Assumptions

Read these before trusting a number. Each is explained in the skill and can be changed in `crops.py` or `engine.py`.

- **The bucket is full at the start of today.** The registry has no soil moisture. A plot that was not watered for a long time would really need water earlier than the plan says.
- **Irrigate when the day would end below half of the bucket.** FAO-56 recommends a crop-specific fraction (tomato 0.40, pepper 0.30). The task asked for half.
- **Crops:** tomato and bell pepper only, with the Kc, stage lengths and root depth in `crops.py`. A plot with another crop gets 422.
- **After the season ends** (day number past the sum of the four stages) the Kc stays at its end value. The seed plots were planted months ago, so today they are in this case.
- Rain counts in full. There is no stress factor, no drip efficiency loss and no correction of Kc for the wetted fraction.
- Stage lengths are the Mediterranean rows of FAO-56 Table 11. The book says to use local data.

## Settings (`.env`)

| Variable | Meaning | Example |
|---|---|---|
| `REGISTRY_URL` | Where registry-service is | `http://127.0.0.1:8000` |
| `WEATHER_URL` | Where weather-service is | `http://127.0.0.1:8001` |
| `REGISTRY_TIMEOUT_SECONDS` | Timeout of one registry call | `3` |
| `WEATHER_TIMEOUT_SECONDS` | Timeout of the weather call. Longer, because the weather-service may retry its provider | `20` |

## Layout

- `main.py`: the route, validation and error handling.
- `engine.py`: the calculation. No network, no clock.
- `crops.py`: the crop numbers, with their FAO-56 sources.
- `clients.py`: the calls to registry-service and weather-service, and the checks of their answers.
- `config.py`: settings, read with pydantic-settings.
- `docs/research/fao56.md`: the research notes.
- `tests/`: automated tests. `test_engine.py` holds the hand-calculated cases.
