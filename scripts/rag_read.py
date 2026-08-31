"""Docs RAG — CLI query tool (``docs-rag-read``).

Returns the most relevant markdown chunks under a *docs folder* for a
natural-language query.

Usage:
    python docs/scripts/rag_read.py [DOCS_DIR] "how does the skeleton extractor work?"
    python docs/scripts/rag_read.py [DOCS_DIR] "trick classifier" --k 5 --json

Options: --k, --path, --project, --json, --extract, --score
"""

import argparse
from pathlib import Path

from rag_docs import build_docs_spec, default_docs_dir
from rag_engine import read_query


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", nargs="?", type=Path, default=default_docs_dir(),
                        help="Docs folder to query (default %(default)s)")
    parser.add_argument("query", help="Natural-language query")
    parser.add_argument("--k", type=int, default=4, help="Number of results (default 4)")
    parser.add_argument("--path", default=None, help="Filter source paths containing SUBSTR")
    parser.add_argument("--project", default=None, help="Filter by project_name metadata")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--extract", action="store_true",
                        help="Also print the full text of the top hit")
    parser.add_argument("--score", action="store_true", help="Show distance per result")
    args = parser.parse_args()

    read_query(
        build_docs_spec(args.docs_dir),
        args.query,
        k=args.k,
        path_filter=args.path,
        project_filter=args.project,
        as_json=args.json,
        extract=args.extract,
        score=args.score,
    )


if __name__ == "__main__":
    main()
