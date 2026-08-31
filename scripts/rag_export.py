"""Export the documentation RAG collection to a portable, versionable JSON file.

ChromaDB's on-disk format (SQLite + parquet blobs) is not diff-friendly and is
git-ignored. This script dumps the whole collection (ids, documents, embeddings,
metadatas) into a single JSON file useful for audit, backup, or moving between
machines. Embeddings are stored as lists of floats.

Usage:
    python docs/scripts/rag_export.py [--output PATH] [--chroma-dir PATH]
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import rag_config
from rag_docs import DOCS_COLLECTION, build_docs_spec, default_docs_dir


def _jsonable(value: Any) -> Any:
    """Recursively convert numpy arrays / non-JSON types to plain JSON values."""
    import numpy as np

    if isinstance(value, np.ndarray):
        return [_jsonable(v) for v in value.tolist()]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value

DEFAULT_OUT = default_docs_dir() / "rag" / "manifests" / "export.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", nargs="?", type=Path, default=default_docs_dir(),
                        help="Docs folder to export (default %(default)s)")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    spec = build_docs_spec(args.docs_dir)
    chroma_dir = spec.chroma_dir
    collection_name = spec.collection_name
    output = args.output or (spec.rag_dir / "manifests" / "export.json")

    import chromadb

    client = chromadb.PersistentClient(path=str(chroma_dir))
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        raise SystemExit(f"Collection '{collection_name}' not found. Run docs-rag-write first.")

    data = collection.get(include=["documents", "metadatas", "embeddings"])

    payload = {
        "collection": collection_name,
        "model": rag_config.EMBED_MODEL,
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(data["ids"]),
        "records": [
            {
                "id": data["ids"][i],
                "document": data["documents"][i],
                "metadata": data["metadatas"][i],
                "embedding": _jsonable(data["embeddings"][i]),
            }
            for i in range(len(data["ids"]))
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported {payload['count']} records -> {output}")


if __name__ == "__main__":
    main()
