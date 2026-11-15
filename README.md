# AgroPilot

AgroPilot helps a grower manage agricultural crops with modern AI. 


## Where to start

Services live under `services/`. The service in the repository today is `registry-service`, a FastAPI application.

## Run it after a fresh clone

You need:

- Linux or macOS. On Windows, use WSL (Ubuntu) and run every command below inside it.
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- The `sqlite3` command-line tool (on Ubuntu: `sudo apt install sqlite3`)

```bash
git clone https://github.com/davidavni1221/ArgoPilot-App.git
cd ArgoPilot-App/services/registry-service
uv sync                    # installs Python and the dependencies
bash seed_registry.sh      # creates registry.db (not tracked by git)
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/health. A running service returns `{"status": "ok"}`.
The interactive API docs are at http://127.0.0.1:8000/docs.

Run the tests (from `services/registry-service`):

```bash
uv run pytest
```

More details are in [services/registry-service/README.md](services/registry-service/README.md).
