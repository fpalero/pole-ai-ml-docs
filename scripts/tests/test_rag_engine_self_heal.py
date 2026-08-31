"""Self-healing tests for :mod:`rag_engine.write_index`.

Verifies that the incremental writer detects and repairs a *manifest <=> ChromaDB
desync*: when a file's manifest entry has a matching ``file_hash`` (so it would
normally be skipped as "unchanged") but its chunks are missing from the Chroma
collection, the writer re-embeds that path instead of leaving it broken.

Uses a temp ``RagSpec`` + a fake embedder so the test is hermetic and fast (no
HuggingFace download, no network).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import logging

import pytest
from unittest.mock import patch

from rag_config import EMBEDDING_DIM
from rag_engine import RagSpec, write_index


def _make_spec(tmp: Path) -> RagSpec:
    """Build a tiny RagSpec over a temp source dir + temp rag dir."""
    src = tmp / "src"
    rag = tmp / "rag"
    src.mkdir(parents=True, exist_ok=True)
    (src / "a.md").write_text(
        "Alpha section one.\n\nAlpha section two.\n\nAlpha section three.",
        encoding="utf-8",
    )
    return RagSpec(
        name="testrag",
        source_dir=src,
        rag_dir=rag,
        collection_name="testrag",
        kind="docs",
        splitter=lambda text: [p for p in text.split("\n\n") if p.strip()],
    )


class _FakeEmbedder:
    """Returns fixed-size unit-ish vectors; count matches number of docs."""

    def __init__(self, *args, **kwargs):
        pass

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * EMBEDDING_DIM for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1] * EMBEDDING_DIM


@pytest.fixture
def spec():
    with tempfile.TemporaryDirectory() as td:
        yield _make_spec(Path(td))


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_unchanged_file_skipped_on_second_run(spec, caplog):
    caplog.set_level(logging.INFO)
    write_index(spec)                     # first: index
    caplog.clear()
    write_index(spec)                     # second: skip as unchanged
    assert "Summary: 0 new, 0 changed, 1 unchanged, 0 purged." in caplog.text
    assert "Self-heal" not in caplog.text  # healthy path: no re-embed


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_missing_chunks_are_re_embedded(spec, caplog):
    import chromadb
    caplog.set_level(logging.INFO)
    # index once so the manifest records the hash and the chunks exist
    write_index(spec)
    # simulate a desync: wipe the path's chunks from Chroma but KEEP the manifest
    client = chromadb.PersistentClient(path=str(spec.chroma_dir))
    collection = client.get_collection(spec.collection_name)
    before = collection.count()
    assert before == 3                     # 3 chunks for a.md
    collection.delete(where={"path": "a.md"})
    assert collection.count() == 0

    # next incremental run must self-heal (re-embed a.md) despite hash match
    caplog.clear()
    write_index(spec)
    assert "Self-heal a.md:" in caplog.text
    assert "Summary: 0 new, 1 changed, 0 unchanged, 0 purged." in caplog.text
    assert collection.count() == 3         # chunks restored
