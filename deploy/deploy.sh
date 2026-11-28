#!/usr/bin/env bash
# Brings the whole AgroPilot stack up on this EC2 instance: PostgreSQL in Docker,
# registry-service, weather-service, planner-service and the frontend.
#
# Run by .github/workflows/deploy.yaml, after it checked out the commit to deploy.
# Every step works on a clean instance and on one that was already deployed many times.
set -euo pipefail

: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}"
SERVICES=/home/ubuntu/AgroPilot-App/services
UV=/home/ubuntu/.local/bin/uv

# 1. Tools: install only what is missing.
if [ ! -x "$UV" ]; then
  curl -LsSf https://astral.sh/uv/0.13.6/install.sh | sh
fi
PACKAGES=""
command -v docker >/dev/null || PACKAGES="$PACKAGES docker.io"
command -v npm >/dev/null || PACKAGES="$PACKAGES nodejs npm"
if [ -n "$PACKAGES" ]; then
  sudo apt-get update
  sudo apt-get install -y $PACKAGES
fi

# 2. PostgreSQL in Docker. The named volume keeps the data.
if ! sudo docker ps -a --format '{{.Names}}' | grep -qx postgres; then
  sudo docker run -d --name postgres --restart unless-stopped \
    -e POSTGRES_USER=registry \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -e POSTGRES_DB=registry \
    -v pgdata:/var/lib/postgresql/data \
    -p 127.0.0.1:5432:5432 \
    postgres:17 \
    || { sudo docker rm -f postgres; exit 1; }
fi
sudo docker start postgres
for i in $(seq 1 30); do
  sudo docker exec postgres pg_isready -h 127.0.0.1 -U registry -d registry && break
  sleep 1
done

# 3. .env files: written from scratch on every run, never appended.
cat > "$SERVICES/registry-service/.env" <<EOF
DATABASE_URL=postgresql://registry:$POSTGRES_PASSWORD@127.0.0.1:5432/registry
AWS_S3_BUCKET=david-agropilot-photos
AWS_REGION=eu-north-1
EOF

cat > "$SERVICES/weather-service/.env" <<EOF
PROVIDER_BASE_URL=https://api.open-meteo.com/v1/forecast
PROVIDER_API_KEY=
PROVIDER_TIMEOUT_SECONDS=5
PROVIDER_RETRIES=2
FORECAST_FRESH_SECONDS=10800
FORECAST_MAX_STALE_SECONDS=86400
RETRY_AFTER_SECONDS=60
EOF

cat > "$SERVICES/planner-service/.env" <<EOF
REGISTRY_URL=http://127.0.0.1:8000
WEATHER_URL=http://127.0.0.1:8001
REGISTRY_TIMEOUT_SECONDS=3
WEATHER_TIMEOUT_SECONDS=20
EOF

cat > "$SERVICES/frontend/.env.local" <<EOF
REGISTRY_URL=http://127.0.0.1:8000
WEATHER_URL=http://127.0.0.1:8001
PLANNER_URL=http://127.0.0.1:8002
EOF

# 4. Python dependencies, and seed only an empty database (seeding drops the tables).
for svc in registry-service weather-service planner-service; do
  (cd "$SERVICES/$svc" && "$UV" sync --locked)
done
if [ -z "$(sudo docker exec postgres psql -U registry -d registry -tAc "SELECT to_regclass('public.plots')")" ]; then
  (cd "$SERVICES/registry-service" && "$UV" run python seed_postgres.py)
fi
# Tables added to tables.py after the first seed. Existing tables and their rows are left alone.
(cd "$SERVICES/registry-service" && "$UV" run python -c \
  "import database, tables; from sqlalchemy import create_engine; tables.metadata.create_all(create_engine(database.driver_url(database.database_url())))")

# 5. Frontend: build once per deploy. next start serves this build.
(cd "$SERVICES/frontend" && npm ci && npm run build)

# 6. systemd units from the repo.
sudo cp "$SERVICES/registry-service/registry.service" \
        "$SERVICES/weather-service/weather.service" \
        "$SERVICES/planner-service/planner.service" \
        "$SERVICES/frontend/frontend.service" \
        /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable registry.service weather.service planner.service frontend.service
sudo systemctl restart registry.service weather.service planner.service frontend.service

# 7. Health checks: a service that crashes on startup turns the job red.
wait_for() {
  local name=$1 url=$2
  for i in $(seq 1 30); do
    if curl -fsS -o /dev/null "$url"; then
      echo "$name is up"
      return 0
    fi
    sleep 2
  done
  echo "$name did not start"
  sudo journalctl -u "$name.service" -n 50 --no-pager
  return 1
}
wait_for registry http://127.0.0.1:8000/health
wait_for weather http://127.0.0.1:8001/health
wait_for planner http://127.0.0.1:8002/health
wait_for frontend http://127.0.0.1:3000/
