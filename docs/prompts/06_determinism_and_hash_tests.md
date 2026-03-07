# Prompt 06 — Determinism and Tests

## Goal
Add byte-identical JSON determinism tests and full test suite.

## Requirements
- `tests/test_determinism_json.py`: assert canonical_json is stable, keys are sorted,
  trailing newline present, byte-identical output for repeated calls.
- `tests/test_ordering_pagination.py`: sort stability, tie-breaker, shuffle safety,
  pagination stability, empty results.
- `tests/test_cli_smoke.py`: subprocess smoke tests, byte-identical stdout on repeat.
- `tests/test_api_smoke.py`: TestClient smoke tests.

## Checkpoint
- `pytest -q` all green.
