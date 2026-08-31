"""Code RAG — incremental writer (``code-rag-write``).

Scans the source tree of an app / package, splits source files with a
language-aware code splitter, embeds the chunks with a local HuggingFace
``sentence-transformers`` model and upserts them into ChromaDB
(under ``<project>/rag/``), keeping a content-hash manifest so only *changed*
files are re-embedded on subsequent runs.

Usage:
    python docs/scripts/code_rag_write.py <PROJECT> [--reset] [--dry-run]

``PROJECT`` is an app/package name (e.g. ``pole_api``) or a path to a project
folder. A ``rag/`` folder is created inside the project.

The pixi task is:
    pixi run code-rag-write <project>
"""

from __future__ import annotations

import argparse
from pathlib import Path

import rag_config
from code_splitter import split_text_for_path
from rag_engine import RagSpec, write_index

# Directories never indexed, regardless of language.
EXCLUDE_DIRNAMES = (
    "rag", "manifests", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "node_modules", ".git", ".venv", ".pixi", "dist", "build",
    ".angular", "coverage", ".idea", ".vscode", "venv", "models", "datasets",
    "logs",
)
# File suffixes included (source + light config). Everything else is skipped.
INCLUDE_SUFFIXES = (
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".html", ".css", ".scss", ".json", ".md", ".yaml", ".yml", ".toml",
)
# Individual lockfiles / noise to skip.
EXCLUDE_FILENAMES = (
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb",
    "poetry.lock", "uv.lock", "requirements.txt", "Cargo.lock",
)


def iter_code_files(spec: RagSpec):
    for path in sorted(spec.source_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(spec.source_dir)
        parts = rel.parts
        if any(part in EXCLUDE_DIRNAMES for part in parts):
            continue
        if path.name in EXCLUDE_FILENAMES:
            continue
        if path.suffix not in INCLUDE_SUFFIXES:
            continue
        if "rag" in parts:
            continue
        yield path


def build_code_spec(project_path: Path) -> RagSpec:
    """Build a code RagSpec whose splitter knows each file's path.

    The engine calls ``spec.splitter(text)`` without the path, so we record the
    current relative path on the spec via a wrapping iterator, and the splitter
    reads it back to pick the right language separators.
    """
    project_dir = project_path.resolve()
    state = {"path": ""}

    def _code_iter(s: RagSpec):
        for p in iter_code_files(s):
            state["path"] = str(p.relative_to(s.source_dir))
            yield p

    def _split(text: str) -> list[str]:
        return split_text_for_path(text, state["path"])

    spec = RagSpec(
        name=project_dir.name,
        source_dir=project_dir,
        rag_dir=project_dir / "rag",
        collection_name=f"{project_dir.name}_code",
        kind="code",
        splitter=_split,
        iter_files=_code_iter,
    )
    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="App/package name (e.g. pole_api) or project path")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_dir, _ = rag_config.resolve_project(args.project)
    write_index(build_code_spec(project_dir), reset=args.reset, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
