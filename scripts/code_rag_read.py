"""Code RAG — CLI query tool (``code-rag-read``).

Returns the most relevant source-code chunks under a project's ``rag/`` index
for a natural-language query.

Usage:
    python docs/scripts/code_rag_read.py <PROJECT> "how is the trick classified?"

Options:
    --k N          number of results (default 4)
    --path SUBSTR  filter by source path containing SUBSTR
    --json         emit raw JSON (for programmatic use / agents)
    --extract      print the full source text of the top result
    --score        show the similarity distance next to each result
"""

from __future__ import annotations

import argparse
from pathlib import Path

import rag_config
from rag_engine import RagSpec, read_query


def build_code_spec(project_dir: Path) -> RagSpec:
    return RagSpec(
        name=project_dir.name,
        source_dir=project_dir,
        rag_dir=project_dir / "rag",
        collection_name=f"{project_dir.name}_code",
        kind="code",
        splitter=lambda t: [t],  # read only needs paths, not a real splitter
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="App/package name or project path")
    parser.add_argument("query", help="Natural-language query")
    parser.add_argument("--k", type=int, default=4, help="Number of results (default 4)")
    parser.add_argument("--path", default=None, help="Filter source paths containing SUBSTR")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--extract", action="store_true",
                        help="Also print the full text of the top hit")
    parser.add_argument("--score", action="store_true", help="Show distance per result")
    args = parser.parse_args()

    project_dir, _ = rag_config.resolve_project(args.project)
    read_query(
        build_code_spec(project_dir),
        args.query,
        k=args.k,
        path_filter=args.path,
        as_json=args.json,
        extract=args.extract,
        score=args.score,
    )


if __name__ == "__main__":
    main()
