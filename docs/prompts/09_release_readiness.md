# Prompt 09 — Release Readiness

## Checklist

- [ ] `pytest -q` all green
- [ ] `UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py` snapshot committed
- [ ] `pytest tests/test_openapi_snapshot.py` passes (no env var)
- [ ] `python -m document_catalog_query.cli.main health` outputs stable JSON
- [ ] `techvault-tool-validate <repo_path>` exits 0
- [ ] `techvault-tool-security-scan <repo_path>` exits 0
- [ ] Repo placed at `backend/tools/document_catalog_query/` (or added as a submodule)
- [ ] TechVault manifest validation passes and tool is discovered automatically
- [ ] Activation confirmed via local operator override or `enabled_by_default` in `tool.toml`
