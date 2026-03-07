# Prompts Directory

This directory contains the Copilot execution prompts corresponding to each phase
of `TOOL_DOCUMENT_CATALOG_QUERY_EXECUTION_PLAN.md`.

| File | Phase | Goal |
|------|-------|------|
| `00_scaffold_repo.md` | Phase 0 | Scaffold repo structure |
| `01_contracts_and_determinism.md` | Phase 1 | Schemas + determinism helpers |
| `02_catalog_loader.md` | Phase 2a | Catalog loader + path safety |
| `03_service_layer_ordering.md` | Phase 2b | Filter/sort/paginate service |
| `04_api_interface.md` | Phase 3a | FastAPI router |
| `05_openapi_snapshot.md` | Phase 4 | OpenAPI snapshot |
| `06_determinism_and_hash_tests.md` | Phase 5a | Determinism tests |
| `07_final_gate.md` | Phase 6 | Validation gates |
| `08_cli_interface.md` | Phase 3b | CLI adapter |
| `09_release_readiness.md` | Phase 6+ | Release checklist |
| `10_sot_invariant_check.md` | Phase 6+ | SOT invariant check |
