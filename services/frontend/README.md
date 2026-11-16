# frontend

The AgroPilot web app for growers: the farms and their plots, and for each plot today's answer ("Water for 38 minutes" or "No irrigation today") with the plan for the next 7 days. Next.js (App Router), TypeScript, Tailwind CSS and shadcn/ui.

The browser never calls the services. Pages fetch their data on the server, and every call lives in `src/lib/`.

## Run it

Needs Node.js (LTS). From `services/frontend`:

```bash
npm install
cp .env.example .env.local    # addresses of the three services
npm run dev                   # http://localhost:3000
npm run build && npm run lint
```

Start registry-service (8000), weather-service (8001) and planner-service (8002) first. Without them the pages show what is down.

## Settings (`.env.local`)

| Variable | Meaning | Example |
|---|---|---|
| `REGISTRY_URL` | registry-service | `http://127.0.0.1:8000` |
| `WEATHER_URL` | weather-service, used only for the status line | `http://127.0.0.1:8001` |
| `PLANNER_URL` | planner-service | `http://127.0.0.1:8002` |

## Pages

- `/`: every farm with its plots. Each plot links to `/plots/{id}`.
- `/plots/{id}`: today's recommendation first, then the next 7 days. The bucket gauge shows how full the soil is. The mark in the middle is the half line, below which the planner waters.
- Every page shows a status line: whether each service answers `GET /health`.

When the forecast is stale, the plot page says so under today's answer and on every day it affects. When a service fails, the page names it in plain words and does not show a stack trace.

## Layout

- `src/lib/services.ts`: the one place that calls a service. Timeouts, error kinds and the plain-language message for each.
- `src/lib/registry.ts`, `src/lib/planner.ts`: the calls the pages need.
- `src/app/`: the pages. Fetching components sit inside `<Suspense>`, which this Next.js version (Cache Components) requires for live data.
- `src/components/`: `recommendation`, `day-list`, `bucket-gauge`, `failure-notice`, `service-status`. `ui/` is shadcn/ui.

The design follows the `frontend-design` skill: one typeface (Atkinson Hyperlegible, made for reading in poor light), a sage and spruce palette with blue for water and amber for an old forecast, and one memorable element, the bucket gauge.
