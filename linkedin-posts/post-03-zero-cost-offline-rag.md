# A RAG That Costs €0 — Forever

Most RAG systems bill you per query. Mine costs €0, forever.

I built an offline documentation RAG that never calls a paid API:
- Local embeddings (all-MiniLM-L6-v2)
- ChromaDB for persistence
- A sha256 manifest that re-embeds only what changed

The insight isn't the model — it's the indexing. A hash manifest tells you *what changed*, so you re-embed 3 files instead of 3,000.

Fully reproducible, versioned, and free. It's the knowledge base powering my AI Sport Agent project.

What's your default — local or hosted RAG?

**Hashtags:** #RAG #AI #LLM #AgenticAI
