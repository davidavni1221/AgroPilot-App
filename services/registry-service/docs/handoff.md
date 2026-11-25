# Handoff: where the work stands

Written 2026-11-16 so work can continue from another computer. Chat history is local to one machine and does not travel. This file does.

## Git state

- `main` is on GitHub and holds everything merged so far: P1 (PR #1), the `registry-api` skill with its evals, and `.claude/settings.json` (enables the Superpowers plugin).
- `p2` is the working branch for the P2 task. It starts from `main` with the PostgreSQL migration merged in (merge commit `5684f91`).
- P2 ends with a PR from `p2` into `main`. Read your own diff on GitHub before merging.
- Updated 2026-11-22: P2 is built (weather-service, planner-service, frontend) and its PR #2 (`p2` into `main`) is open. The repository README describes the four services.

## What is already built

- **registry-service** runs on SQLite by default (`registry.db`) and on PostgreSQL when `DATABASE_URL` is set. Existing endpoints behave the same on both.
- **Tests:** `uv run pytest` from `services/registry-service`. Without PostgreSQL: 108 passed, 102 skipped. With PostgreSQL: 210 passed (checked 2026-11-22).
- **Skills and rules** in `.claude/`: `registry-api` (API conventions, with evals), `drip-irrigation`, and the rules in `.claude/rules/`.
- **PostgreSQL design and plan:** `docs/superpowers/specs/2026-11-15-postgres-support-design.md` and `docs/superpowers/plans/2026-11-15-postgres-support.md`.
- **Decision history:** `docs/judgment-log.md`.

## Known behavior differences (accepted)

- `GET /v1/crops` is now ordered by id.
- A NUL character in an id, path or query value gives 422 on PostgreSQL. SQLite gives 404, an empty list or a field-specific 422.

## Open question for P2

Resolved 2026-11-16: the user chose SQLAlchemy (Core). See `docs/superpowers/specs/2026-11-16-sqlalchemy-design.md`.

## Setting up on a new computer

Needs git, `uv`, VS Code with Claude Code. Docker only if you want PostgreSQL.

```bash
git clone https://github.com/davidavni1221/AgroPilot-App.git
cd AgroPilot-App
git switch p2
cd services/registry-service
uv sync
bash seed_registry.sh        # creates registry.db (needs sqlite3)
uv run pytest
```

Not in git, so recreate by hand:

- `.env`: copy `.env.example` and fill in the password. Never commit it.
- PostgreSQL for tests (optional): start a PostgreSQL 16 container named `registry-pg`, then
  `docker exec registry-pg createdb -U postgres registry_test`.
  Set `TEST_DATABASE_URL` to the `registry_test` database. Without it the PostgreSQL tests are skipped.
- Superpowers plugin: `.claude/settings.json` turns it on, but install it again on each machine (Manage plugins in the `/` menu).
- Local only and excluded from git: `CLAUDE.md` in `services/registry-service` and `.superpowers/`.

## Starting a new chat

Say: "Read `services/registry-service/docs/handoff.md`, then I will send you the P2 task."
