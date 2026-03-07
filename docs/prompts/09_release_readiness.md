# Prompt 09 — Release Readiness

## Checklist

- [ ] `pytest -q` all green
- [ ] `UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py` snapshot committed
- [ ] `pytest tests/test_openapi_snapshot.py` passes (no env var)
- [ ] `python -m document_catalog_query.cli.main health` outputs stable JSON
- [ ] `techvault-tool-validate <repo_path>` exits 0
- [ ] `techvault-tool-security-scan <repo_path>` exits 0
- [ ] `techvault-tool-register --apply` completed
- [ ] `document_catalog_query` added to `backend/platform/enabled_tools.toml`
- [ ] Repo placed at `backend/tools/document_catalog_query/`
