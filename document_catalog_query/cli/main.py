"""document_catalog_query.cli.main — argparse CLI for the document_catalog_query tool.

Canonical invocation: python -m document_catalog_query.cli.main <command> [options]

Commands
--------
health  [--catalog-file <path>]
query   [--catalog-file <path>] [filter options] [sort/pagination options]

stdout: JSON only (canonical: sort_keys, compact, one trailing newline)
stderr: error messages only, no tracebacks
exit 0 on success, exit 1 on error
"""
from __future__ import annotations

import argparse
import json
import sys


def _emit(obj: dict) -> None:
    """Write canonical JSON to stdout."""
    sys.stdout.write(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    )


def _die(message: str) -> None:
    """Write error message to stderr and exit 1."""
    sys.stderr.write(f"error: {message}\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def _cmd_health(_args: argparse.Namespace) -> None:
    from document_catalog_query.core import service  # noqa: PLC0415

    try:
        result = service.health()
    except (ValueError, PermissionError) as exc:
        _die(str(exc))
        return
    _emit(result)


def _cmd_query(args: argparse.Namespace) -> None:
    from document_catalog_query.core import service  # noqa: PLC0415
    from document_catalog_query.core.catalog_loader import load_catalog  # noqa: PLC0415

    try:
        if args.catalog_file:
            records = load_catalog(args.catalog_file)
        else:
            records = []

        result = service.query_documents(
            records,
            document_id=args.document_id or None,
            title=args.title or None,
            author=args.author or None,
            library_id=args.library_id or None,
            group_id=args.group_id or None,
            security_level=args.security_level or None,
            doc_type=args.doc_type or None,
            language=args.language or None,
            status=args.status or None,
            ingest_date_from=args.ingest_date_from or None,
            ingest_date_to=args.ingest_date_to or None,
            sort_by=args.sort_by,
            sort_dir=args.sort_dir,
            limit=args.limit,
            offset=args.offset,
        )
    except (ValueError, PermissionError) as exc:
        _die(str(exc))
        return
    _emit(result)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m document_catalog_query.cli.main",
        description="document_catalog_query tool CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── health ──────────────────────────────────────────────────────────────
    health_p = subparsers.add_parser("health", help="Return tool health status")
    health_p.add_argument(
        "--catalog-file",
        dest="catalog_file",
        default="",
        metavar="PATH",
        help="(accepted for contract compliance; not used by health)",
    )

    # ── query ────────────────────────────────────────────────────────────────
    query_p = subparsers.add_parser(
        "query",
        help="Filter and paginate document catalog metadata",
    )
    query_p.add_argument(
        "--catalog-file",
        dest="catalog_file",
        default="",
        metavar="PATH",
        help="Relative path to catalog JSON file (standalone mode)",
    )

    # Filters
    query_p.add_argument("--document-id", dest="document_id", default="", metavar="ID")
    query_p.add_argument("--title", dest="title", default="", metavar="SUBSTR")
    query_p.add_argument("--author", dest="author", default="", metavar="SUBSTR")
    query_p.add_argument("--library-id", dest="library_id", default="", metavar="ID")
    query_p.add_argument("--group-id", dest="group_id", default="", metavar="ID")
    query_p.add_argument(
        "--security-level",
        dest="security_level",
        default="",
        metavar="LEVEL",
        help="public | private | protected | secret",
    )
    query_p.add_argument(
        "--doc-type",
        dest="doc_type",
        default="",
        metavar="TYPE",
        help="pdf | epub | txt | md | csv | docx | code | unknown",
    )
    query_p.add_argument("--language", dest="language", default="", metavar="LANG")
    query_p.add_argument(
        "--status",
        dest="status",
        default="",
        metavar="STATUS",
        help="active | archived | etc.",
    )
    query_p.add_argument(
        "--ingest-date-from",
        dest="ingest_date_from",
        default="",
        metavar="YYYY-MM-DD",
        help="Lower bound for ingested_at (inclusive)",
    )
    query_p.add_argument(
        "--ingest-date-to",
        dest="ingest_date_to",
        default="",
        metavar="YYYY-MM-DD",
        help="Upper bound for ingested_at (inclusive)",
    )

    # Sort / pagination
    query_p.add_argument(
        "--sort-by",
        dest="sort_by",
        default="document_id",
        metavar="FIELD",
        help=(
            "document_id | title | author | library_id | group_id | "
            "security_level | doc_type | language | status | ingest_date"
        ),
    )
    query_p.add_argument(
        "--sort-dir",
        dest="sort_dir",
        default="asc",
        choices=["asc", "desc"],
    )
    query_p.add_argument(
        "--limit",
        dest="limit",
        type=int,
        default=25,
        metavar="N",
        help="Maximum results (1–500, default 25)",
    )
    query_p.add_argument(
        "--offset",
        dest="offset",
        type=int,
        default=0,
        metavar="N",
        help="Pagination offset (default 0)",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "health": _cmd_health,
        "query": _cmd_query,
    }
    handler = dispatch.get(args.command)
    if handler is None:  # pragma: no cover
        _die(f"Unknown command: {args.command!r}")
    else:
        handler(args)


if __name__ == "__main__":
    main()
