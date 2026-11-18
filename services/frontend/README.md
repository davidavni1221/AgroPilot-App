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

- `/`: the farmer's page. It shows the plots that came with the database (the four in `src/lib/seed.ts`), grouped by farm and sorted A to Z. Each plot card shows today's answer (it asks the planner, one card at a time, so the page appears first) and links to `/plots/{id}`. The search box filters farms and plots as you type: a farm name brings all its plots, a plot or crop name brings that plot. It filters what the page already loaded, so there is no request per key. The farmer only reads here. An **Admin** button at the top right opens `/admin`.
- `/admin`: for the Netafim team. Buttons to add a farm, a crop or a plot, then **every** farm and plot, including what was added through the app, with the same search box. Each farm has "Change the farm name", and "Delete this farm" when it has no plots (it asks "are you sure" first, and the registry refuses a farm that still has plots). A plot card opens `/admin/plots/{id}`. There is no login yet, so this page is hidden by layout only, not protected.
- `/admin/plots/{id}`: the same answer and 7 days as `/plots/{id}`, and under it "Change this plot" and "Delete this plot" (asks first).
- `/admin/plots/{id}/edit`: every plot field can be changed, as `PATCH /v1/plots/{id}` allows. The farm cannot (the registry has no way to move a plot).
- `/admin/farms/{id}/edit`: change a farm's name.
- `/plots/{id}`: today's recommendation first, then the next 7 days. A ring shows how full the soil is, a bar chart shows the minutes of watering per day, and a table has the numbers.
- `/farms/new`: add a farm (a name).
- `/crops/new`: add a crop. The grower enters the FAO-56 numbers (Kc at three stages, four stage lengths, root depth). ET0 is never entered: the weather service gets it from the plot's location. For a crop we already hold, such as Tomato or Bell pepper, the typed numbers are ignored and the stored ones are used. The match is by name (capitals and spaces do not matter), so "cherry tomato" counts as a new crop.
- `/plots/new`: add a plot. The grower picks the farm, crop, soil and emitter from lists and finds the location by place name. The place search is Open-Meteo's free geocoding, called from the server, so the text typed there is sent to open-meteo.com. The grower picks one match from the list, because a name like Beersheba exists in several countries.
- Every page shows a status line: whether each service answers `GET /health`.

When the forecast is stale, the plot page says so under today's answer and on every day it affects. When a service fails, the page names it in plain words and does not show a stack trace.

## Layout

- `src/lib/services.ts`: the one place that calls a service. Timeouts, error kinds and the plain-language message for each.
- `src/lib/registry.ts`, `src/lib/planner.ts`, `src/lib/geocoding.ts`: the calls the pages need.
- `src/app/actions.ts`: what happens when a form is sent. It checks the input, calls the registry and redirects. The registry still has the last word, and its message is shown when it refuses.
- `src/app/`: the pages. Fetching components sit inside `<Suspense>`, which this Next.js version (Cache Components) requires for live data.
- `src/components/`: `recommendation`, `soil-ring`, `day-list`, `week-chart`, `failure-notice`, `service-status`, and `forms/`. `ui/` holds shadcn/ui components, and `circular-progress`, `chart` and `table` come from shadcn.io (see below).

## Components from shadcn.io

`circular-progress`, `chart` and `table` were added from https://www.shadcn.io with the shadcn CLI. The registry is set in `components.json` and the token is read from `SHADCNIO_TOKEN` in `.env.local`, which is git-ignored. You only need the token to add more components, not to run the app. They add two packages: `@ark-ui/react` and `recharts`.

The design follows the `frontend-design` skill: one typeface (Atkinson Hyperlegible, made for reading in poor light), a sage and spruce palette with blue for water and amber for an old forecast, and one memorable element, the soil ring.
