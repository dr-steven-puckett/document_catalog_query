# document_catalog_query

Deterministic metadata query tool for browsing and filtering TechVault's
ingested document catalog metadata stored in Postgres.

## Purpose

Provides deterministic, read-only filtering over document metadata stored in
the TechVault `documents` table. Supports stable sorting, explicit pagination,
and canonical JSON output.

This tool is intentionally narrow. It does **not** perform semantic search,
vector retrieval, summarization, or any LLM-based operations.

## Architecture

```
document_catalog_query/
  api/          FastAPI router adapter
  core/         Canonical deterministic service logic + catalog loader
  cli/          argparse CLI adapter
  tool.py       Agent callable stub
tests/          Full pytest suite
```

API and CLI both call the same `core/service` functions.

## Supported filters

- `document_id` — exact match
- `title` — case-insensitive substring
- `author` — case-insensitive substring
- `library_id` — exact match
- `group_id` — exact match
- `security_level` — exact match (`public` / `private` / `protected` / `secret`)
- `doc_type` — exact match (`pdf` / `epub` / `txt` / `md` / `csv` / `docx` / `code` / `unknown`)
- `language` — case-insensitive exact match
- `status` — exact match (default `active`)
- `ingest_date_from` / `ingest_date_to` — ISO date strings (`YYYY-MM-DD`)

## Sort fields

`document_id`, `title`, `author`, `library_id`, `group_id`, `security_level`,
`doc_type`, `language`, `status`, `ingest_date`

Tie-breaker always applied on `document_id` ascending.

## Determinism guarantees

- Explicit sorting with stable tie-breakers
- Stable limit/offset pagination
- Canonical JSON (UTF-8, `sort_keys=true`, compact separators, trailing newline)
- Identical inputs produce byte-identical outputs
- No LLM calls, no randomness, no background jobs

## CLI usage

```bash
# Health
python -m document_catalog_query.cli.main health

# Query (standalone catalog-file mode)
python -m document_catalog_query.cli.main query \
  --catalog-file tests/fixtures/catalog_small.json \
  --status active \
  --sort-by title \
  --sort-dir asc \
  --limit 10 \
  --offset 0
```

## API

```
GET  /v1/tools/document_catalog_query/health
POST /v1/tools/document_catalog_query/query
```

## Deployment

Place this repo (or add it as a Git submodule) under `backend/tools/document_catalog_query/`.
TechVault discovers it automatically by finding `tool.toml`. Activation is determined
first by local TechVault operator overrides and otherwise by `enabled_by_default` in
`tool.toml`. Invalid manifests are surfaced clearly and not silently activated.

## Tests

```bash
pytest -q

# Regenerate OpenAPI snapshot
UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q
```
