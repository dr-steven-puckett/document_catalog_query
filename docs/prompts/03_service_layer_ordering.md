# Prompt 03 — Service Layer Ordering

## Goal
Implement deterministic filter, sort, and paginate logic in `core/service.py`.

## Requirements
- Filter by all supported fields (document_id, title, author, library_id, group_id,
  security_level, doc_type, language, status, ingest_date_from, ingest_date_to).
- Sort by any VALID_SORT_FIELDS with `document_id` tie-breaker.
- Paginate with limit/offset; validate bounds.
- Reject invalid sort_by / sort_dir with ValueError.
- Service exception boundary: only ValueError and PermissionError escape.

## Checkpoint
- `pytest tests/test_ordering_pagination.py -q` passes.
