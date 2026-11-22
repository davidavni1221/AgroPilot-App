# AgroPilot

AgroPilot helps a grower manage agricultural crops with modern AI. Its daily question is: should I water this plot today?

## Services

Four services live under `services/`. They talk over HTTP only.

| Service | Port | What it does |
|---|---|---|
| `registry-service` | 8000 | Farms, plots, crops, soils and emitters. SQLite by default, PostgreSQL when `DATABASE_URL` is set |
| `weather-service` | 8001 | Daily ET0 and rain from Open-Meteo, cached, with a stale answer when the provider is down |
| `planner-service` | 8002 | The 7-day irrigation plan for a plot |
| `frontend` | 3000 | Next.js app: farms, plots, today's answer and the week |

Each service has its own README with the API, the settings and the tests.

## Run it after a fresh clone

You need:

- Linux or macOS. On Windows, use WSL (Ubuntu) and run every command below inside it.
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- The `sqlite3` command-line tool (on Ubuntu: `sudo apt install sqlite3`)
- Node.js, for the frontend

```bash
git clone https://github.com/davidavni1221/ArgoPilot-App.git
cd ArgoPilot-App/services
```

Start each service in its own terminal.

```bash
cd registry-service
uv sync
bash seed_registry.sh      # creates registry.db (not tracked by git)
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

```bash
cd weather-service
uv sync
cp .env.example .env       # every variable is required
uv run uvicorn main:app --host 127.0.0.1 --port 8001
```

```bash
cd planner-service
uv sync
cp .env.example .env       # every variable is required
uv run uvicorn main:app --host 127.0.0.1 --port 8002
```

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                # http://localhost:3000
```

Each Python service answers `GET /health` with `{"status": "ok"}`, and its API docs are at `/docs`.

Run the tests of a service with `uv run pytest` from its folder.

More details are in the README of each service:
[registry](services/registry-service/README.md),
[weather](services/weather-service/README.md),
[planner](services/planner-service/README.md),
[frontend](services/frontend/README.md).
