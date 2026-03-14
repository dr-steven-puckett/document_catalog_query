Build a new deterministic TechVault tool repository named `document_catalog_query` using the canonical tool template repository at:

`/home/spuckett1/projects/tools/techvault_tool_template`

You must inspect the template repository first and follow its architecture exactly. Do not invent a new architecture, workflow, or repository layout outside what the template defines.

## Goal

Create a standalone tool repo for `document_catalog_query`, a deterministic metadata query tool for browsing and filtering TechVault’s ingested document catalog metadata stored in Postgres.

This tool is intentionally narrow.

It must:
- provide deterministic filtering over document metadata
- support stable sorting and pagination
- expose API + CLI + agent/tool callable consistent with the template
- remain read-only
- avoid duplicating semantic search, vector search, chunk retrieval, summarization, or RAG endpoints

## Canonical source to follow

Use the template repository as the source of truth, especially its:
Use the template repository as the source of truth, especially its:
- prompts
- repo skeleton
- manifest conventions
- deterministic serialization conventions
- test patterns
- OpenAPI snapshot patterns
- CLI patterns
- platform integration conventions

Read and follow the template prompt phases from `docs/prompts/` before implementation.

## Required initial inspection order

Inspect the template repository first, especially:
- `docs/TOOL_SPEC_TEMPLATE.md`
- `docs/TOOL_PROMPT_GENERATOR.md`
- `docs/TOOL_AUTOMATION_SCHEME.md`
- `docs/TOOL_FACTORY_PIPELINE.md`
- `docs/STANDARD_REPO_SKELETON.md`
- `docs/TOOL_TEMPLATE.md`
- `docs/TOOL_TEMPLATE_EXECUTION_PLAN.md`
- `docs/prompts/`

Then inspect the relevant TechVault platform integration files and any example tool manifests / existing tool repos needed to mirror conventions.

## Tool specification

Implement the tool according to this specification:

### Name
`document_catalog_query`

### Purpose
Deterministic query tool for browsing and filtering TechVault’s ingested document catalog metadata stored in Postgres.

### Scope
Read-only metadata query only.

### Supported filtering fields
- `document_id`
- `title`
- `author`
- `library_id`
- `group_id`
- `security_level`
- `doc_type`
- `language`
- `status`
- ingest date range

### Supported sort fields
At minimum:
- `document_id`
- `title`
- `author`
- `library_id`
- `group_id`
- `security_level`
- `doc_type`
- `language`
- `status`
- `ingest_date`

### Deterministic requirements
- deterministic outputs only
- explicit sorting everywhere
- stable pagination
- no dict/set iteration reliance
- canonical JSON serialization
- explicit tie-break ordering with `document_id`
- no timestamps unless they are schema fields
- no LLM calls
- no orchestration frameworks
- offline operation
- no changes to core TechVault services except standard tool registration/integration points required by the platform

### Non-goals
Do not implement:
- semantic search
- vector search
- chunk retrieval
- summarization
- RAG behavior
- fuzzy ranking
- writes to database
- new platform abstractions

## Expected repository contents

Generate a full deterministic tool repository consistent with the template, including at least:
- `tool.toml`
- FastAPI router
- CLI entrypoint
- `schemas.py`
- `service.py`
- `router.py`
- agent/tool callable
- pytest suite
- deterministic ordering tests
- pagination tests
- OpenAPI snapshot
- `README.md`

## Implementation guidance

Keep the implementation as small and composable as possible.

Prefer the smallest deterministic implementation consistent with the template.

Use read-only access to the minimal required TechVault tables, preferring `documents` first and joining other tables only if necessary.

Do not broaden scope beyond document-level metadata browsing.

Do not duplicate other TechVault functionality.

## Integration requirements

Follow template and platform conventions for:
- `tool.toml`
- manifest naming
- API registration
- router registration
- CLI entrypoint naming
- canonical JSON output
- OpenAPI generation / snapshotting

TechVault discovers this tool automatically when the repository is present under
`backend/tools/document_catalog_query/` and contains a valid `tool.toml`. Activation
is determined first by local TechVault operator overrides and otherwise by
`enabled_by_default` in `tool.toml`.

Do not invent alternate registration mechanisms.

## Testing requirements

Produce tests proving determinism and stability, including:
- validation tests
- filter tests
- sort tests
- tie-break tests using `document_id`
- pagination stability tests
- empty result tests
- invalid sort field rejection
- invalid page token rejection if cursor pagination is used
- CLI output stability
- OpenAPI snapshot stability

Where the template includes canonical JSON helpers or shared deterministic utilities, reuse them instead of reimplementing new ones.

## Execution behavior

Proceed phase-by-phase using the template workflow:
1. inspect template docs and prompt phases
2. derive the repo structure from the template
3. generate the tool files
4. wire manifest/integration according to platform conventions
5. generate tests
6. generate or update OpenAPI snapshot artifacts required by the template
7. verify deterministic ordering and stable output assumptions

## Constraints

- do not invent architecture outside the template
- do not add speculative features
- do not add semantic retrieval
- do not add LLM usage
- do not modify unrelated TechVault services
- do not introduce new abstraction layers unless the template already defines them
- do not use nondeterministic defaults

## Deliverable expectation

Produce the full tool repository implementation for `document_catalog_query` in the standard standalone tool repo structure expected by the deterministic tool factory pipeline, ready to add under:

`backend/tools/document_catalog_query`

Mirror the template repository patterns exactly.