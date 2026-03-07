"""
Agent-mode stub for document_catalog_query.

Provides TOOL_SPEC and run() as required by the TechVault platform tool manifest
[agent_tool] contract.  These are placeholder implementations for future
agent-driven document catalog browsing integration.
"""
from __future__ import annotations

from typing import Any

TOOL_SPEC: dict[str, Any] = {
    "name": "document_catalog_query",
    "description": (
        "Deterministic read-only query tool for browsing and filtering TechVault's "
        "ingested document catalog metadata. Supports filtering by document_id, title, "
        "author, library_id, group_id, security_level, doc_type, language, status, and "
        "ingest date range with stable sorting and pagination."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["health", "query"],
                "description": "The catalog query action to perform.",
            },
            "args": {
                "type": "object",
                "description": "Action-specific arguments.",
                "properties": {
                    "document_id": {"type": "string"},
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "library_id": {"type": "string"},
                    "group_id": {"type": "string"},
                    "security_level": {
                        "type": "string",
                        "enum": ["public", "private", "protected", "secret"],
                    },
                    "doc_type": {
                        "type": "string",
                        "enum": [
                            "pdf", "epub", "txt", "md",
                            "csv", "docx", "code", "unknown",
                        ],
                    },
                    "language": {"type": "string"},
                    "status": {"type": "string"},
                    "ingest_date_from": {
                        "type": "string",
                        "description": "ISO date lower bound (YYYY-MM-DD), inclusive",
                    },
                    "ingest_date_to": {
                        "type": "string",
                        "description": "ISO date upper bound (YYYY-MM-DD), inclusive",
                    },
                    "sort_by": {"type": "string", "default": "document_id"},
                    "sort_dir": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "default": "asc",
                    },
                    "limit": {"type": "integer", "default": 25},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        },
        "required": ["action"],
    },
}


def run(ctx: Any, args: dict[str, Any]) -> dict[str, Any]:
    """Agent callable entry point (stub — full implementation pending).

    In agent mode the platform calls this with a ToolContext and parsed args dict.
    The stub raises NotImplementedError so callers know it is not yet wired up
    rather than silently returning empty data.
    """
    raise NotImplementedError(
        "document_catalog_query agent-mode run() is not yet implemented. "
        "Use the API or CLI interface instead."
    )
