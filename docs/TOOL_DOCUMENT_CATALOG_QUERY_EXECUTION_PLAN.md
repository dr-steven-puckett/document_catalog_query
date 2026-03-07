# TOOL DOCUMENT CATALOG QUERY — EXECUTION PLAN (Phase 0–6)

Run each phase in order. Do not proceed until the checkpoint passes.

## Phase 0 — Scaffold
- Create repo tree, package skeleton, tool.toml, README, openapi.snapshot.json placeholder, docs/.
- Include `cli/` package and `core/catalog_loader.py`.
- Create `docs/prompts/README.md`.

Checkpoint 0:
- `python -c "import document_catalog_query"` succeeds
- `pytest -q` collects

## Phase 1 — Contracts first (schemas + determinism helpers)
- Define Pydantic request/response schemas in `api/schemas.py`.
- Add canonical JSON helper in `core/determinism.py`.
- Add contract tests.

Checkpoint 1:
- `pytest tests/test_contract_schemas.py -q` passes

## Phase 2 — Service layer
- Implement filter/sort/paginate logic in `core/service.py`.
- Implement catalog loader + normalization in `core/catalog_loader.py`.
- Add ordering + pagination invariants and shuffle test.

Checkpoint 2:
- `pytest tests/test_ordering_pagination.py -q` passes

## Phase 3 — API adapter + CLI adapter
- Implement FastAPI router, deps.
- Implement CLI commands backed by service layer.
- Standalone `--catalog-file` mode.

Checkpoint 3:
- `python -m document_catalog_query.cli.main health` returns valid JSON
- `python -m document_catalog_query.cli.main query --catalog-file tests/fixtures/catalog_small.json` returns valid JSON

## Phase 4 — OpenAPI snapshot
- Implement `api/openapi_snapshot.py` + snapshot test.

Checkpoint 4:
- `UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q`
- `pytest tests/test_openapi_snapshot.py -q` passes

## Phase 5 — Determinism + CLI tests + full suite
- Byte-identical JSON tests.
- CLI smoke tests.
- API smoke tests.

Checkpoint 5:
- `pytest -q` all green

## Phase 6 — Tooling Gates
```bash
techvault-tool-validate <repo_path>
techvault-tool-security-scan <repo_path>
techvault-tool-register <repo_path> --techvault-root <root> --apply
```
