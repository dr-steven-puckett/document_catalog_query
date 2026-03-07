# TechVault Library Tool Template

This file is the reusable entrypoint for all TechVault library tool repos.

## Required Documents

- `TOOL_DOCUMENT_CATALOG_QUERY_SOT.md` — normative source of truth.
- `TOOL_DOCUMENT_CATALOG_QUERY_EXECUTION_PLAN.md` — phased build sequence.
- `TOOL_DOCUMENT_CATALOG_QUERY_ROADMAP.md` — non-binding future ideas only.

## Architecture Contract (Mandatory)

Every tool implements three interfaces over shared logic:

- Service layer (`core/service.py`) as canonical deterministic logic
- FastAPI adapter (`api/router.py`)
- CLI adapter (`cli/main.py`)

API and CLI must call the same service functions.

## Determinism Requirement

Tools must enforce:

- stable sorting with explicit tie-breakers
- stable pagination
- byte-identical JSON for identical inputs
- input-order independence (shuffle-safe)

## Template Version

2.0.0
