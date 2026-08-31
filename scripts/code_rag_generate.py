"""Code RAG — regenerate from scratch (``code-rag-generate``).

Deletes the existing project code RAG (ChromaDB store + manifest) under the
project's ``rag/`` folder, then re-reads and re-embeds every source file.

Usage:
    python docs/scripts/code_rag_generate.py <PROJECT>

The pixi task is:
    pixi run code-rag-generate <project>
"""

from __future__ import annotations

import argparse
from pathlib import Path

import rag_config
from rag_engine import RagSpec, generate_index


def build_code_spec(project_dir: Path) -> RagSpec:
    return RagSpec(
        name=project_dir.name,
        source_dir=project_dir,
        rag_dir=project_dir / "rag",
        collection_name=f"{project_dir.name}_code",
        kind="code",
        splitter=lambda t: [t],  # generate delegates to write which uses real splitter
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="App/package name or project path")
    args = parser.parse_args()

    project_dir, _ = rag_config.resolve_project(args.project)
    generate_index(build_code_spec(project_dir))


if __name__ == "__main__":
    main()
