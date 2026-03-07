# Prompt 10 — SOT Invariant Check

## Goal
Verify that the implementation matches all invariants declared in
`TOOL_DOCUMENT_CATALOG_QUERY_SOT.md`.

## Checks

1. **Service exception boundary**: only `ValueError` and `PermissionError` escape.
2. **Sort fields**: all 10 declared fields accepted; invalid field raises `ValueError`.
3. **Tie-breaker**: `document_id` ascending always applied.
4. **Catalog loader path safety**: absolute path, `..`, null bytes all raise `ValueError`.
5. **CLI stdout is JSON-only**: no plain-text errors on stdout.
6. **Pagination bounds**: `limit` 1–500, `offset` ≥ 0; outside range raises `ValueError`.
7. **No writes**: no INSERT/UPDATE/DELETE anywhere in codebase.
8. **No LLM imports**: no `openai`, `anthropic`, `langchain`, etc.
9. **OpenAPI snapshot**: no drift from committed file.
10. **response_hash**: not emitted (disabled).
