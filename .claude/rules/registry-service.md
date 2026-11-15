---
paths:
  - "services/registry-service/**/*.py"
---

# Registry service rules

- Every request body is a Pydantic model. Never use a `dict` or loose parameters for a body.
- Every numeric field in a request body has a constraint (`gt=0`, `ge=0`, or a range). No unbounded numbers.
- Every endpoint has a test in `tests/`, including at least one invalid-input case.
- Raise errors with `APIError` or the shared handlers, so every error stays `application/problem+json`.
