"""Shared configuration for the Pole AI RAG tooling.

There are two flavors of RAG, both built on the same generic engine in
``rag_engine.py``:

* **Docs RAG** — indexes markdown under a *docs folder* (default ``docs/``).
* **Code RAG** — indexes the source tree of an app / package.

In both cases the vector artifacts are stored under ``<source>/rag/``:
``<source>/rag/chroma/`` (git-ignored binary store) and
``<source>/rag/manifests/manifest.json`` (versioned incremental snapshot).

All paths are resolved relative to this file so the scripts work regardless of
the current working directory.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — resolved from this file's directory so CWD does not matter.
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent.parent               # monorepo root
APPS_DIR = REPO_ROOT / "app"
PACKAGES_DIR = REPO_ROOT / "packages"

# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# ---------------------------------------------------------------------------
# Chunking (shared default for docs + code)
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# ---------------------------------------------------------------------------
# Metadata keys stored on every chunk.
# ---------------------------------------------------------------------------
METADATA_KEYS = {
    "path": "relative path of the source file",
    "file_name": "basename of the source file",
    "project_name": "project inferred from the path",
    "created_date": "ISO date the source file was first indexed",
    "last_update": "ISO datetime of the source file's last modification",
    "file_hash": "sha256 of the source file content at last index",
}

# ChromaDB reserved metadata keys must not be used by us.
RESERVED_META = {"chroma:document", "chroma:collection"}

# ---------------------------------------------------------------------------
# Project registry — the known apps and packages that can host a code RAG.
# ---------------------------------------------------------------------------
APPS = ("pole_analyst", "pole_api", "pole_fe")
PACKAGES = (
    "analysis-tools",
    "chatbot",
    "jobs",
    "pole-crawler",
    "pole-crop",
    "pole-tools",
    "pole-train-model",
)


def resolve_project(name_or_path: str) -> tuple[Path, str]:
    """Resolve a project name (or path) to ``(project_dir, project_name)``.

    Accepts either a bare name (``pole_api``) resolved against ``app/`` and
    ``packages/``, or an explicit relative/absolute path to a project folder.
    """
    p = Path(name_or_path)
    candidate = p if p.is_absolute() else Path.cwd() / p

    if candidate.exists():
        project_dir = candidate.resolve()
        return project_dir, project_dir.name

    for base in (APPS_DIR, PACKAGES_DIR):
        cand = (base / name_or_path).resolve()
        if cand.is_dir():
            return cand, cand.name

    known = ", ".join(sorted(APPS + PACKAGES))
    raise SystemExit(
        f"Unknown project '{name_or_path}'. Known apps/packages: {known} "
        f"(or pass a path to a project folder)."
    )
