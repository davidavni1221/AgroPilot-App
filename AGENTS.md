# AgroPilot

## Project facts

- Work in `services/registry-service`. Run commands from that folder.
- Run the tests with `uv run pytest`.
- Create or reset the database with `bash seed_registry.sh` (needs the `sqlite3` tool). Never edit `registry.db` by hand. It is not tracked by git.
- Start the service with `uv run uvicorn main:app --host 127.0.0.1 --port 8000`.
- Every error is `application/problem+json` with a `code`: `VALIDATION`, `NOT_FOUND`, `CONFLICT` or `UNAVAILABLE`.
- Dates are always `YYYY-MM-DD`.
- Delete functionality that the task does not list.

## How to work

1. **Think before coding.** Do not assume. Do not hide confusion. Surface tradeoffs, and ask when the request is unclear.
2. **Simplicity first.** Write the minimum code that solves the problem. Nothing speculative.
3. **Surgical changes.** Touch only what you must. Clean up only your own mess.
4. **Goal-driven execution.** Define the success criteria, then loop until they are verified (for example, `uv run pytest` passes).
