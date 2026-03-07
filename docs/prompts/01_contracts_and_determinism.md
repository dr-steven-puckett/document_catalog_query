# Prompt 01 — Contracts and Determinism Helpers

## Goal
Define schema contracts and canonical determinism primitives.

## Requirements
- Define `HealthResponse`, `QueryRequest`, `DocumentRecord`, `QueryResponse` in `api/schemas.py`.
- Implement `canonical_json` and `canonical_json_bytes` in `core/determinism.py`.
- Enforce UTF-8 and sorted JSON keys.
- Add contract tests in `tests/test_contract_schemas.py`.

## Checkpoint
- `pytest tests/test_contract_schemas.py -q` passes.
