# Prompt 04 — API Interface

## Goal
Implement the FastAPI router adapter.

## Requirements
- Prefix: `/v1/tools/document_catalog_query`
- Tags: `["tools:document_catalog_query"]`
- `GET /health` → HealthResponse
- `POST /query` → QueryResponse
- Error mapping: PermissionError→403, ValueError("not found")→404, ValueError→400
- Router calls service functions only (no duplicated logic).

## Checkpoint
- `pytest tests/test_api_smoke.py -q` passes.
