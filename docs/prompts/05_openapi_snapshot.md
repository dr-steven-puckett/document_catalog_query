# Prompt 05 — OpenAPI Snapshot

## Goal
Implement `api/openapi_snapshot.py` and the snapshot test.

## Requirements
- `generate_openapi()` creates a minimal FastAPI app with the router and returns `app.openapi()`.
- `tests/test_openapi_snapshot.py` reads `openapi.snapshot.json` and asserts no drift.
- `UPDATE_OPENAPI_SNAPSHOT=1` regenerates the snapshot.

## Checkpoint
- `UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q`
- `pytest tests/test_openapi_snapshot.py -q` passes (no env var).
