"""Rebuild the documentation RAG from a JSON export (or from source docs).

Two modes:

1. **From export** (default): reads a ``rag_export.py`` JSON file and re-adds
   every record verbatim (embeddings are reused, no model is loaded). Useful for
   restoring a collection on a new machine without re-running the embedder.

2. **From source**: a thin wrapper around ``rag_write.py`` that re-embeds all
   markdown under ``docs/`` and rebuilds the manifest. Use this when you prefer
   reproducibility from the git-tracked sources (recommended for normal rebuilds).

Usage:
    python docs/scripts/rag_import.py --from-export path/to/export.json
    python docs/scripts/rag_import.py --from-source [--reset] [--docs-dir PATH]
"""

import argparse
import json
from pathlib import Path

from rag_docs import DOCS_COLLECTION, build_docs_spec, default_docs_dir


def import_from_export(export_path: Path, chroma_dir: Path, collection_name: str) -> None:
    import chromadb

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    records = payload["records"]
    collection_name = payload.get("collection", collection_name)

    client = chromadb.PersistentClient(path=str(chroma_dir.resolve()))
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )

    # Insert in batches to stay within Chroma's request limits.
    batch = 512
    for start in range(0, len(records), batch):
        chunk = records[start:start + batch]
        collection.add(
            ids=[r["id"] for r in chunk],
            documents=[r["document"] for r in chunk],
            embeddings=[r["embedding"] for r in chunk],
            metadatas=[r["metadata"] for r in chunk],
        )
    print(f"Imported {len(records)} records from {export_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", nargs="?", type=Path, default=default_docs_dir(),
                        help="Docs folder (default %(default)s)")
    parser.add_argument("--from-export", type=Path, default=None,
                        help="Path to export JSON (defaults to <docs>/rag/manifests/export.json)")
    parser.add_argument("--from-source", action="store_true",
                        help="Re-embed all markdown under the docs folder (calls docs-rag-write).")
    parser.add_argument("--reset", action="store_true",
                        help="With --from-source, rebuild the whole collection.")
    args = parser.parse_args()

    spec = build_docs_spec(args.docs_dir)
    chroma_dir = spec.chroma_dir
    collection_name = spec.collection_name

    if args.from_source:
        from rag_write import main as write_main
        import sys
        argv = ["rag_write.py", str(args.docs_dir)]
        if args.reset:
            argv.append("--reset")
        sys.argv = argv
        write_main()
        return

    export_path = args.from_export or (spec.rag_dir / "manifests" / "export.json")
    if not export_path.exists():
        raise SystemExit(f"Export not found: {export_path}. Run docs-rag-export first.")
    import_from_export(export_path, chroma_dir, collection_name)


if __name__ == "__main__":
    main()
