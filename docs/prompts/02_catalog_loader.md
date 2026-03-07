# Prompt 02 — Catalog Loader

## Goal
Implement safe catalog loading and normalization for standalone/test mode.

## Requirements
- Path safety: reject absolute paths, path traversal, null bytes, non-UTF-8.
- Validate required fields: `document_id`, `status`.
- Normalize to document_id ascending order.
- Raise `ValueError` for all error cases.

## Checkpoint
- Path safety tests pass.
- Catalog loads and normalizes correctly.
