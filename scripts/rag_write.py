"""Docs RAG — incremental writer (``docs-rag-write``).

Scans every ``.md`` file under a *docs folder*, chunks + embeds it with a local
HuggingFace ``sentence-transformers`` model and upserts into ChromaDB
(under ``<docs-folder>/rag/``), keeping a content-hash manifest so only *changed*
files are re-embedded on subsequent runs.

Usage:
    python docs/scripts/rag_write.py [DOCS_DIR] [--reset] [--dry-run]

The pixi task is:
    pixi run docs-rag-write [<docs-dir>]
"""

import argparse
from pathlib import Path

from rag_docs import build_docs_spec, default_docs_dir
from rag_engine import write_index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", nargs="?", type=Path, default=default_docs_dir(),
                        help="Docs folder to index (default %(default)s)")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_index(build_docs_spec(args.docs_dir), reset=args.reset, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
