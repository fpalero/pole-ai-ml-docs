"""Filter tests for :mod:`rag_engine.read_query`.

Verifies the client-side ``--path`` scoping that replaces the broken chromadb
1.5.9 ``$contains`` metadata filter (PAIML-DEVOPS-001):

* ``--path <prefix>`` returns chunks inside the prefix scope (component-boundary
  matching — no partial-name leakage), never 0 when matches exist;
* a full prefix (``packages/pole_ml``) is stricter than a bare component
  (``pole_ml``) and does not leak across sibling subtrees;
* ``--project`` keeps using the server-side exact ``$eq`` metadata match and
  combines correctly with the path filter;
* the requested ``k`` is respected after the client-side filter.

Uses a temp ``RagSpec`` + a fake embedder so the test is hermetic and fast (no
HuggingFace download, no network).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from unittest.mock import patch

from rag_config import EMBEDDING_DIM
from rag_engine import RagSpec, read_query, write_index


def _docs_project_for(rel_posix: str) -> str:
    """Mimic ``rag_docs.docs_project_for`` on the fixture tree."""
    parts = rel_posix.split("/")
    if parts[0] in ("app", "packages") and len(parts) > 1:
        return parts[1]
    return parts[0]


def _make_spec(tmp: Path) -> RagSpec:
    """Fixture tree mirroring the real docs layout (packages/, app/, diagrams/).

    ``pole_ml_other/`` exists on purpose: its name starts with the filter but it
    must NOT leak (component-boundary matching, no partial names).
    """
    src = tmp / "src"
    rag = tmp / "rag"
    files = {
        "packages/pole_ml/PLAN.md": "Pole ML plan one.\n\nPole ML plan two.",
        "packages/pole_ml/DOCUMENTATION.md": "Pole ML docs one.\n\nPole ML docs two.",
        "app/pole_api/API.md": "Pole API spec one.\n\nPole API spec two.",
        "diagrams/pole_ml/FLOW.md": "Pole ML flow one.\n\nPole ML flow two.",
        "packages/pole_tools/TOOLS.md": "Pole tools one.\n\nPole tools two.",
        "pole_ml_other/LEAK.md": "Nearby name one.\n\nNearby name two.",
        "ROOT.md": "Root level one.\n\nRoot level two.",
    }
    for rel, text in files.items():
        p = src / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return RagSpec(
        name="testrag",
        source_dir=src,
        rag_dir=rag,
        collection_name="testrag",
        kind="docs",
        splitter=lambda text: [c for c in text.split("\n\n") if c.strip()],
        project_for=_docs_project_for,
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


def _query_json(spec: RagSpec, query: str, capsys, **kwargs) -> list[dict]:
    """Run ``read_query`` in JSON mode and return the parsed hits."""
    read_query(spec, query, as_json=True, **kwargs)
    return json.loads(capsys.readouterr().out)


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_path_bare_component_scopes_to_all_matching_subtrees(spec, capsys):
    """`--path pole_ml` returns packages/pole_ml/* AND diagrams/pole_ml/* (not 0)."""
    write_index(spec)
    hits = _query_json(spec, "pole ml", capsys, k=10, path_filter="pole_ml")
    paths = {h["path"] for h in hits}
    assert paths == {
        "packages/pole_ml/PLAN.md",
        "packages/pole_ml/DOCUMENTATION.md",
        "diagrams/pole_ml/FLOW.md",
    }


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_path_bare_component_no_leakage(spec, capsys):
    """No hits outside the pole_ml scope; partial names never match."""
    write_index(spec)
    hits = _query_json(spec, "pole ml", capsys, k=10, path_filter="pole_ml")
    paths = {h["path"] for h in hits}
    assert "pole_ml_other/LEAK.md" not in paths
    assert "packages/pole_tools/TOOLS.md" not in paths
    assert "app/pole_api/API.md" not in paths
    assert "ROOT.md" not in paths


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_path_full_prefix_is_stricter_than_bare_component(spec, capsys):
    """`--path packages/pole_ml` does not leak into diagrams/pole_ml."""
    write_index(spec)
    hits = _query_json(spec, "pole ml", capsys, k=10, path_filter="packages/pole_ml")
    paths = {h["path"] for h in hits}
    assert paths == {
        "packages/pole_ml/PLAN.md",
        "packages/pole_ml/DOCUMENTATION.md",
    }


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_project_filter_still_exact(spec, capsys):
    """`--project` keeps the server-side exact $eq on project_name."""
    write_index(spec)
    hits = _query_json(spec, "pole ml", capsys, k=10, project_filter="pole_ml")
    paths = {h["path"] for h in hits}
    # diagram chunks carry project_name "diagrams", so they must NOT match.
    assert paths == {
        "packages/pole_ml/PLAN.md",
        "packages/pole_ml/DOCUMENTATION.md",
    }


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_path_and_project_combined_cross_scope_is_empty(spec, capsys):
    """Path + project filters compose: disjoint scopes return no hits."""
    write_index(spec)
    hits = _query_json(
        spec, "pole ml", capsys,
        k=10, path_filter="pole_ml", project_filter="pole_api",
    )
    assert hits == []


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_path_filter_respects_requested_k(spec, capsys):
    """Oversampling + client filter still truncate to the requested k."""
    write_index(spec)
    hits = _query_json(spec, "pole ml", capsys, k=2, path_filter="pole_ml")
    assert len(hits) == 2
    assert all("pole_ml" in h["path"].split("/") for h in hits)


@patch("langchain_huggingface.HuggingFaceEmbeddings", _FakeEmbedder)
def test_no_filter_returns_up_to_k_paths(spec, capsys):
    """Without filters the query returns at most k results (dedup, capped)."""
    write_index(spec)
    hits = _query_json(spec, "pole ml", capsys, k=4)
    assert len(hits) > 0
    assert len(hits) <= 4
    # one hit per source file (deduplicated by path)
    assert len({h["path"] for h in hits}) == len(hits)