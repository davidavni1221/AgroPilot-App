---
name: registry-api
description: API conventions for the AgroPilot registry-service (FastAPI, SQLite or PostgreSQL). Use whenever you add, change, fix, or test an endpoint, a route, a request or response model, a PATCH/POST/DELETE behavior, or an error response in services/registry-service, even if the user does not mention conventions, errors, or tests.
---

# Registry API conventions

Other services read this API, so every habit below exists to keep responses predictable. A surprise in one endpoint becomes a bug in a client we cannot see.

## Routes and responses

- Put every route under `/v1`. Clients pin to the version prefix, so an unversioned route cannot change later without breaking them.
- Return lists as JSON arrays. No rows means `200` and `[]`, never `404`: an empty list is a valid answer, and clients should not need error handling for it.
- Return only the fields the spec lists, through a `response_model` in `models.py`. Every extra field becomes something we can never remove.
- `PATCH` changes only the fields that are in the body. A missing field means "leave it alone"; an explicit `null` is a `422`, because these fields are required.

## Errors

Every error is `application/problem+json` (RFC 9457) with a stable `code`. Clients branch on `code`, so it must never be improvised.

| Code | Status | Use for |
|---|---|---|
| `VALIDATION` | 422 | Bad body or parameters, unknown ids inside a body |
| `NOT_FOUND` | 404 | The addressed resource does not exist |
| `CONFLICT` | 409 | The change clashes with existing data (duplicate name, farm that still has plots) |
| `UNAVAILABLE` | 503 | The database cannot be reached; always send `Retry-After` |

- Raise errors with `APIError` or the shared handlers in `main.py`. FastAPI's default error body is a different format, and one endpoint returning it breaks every client that parses errors.
- Do not catch a database error to return a custom body. The `503` handler already covers SQLite and PostgreSQL connection failures.

## Tests

- Every endpoint gets a test for the success case and one for every failure case it can return (`422`, `404`, `409`, `503`). Failure paths are where behavior silently drifts.
- Use the `client` fixture in `tests/conftest.py`. It runs each test on SQLite and, when `TEST_DATABASE_URL` is set, on PostgreSQL, so a query that only works on one database fails here and not in production.
- Run `uv run pytest` from `services/registry-service` before saying the work is done. Say what you ran and the result.

## When the spec is silent

If the spec does not say what to do in some case (a new status code, a new field, an odd input), ask. Invented behavior becomes a contract the moment a client depends on it.
