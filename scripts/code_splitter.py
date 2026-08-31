"""Language-aware code splitting for the code RAG.

The upstream LangChain ``CodeSplitter`` requires the heavy native
``tree-sitter-languages`` dependency, which is not part of the pixi workspace.
To stay dependency-light and version-robust, we reproduce the *intent* of
``CodeSplitter`` — splitting code on language-relevant boundaries so related
symbols/functions stay together — using ``RecursiveCharacterTextSplitter`` with
code-specific separator lists per language and the shared default chunk params
(``chunk_size=1000``, ``chunk_overlap=100``).

Every language maps to a set of separators ordered from most to least
structure-preserving. Files without a known language map default to generic
separators.
"""

from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_config import CHUNK_OVERLAP, CHUNK_SIZE

# Separator lists, ordered from most structure-preserving to least. The splitter
# keeps the largest blocks <= chunk_size together, so function/class defs tend
# to remain intact within a chunk.
SEPARATORS = {
    "python": [
        "\nclass ", "\ndef ", "\tdef ", "\n\n", "\n", " ", "",
    ],
    "typescript": [
        "\nclass ", "\ninterface ", "\nfunction ", "\n  ", "\n    ",
        "\nexport ", "\nreturn ", "\n\n", "\n", " ", "",
    ],
    "javascript": [
        "\nclass ", "\nfunction ", "\n  ", "\n    ", "\nexport ", "\nconst ",
        "\nlet ", "\nvar ", "\n\n", "\n", " ", "",
    ],
    "html": ["<div", "<span", "<p", "<h", "<li", "<tr", "<td", "<section", "\n\n", "\n", " ", ""],
    "css": ["}", "\n\n", "\n", " ", ""],
    "json": ["\n", " ", ""],
    "markdown": ["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
}

# Map a file suffix to a separator list name.
SUFFIX_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".html": "html",
    ".css": "css",
    ".scss": "css",
    ".json": "json",
    ".md": "markdown",
}


def separators_for(path: str) -> list[str]:
    """Choose the separator list for a file (by suffix)."""
    from pathlib import Path

    return SEPARATORS.get(SUFFIX_MAP.get(Path(path).suffix, ""), SEPARATORS["python"])


def build_code_splitter(path: str):
    """Build a splitter instance appropriate for ``path``."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=separators_for(path),
        keep_separator=True,
    )


def split_text_for_path(text: str, path: str) -> list[str]:
    """Split ``text`` (from ``path``) into chunk strings using the default params."""
    return build_code_splitter(path).split_text(text)
