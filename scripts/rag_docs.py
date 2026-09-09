"""Shared helpers for the docs RAG specializations (docs-rag-*).

Both the CLI scripts (rag_write / rag_read / rag_generate / rag_export /
rag_import) derive a ``RagSpec`` for a given *docs folder*. The artifacts are
stored under ``<docs-folder>/rag/`` (chroma git-ignored, manifest versioned).
"""

from __future__ import annotations

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

import rag_config
from rag_engine import RagSpec

DOCS_COLLECTION = "pole_ai_docs"


def docs_splitter(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=rag_config.CHUNK_SIZE,
        chunk_overlap=rag_config.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
        keep_separator=True,
    )
    return splitter.split_text(text)


def iter_markdown(spec: RagSpec):
    for path in sorted(spec.source_dir.rglob("*")):
        if path.is_file() and path.suffix == ".md" and "rag" not in path.parts:
            yield path


def docs_project_for(rel_posix: str) -> str:
    """Infer the chunk ``project_name`` from a docs-relative path.

    ``app/<project>/…`` / ``package(s)/<project>/…`` → ``<project>`` (so
    ``--project pole_api`` / ``--project pole_analyst`` filters match);
    top-level groups (``diagrams``, ``scripts``) keep their own name;
    everything else → ``root``.
    """
    parts = rel_posix.split("/")
    if parts[0] in ("app", "package", "packages") and len(parts) > 1:
        return parts[1]
    if parts[0] in ("diagrams", "scripts"):
        return parts[0]
    return "root"


def build_docs_spec(docs_dir: Path) -> RagSpec:
    source = docs_dir.resolve()
    # The default docs folder is the repo "docs" dir -> keep a stable label.
    project_name = "docs" if source.name == "docs" else source.name
    return RagSpec(
        name=project_name,
        source_dir=source,
        rag_dir=source / "rag",
        collection_name=DOCS_COLLECTION,
        kind="docs",
        splitter=docs_splitter,
        iter_files=iter_markdown,
        project_for=docs_project_for,
    )


def default_docs_dir() -> Path:
    return rag_config.SCRIPTS_DIR.parent
