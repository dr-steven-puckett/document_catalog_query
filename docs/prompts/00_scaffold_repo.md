# Prompt 00 — Scaffold Repository

## Goal
Scaffold a deterministic TechVault tool repository that matches the template baseline.

## Requirements
- Create root files: `tool.toml`, `README.md`, `openapi.snapshot.json` (placeholder), `pyproject.toml`, `pytest.ini`.
- Create package folders: `api/`, `core/`, `cli/` under `document_catalog_query/`.
- Create `docs/prompts/README.md`.
- Match `STANDARD_REPO_SKELETON.md` exactly.
- Package-relative imports only.

## Checkpoint
- `python -c "import document_catalog_query"` succeeds.
- `pytest -q` collects tests.
