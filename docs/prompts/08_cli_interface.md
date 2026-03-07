# Prompt 08 — CLI Interface

## Goal
Implement the argparse CLI adapter.

## Requirements
- `health` subcommand: print `{"status":"ok","tool_id":"document_catalog_query"}`.
- `query` subcommand: accept all filter, sort, and pagination options.
- `--catalog-file` required for standalone mode.
- stdout: canonical JSON only. stderr: errors only. exit 0/1.
- No Python tracebacks in stderr.

## Checkpoint
- `python -m document_catalog_query.cli.main health` exits 0, valid JSON.
- `python -m document_catalog_query.cli.main query --catalog-file tests/fixtures/catalog_small.json` exits 0.
