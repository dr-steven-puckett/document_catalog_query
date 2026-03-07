# TOOL DOCUMENT CATALOG QUERY — ROADMAP (Non-Binding Future Ideas)

This file records potential future enhancements that are explicitly **out of scope**
for the current implementation. Nothing here is committed.

## Potential future work

- DB-backed production loader (SQLAlchemy session integration) once the platform
  provides a standard db-dependency injection pattern for read-only tool queries
- Cursor-based pagination for very large catalogs
- Tag filtering (joining `document_tags` table)
- Group-scoped access enforcement via `core/security.py`
- OpenAPI response examples
- Response hash (`response_hash_enabled = true`)

## Explicitly excluded forever

- Semantic search
- Vector similarity
- Chunk retrieval
- Summarization
- LLM calls
- Writes to database
