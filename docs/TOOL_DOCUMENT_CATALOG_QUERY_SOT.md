# TechVault Library Tool — DOCUMENT CATALOG QUERY Source of Truth

**Tool ID:** `document_catalog_query`
**Type:** Standalone deterministic tool repository (read-only metadata query)
**Integration:** Added to TechVault via standard platform registration.
**This document is the single source of truth.** Implementations MUST match this spec.

---

## 0) Determinism Contract (Non-Negotiable)

- Explicit sorting for all collections.
- Stable pagination with stable tie-breakers (`document_id` ascending).
- No reliance on dict/set iteration order.
- Identical inputs → byte-identical JSON outputs (canonical JSON serialization).
- Input order independence: shuffled equivalent inputs MUST yield identical outputs.
- No LLM usage. No orchestration frameworks. No background jobs.

### 0.1 Canonical JSON rules
- UTF-8, `sort_keys=true`, compact separators, one trailing newline.
- No NaN/Infinity.
- CLI output is JSON-only to stdout; errors are emitted to stderr only.

### 0.2 Response hash
`response_hash_enabled = false` (not used by this tool).

---

## 1) Core Architecture (Mandatory)

- **Service Layer (`core/service.py`)**: canonical deterministic filter/sort/paginate logic.
- **FastAPI Router (`api/router.py`)**: integration adapter.
- **CLI Interface (`cli/main.py`)**: standalone execution adapter.
- **Agent Callable (`tool.py`)**: stub for future agent-mode.

API and CLI MUST call the same service functions.

---

## 2) Purpose and Scope

### 2.1 Purpose
Deterministic read-only query tool for browsing and filtering TechVault's ingested
document catalog metadata stored in Postgres.

### 2.2 In scope
- Deterministic filtering over document metadata
- Stable sorting and pagination
- Canonical JSON output
- API + CLI + agent/tool callable
- Standalone catalog-file mode for tests

### 2.3 Out of scope / non-goals
- Semantic search, vector search, chunk retrieval
- Summarization, RAG
- Fuzzy ranking
- Writes to database
- LLM calls
- New platform abstractions

---

## 3) Repository Layout

```
./
  tool.toml
  README.md
  openapi.snapshot.json
  pyproject.toml
  pytest.ini
  docs/
    TOOL_DOCUMENT_CATALOG_QUERY_SOT.md
    TOOL_DOCUMENT_CATALOG_QUERY_EXECUTION_PLAN.md
    TOOL_DOCUMENT_CATALOG_QUERY_ROADMAP.md
    TOOL_TEMPLATE.md
    prompts/
      README.md
      00_scaffold_repo.md  ...  10_sot_invariant_check.md
  document_catalog_query/
    __init__.py
    tool.py
    api/
      __init__.py
      router.py
      schemas.py
      deps.py
      openapi_snapshot.py
    core/
      __init__.py
      service.py
      determinism.py
      catalog_loader.py
    cli/
      __init__.py
      main.py
  tests/
    test_contract_schemas.py
    test_ordering_pagination.py
    test_determinism_json.py
    test_cli_smoke.py
    test_openapi_snapshot.py
    test_api_smoke.py
    fixtures/
      catalog_small.json
      catalog_shuffled.json
```

---

## 4) Filtering Fields

| Filter param       | Match type                    | DB column        |
|--------------------|-------------------------------|------------------|
| `document_id`      | exact (case-sensitive)        | `document_id`    |
| `title`            | case-insensitive substring    | `title`          |
| `author`           | case-insensitive substring    | `author`         |
| `library_id`       | exact (case-sensitive)        | `library_id`     |
| `group_id`         | exact (case-sensitive)        | `group_id`       |
| `security_level`   | exact (case-sensitive)        | `security_level` |
| `doc_type`         | exact (case-sensitive)        | `doc_type`       |
| `language`         | case-insensitive exact        | `language`       |
| `status`           | exact (case-sensitive)        | `status`         |
| `ingest_date_from` | `ingested_at >= date` (ISO)   | `ingested_at`    |
| `ingest_date_to`   | `ingested_at <= date` (ISO)   | `ingested_at`    |

---

## 5) Sort Fields

Valid `sort_by` values: `document_id`, `title`, `author`, `library_id`,
`group_id`, `security_level`, `doc_type`, `language`, `status`, `ingest_date`.

Tie-breaker: always `document_id` ascending.
Invalid `sort_by` → `ValueError`.

---

## 6) Pagination

- `limit` (int, 1–500, default 25)
- `offset` (int, ≥0, default 0)
- Stable: same inputs → same page.

---

## 7) Service Exception Boundary

Only `ValueError` and `PermissionError` may escape service functions.
All unexpected exceptions wrapped as `ValueError("Unexpected error: <ClassName>: <msg>")`.

---

## 8) API Contract

- Prefix: `/v1/tools/document_catalog_query`
- Tags: `["tools:document_catalog_query"]`

### Endpoints

```
GET  /health  → {"status": "ok", "tool_id": "document_catalog_query"}
POST /query   → QueryResponse
```

### Error mapping
- `PermissionError` → HTTP 403
- `ValueError` containing "not found" → HTTP 404
- other `ValueError` → HTTP 400

---

## 9) CLI Contract

```bash
python -m document_catalog_query.cli.main health
python -m document_catalog_query.cli.main query \
  --catalog-file <path> \
  [--document-id ID] [--title SUBSTR] [--author SUBSTR] \
  [--library-id ID] [--group-id ID] [--security-level LEVEL] \
  [--doc-type TYPE] [--language LANG] [--status STATUS] \
  [--ingest-date-from YYYY-MM-DD] [--ingest-date-to YYYY-MM-DD] \
  [--sort-by FIELD] [--sort-dir asc|desc] \
  [--limit N] [--offset N]
```

stdout: canonical JSON only. stderr: errors only. exit 0/1.

---

## 10) Catalog JSON Format (Standalone / Test Mode)

Array of document record objects with fields:
- `document_id` (str, required)
- `status` (str, required)
- `title`, `author`, `library_id`, `group_id`, `security_level`, `doc_type`,
  `language`, `ingested_at` (str|null, optional)

---

## 11) Determinism Tests (Required)

- Byte-identical JSON for same request repeated N times.
- Sort stability: equal primary-key ties resolved by `document_id` ascending.
- Shuffle-safe: shuffled catalog produces identical results.
- Pagination stability.
- Empty result tests.
- Invalid sort_by rejection.
- Date range filter tests.
- CLI stdout byte-identical on repeat.

---

## 12) Done Definition

- `pytest -q` all pass.
- OpenAPI snapshot stable.
- Determinism tests pass (byte-identical JSON).
- CLI smoke tests pass. Standalone `--catalog-file` mode works.
- Service exception boundary enforced.
- `techvault-tool-validate <repo_path>` exits 0.
- `techvault-tool-security-scan <repo_path>` exits 0.
