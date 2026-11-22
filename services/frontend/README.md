# frontend

The AgroPilot web app for growers: the farms and their plots, and for each plot today's answer ("Water for 38 minutes" or "No irrigation today") with the plan for the next 7 days. A grower can also add a farm, a crop and a plot. Next.js (App Router), TypeScript, Tailwind CSS and shadcn/ui.

The browser never calls the services. Pages fetch their data on the server, forms are sent by server actions, and every call lives in `src/lib/`.

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

- `/`: every farm with its plots, sorted A to Z, and a search box that filters farms and plots as you type (a farm name brings all its plots, a plot or crop name brings that plot). It filters what the page already loaded, so there is no request per key.
  - A plot card shows the plot's name, crop, area and today's answer, and opens the plot's page, `/plots/{id}`. All cards are the same size.
  - Beside each plot: a pencil (change every field except the farm, as `PATCH /v1/plots/{id}` allows) and a trash button. Deleting asks first. Deleting the last plot of a farm deletes the farm too, and the question says so.
  - Beside each farm's name: a pencil (change the name), and a trash button only when the farm has no plots.
  - The **Add** button, top right beside the title, opens a window in the middle of the screen with an X. It asks what to add: a plot, a farm or a crop. A new farm or crop goes straight on to the plot form with it already chosen. The place search is Open-Meteo's free geocoding, called from the server, so the text typed there is sent to open-meteo.com. For a crop we already hold, such as Tomato or Bell pepper, the typed crop numbers are ignored and the stored ones are used. The match is by name (capitals and spaces do not matter), so "cherry tomato" counts as a new crop. ET0 is never entered: the weather service gets it from the plot's location.
  - There is no login and no owner in the registry yet, so everyone who opens the page sees and changes every farm.
- `/plots/{id}`: today's recommendation first and big, then the next 7 days. A ring shows how full the soil is, a bar chart shows the minutes of watering per day, and a table has the numbers. A link at the top goes back to `/`. The planner is asked once per visit.
- Every page shows a status line: whether each service answers `GET /health`.

When the forecast is stale, a plot's page says so under today's answer and on every day it affects. When a service fails, the page names it in plain words and does not show a stack trace.

## Layout

- `src/lib/services.ts`: the one place that calls a service. Timeouts, error kinds and the plain-language message for each.
- `src/lib/registry.ts`, `src/lib/planner.ts`, `src/lib/geocoding.ts`: the calls the pages need.
- `src/app/actions.ts`: what happens when a form is sent. It checks the input, calls the registry and refreshes the page. The window that sent the form closes when it is saved. The registry still has the last word, and its message is shown when it refuses.
- `src/app/`: the pages. Fetching components sit inside `<Suspense>`, which this Next.js version (Cache Components) requires for live data.
- `src/components/`: `add-button`, `modal`, `plot-card`, `recommendation`, `soil-ring`, `day-list`, `week-chart`, `failure-notice`, `service-status`, and `forms/`. `ui/` holds shadcn/ui components, and `circular-progress`, `chart` and `table` come from shadcn.io (see below).

## Components from shadcn.io

`circular-progress`, `chart` and `table` were added from https://www.shadcn.io with the shadcn CLI. The registry is set in `components.json` and the token is read from `SHADCNIO_TOKEN` in `.env.local`, which is git-ignored. You only need the token to add more components, not to run the app. They add two packages: `@ark-ui/react` and `recharts`.

The design follows the `frontend-design` skill: one typeface (Atkinson Hyperlegible, made for reading in poor light), a sage and spruce palette with blue for water and amber for an old forecast, and one memorable element, the soil ring.
