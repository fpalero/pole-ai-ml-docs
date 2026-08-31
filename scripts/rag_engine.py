"""Generic, reusable RAG core shared by the docs-rag and code-rag specializations.

This module centralises the write / read / generate logic so the two flavors
(plain-text markdown and language-aware source code) only need to provide a
small ``RagSpec`` describing their content:

* where the source lives,
* where the ``rag/`` artifacts live,
* the collection name,
* how to split a file into chunks,
* which files to include / exclude.

Deterministic chunk ids (``sha1(rel_path)::chunk-<i>``) make upserts idempotent,
and a content-hash manifest (``<rag>/manifests/manifest.json``) is kept so only
*changed* files are re-embedded on subsequent runs. Unchanged files are skipped,
changed files are re-chunked + re-embedded, and deleted files are purged.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Iterator

from rag_config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_MODEL,
    EMBEDDING_DIM,
    SCRIPTS_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger("rag_engine")

# ---------------------------------------------------------------------------
# RagSpec
# ---------------------------------------------------------------------------


@dataclass
class RagSpec:
    """Everything the generic engine needs to index one RAG."""

    name: str                                # friendly label, e.g. "docs" | "pole_api"
    source_dir: Path                         # root of the content to index
    rag_dir: Path                            # where rag/ artifacts live
    collection_name: str
    kind: str                                # "docs" | "code"
    splitter: Callable[[str], list[str]]     # text -> list of chunk strings
    iter_files: Callable[["RagSpec"], Iterator[Path]] = field(default=None)  # noqa: F821
    # directories / file extensions to skip (code RAG)
    exclude_dirnames: tuple[str, ...] = ()
    include_suffixes: tuple[str, ...] = ()
    exclude_filenames: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.iter_files is None:
            self.iter_files = default_iter_files

    @property
    def chroma_dir(self) -> Path:
        return self.rag_dir / "chroma"

    @property
    def manifests_dir(self) -> Path:
        return self.rag_dir / "manifests"

    @property
    def manifest_path(self) -> Path:
        return self.manifests_dir / "manifest.json"


# ---------------------------------------------------------------------------
# Generic file iteration
# ---------------------------------------------------------------------------


def default_iter_files(spec: RagSpec) -> Iterator[Path]:
    """Yield source files from ``source_dir`` honouring exclusions / suffixes."""
    for path in sorted(spec.source_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(spec.source_dir)
        if any(part in spec.exclude_dirnames for part in rel.parts):
            continue
        if path.name in spec.exclude_filenames:
            continue
        if spec.include_suffixes and path.suffix not in spec.include_suffixes:
            continue
        if "rag" in rel.parts:  # never index the RAG's own artifacts
            continue
        yield path


# ---------------------------------------------------------------------------
# Manifest + hashing helpers
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(spec: RagSpec) -> dict:
    if spec.manifest_path.exists():
        return json.loads(spec.manifest_path.read_text(encoding="utf-8"))
    return {}


def save_manifest(spec: RagSpec, manifest: dict) -> None:
    spec.manifests_dir.mkdir(parents=True, exist_ok=True)
    spec.manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )


def make_collection(client, name: str):
    return client.get_or_create_collection(
        name=name, metadata={"hnsw:space": "cosine"}
    )


# ---------------------------------------------------------------------------
# Write (incremental, idempotent)
# ---------------------------------------------------------------------------


def write_index(
    spec: RagSpec,
    reset: bool = False,
    dry_run: bool = False,
) -> None:
    """Scan ``spec.source_dir``, chunk + embed changed files into ChromaDB."""
    import chromadb
    from langchain_huggingface import HuggingFaceEmbeddings

    spec.chroma_dir.mkdir(parents=True, exist_ok=True)
    spec.manifests_dir.mkdir(parents=True, exist_ok=True)

    manifest = {} if reset else load_manifest(spec)
    embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=str(spec.chroma_dir))
    collection = make_collection(client, spec.collection_name)

    if reset:
        logger.info("Resetting collection %s", spec.collection_name)
        try:
            client.delete_collection(spec.collection_name)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Delete collection raised: %s", exc)
        collection = make_collection(client, spec.collection_name)

    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    seen_paths: set[str] = set()
    changed = unchanged = new_files = 0

    for file_path in spec.iter_files(spec):
        rel = file_path.relative_to(spec.source_dir)
        rel_str = rel.as_posix()
        seen_paths.add(rel_str)

        digest = sha256_file(file_path)
        prev = manifest.get(rel_str)
        if prev and prev.get("file_hash") == digest:
            # Self-heal: a hash match normally means "already indexed", but the
            # Chroma collection may be missing this path's chunks (e.g. an
            # interrupted rebuild or a manifest <=> ChromaDB desync). Verify the
            # actual chunk count matches the expected one and re-embed if not.
            text = file_path.read_text(encoding="utf-8", errors="replace")
            expected = len(spec.splitter(text))
            got = collection.get(where={"path": rel_str}, include=[])
            actual = len(got["ids"]) if got and got["ids"] else 0
            if actual == expected:
                unchanged += 1
                continue
            logger.warning(
                "Self-heal %s: manifest says indexed but Chroma has %d/%d "
                "chunks; re-embedding", rel_str, actual, expected,
            )
        else:
            text = file_path.read_text(encoding="utf-8", errors="replace")

        created = prev.get("created_date", now_iso) if prev else now_iso
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc)
        last_update = mtime.isoformat(timespec="seconds")

        chunks = spec.splitter(text)
        prefix = hashlib.sha1(rel_str.encode("utf-8")).hexdigest()
        ids = [f"{prefix}::chunk-{i}" for i in range(len(chunks))]
        metadatas = [{
            "path": rel_str,
            "file_name": file_path.name,
            "project_name": spec.name,
            "created_date": created,
            "last_update": last_update,
            "file_hash": digest,
        } for _ in chunks]

        if dry_run:
            logger.info("[dry-run] would (re)index %s (%d chunks)", rel_str, len(chunks))
            new_files += 1
            manifest[rel_str] = {
                "file_hash": digest, "created_date": created, "last_update": last_update,
            }
            continue

        collection.delete(where={"path": rel_str})
        if chunks:
            collection.add(
                ids=ids,
                embeddings=embedder.embed_documents(chunks),
                metadatas=metadatas,
                documents=chunks,
            )
        changed += 1 if prev else 0
        new_files += 0 if prev else 1
        manifest[rel_str] = {
            "file_hash": digest, "created_date": created, "last_update": last_update,
        }
        logger.info("Indexed %s (%d chunks)", rel_str, len(chunks))

    purged = 0
    for rel_str in list(manifest.keys()):
        if rel_str not in seen_paths:
            purged += 1
            if not dry_run:
                collection.delete(where={"path": rel_str})
            del manifest[rel_str]
            logger.info("Purged missing file %s", rel_str)

    if not dry_run:
        save_manifest(spec, manifest)
        logger.info("Collection %s now has %d chunks.", spec.collection_name, collection.count())
    else:
        logger.info("[dry-run] no changes written.")

    logger.info(
        "Summary: %d new, %d changed, %d unchanged, %d purged.",
        new_files, changed, unchanged, purged,
    )


# ---------------------------------------------------------------------------
# Read (query)
# ---------------------------------------------------------------------------


def read_query(
    spec: RagSpec,
    query: str,
    k: int = 4,
    path_filter: str | None = None,
    project_filter: str | None = None,
    as_json: bool = False,
    extract: bool = False,
    score: bool = False,
) -> None:
    """Query ``spec`` and print the best-matching chunks."""
    import chromadb
    from langchain_huggingface import HuggingFaceEmbeddings

    embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=str(spec.chroma_dir))

    try:
        collection = client.get_collection(name=spec.collection_name)
    except Exception:
        raise SystemExit(
            f"Collection '{spec.collection_name}' not found under {spec.chroma_dir}. "
            f"Run the corresponding write/generate command first."
        )

    where: dict | None = None
    if path_filter or project_filter:
        conds = []
        if path_filter:
            conds.append({"path": {"$contains": path_filter}})
        if project_filter:
            conds.append({"project_name": {"$eq": project_filter}})
        where = conds[0] if len(conds) == 1 else {"$and": conds}

    query_embedding = embedder.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where or None,
        include=["metadatas", "documents", "distances"],
    )

    hits = []
    for i, doc_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i] or {}
        hits.append({
            "id": doc_id,
            "path": meta.get("path", ""),
            "project": meta.get("project_name", ""),
            "created_date": meta.get("created_date", ""),
            "last_update": meta.get("last_update", ""),
            "distance": round(results["distances"][0][i], 4),
            "text": (results["documents"][0][i] or "")[:2000],
        })

    # Deduplicate by path, keeping the best (lowest distance) hit per source file
    # while preserving the order of each path's first occurrence.
    best_by_path: dict[str, dict] = {}
    order: list[str] = []
    for h in hits:
        if h["path"] not in best_by_path:
            best_by_path[h["path"]] = h
            order.append(h["path"])
        elif h["distance"] < best_by_path[h["path"]]["distance"]:
            best_by_path[h["path"]] = h
    hits = [best_by_path[p] for p in order]

    if as_json:
        import json as _json
        print(_json.dumps(hits, indent=2, ensure_ascii=False))
        return

    if not hits:
        print("No results.")
        return

    for idx, h in enumerate(hits, 1):
        header = f"[{idx}] {h['path']} (project={h['project']})"
        if score:
            header += f" distance={h['distance']}"
        print(header)
        print("-" * len(header))
        print(h["text"])
        print()

    if extract and hits:
        src = spec.source_dir / hits[0]["path"]
        if src.exists():
            print(f"===== FULL SOURCE: {src} =====")
            print(src.read_text(encoding="utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# Generate (wipe + rebuild)
# ---------------------------------------------------------------------------


def generate_index(spec: RagSpec) -> None:
    """Wipe the existing artifacts for ``spec`` then rebuild from scratch."""
    if spec.chroma_dir.exists():
        shutil.rmtree(spec.chroma_dir)
        logger.info("Deleted %s", spec.chroma_dir)
    for f in (spec.manifest_path, spec.manifests_dir / "export.json"):
        if f.exists():
            f.unlink()
    write_index(spec, reset=True)
