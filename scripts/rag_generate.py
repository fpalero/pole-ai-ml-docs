"""Docs RAG — regenerate from scratch (``docs-rag-generate``).

Deletes the existing docs RAG (ChromaDB store + manifest) under a *docs folder*
then re-reads every markdown file and re-embeds it.

Usage:
    python docs/scripts/rag_generate.py [DOCS_DIR]

The pixi task is:
    pixi run docs-rag-generate [<docs-dir>]
"""

import argparse
from pathlib import Path

from rag_docs import build_docs_spec, default_docs_dir
from rag_engine import generate_index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", nargs="?", type=Path, default=default_docs_dir(),
                        help="Docs folder to regenerate (default %(default)s)")
    args = parser.parse_args()

    generate_index(build_docs_spec(args.docs_dir))


if __name__ == "__main__":
    main()
