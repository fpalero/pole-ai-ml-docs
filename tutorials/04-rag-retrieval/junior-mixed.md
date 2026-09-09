# Theme 04 — RAG & Retrieval · Audience: Mixed Beginner → Intermediate

> The friendliest path into RAG: why you'd want it, a walkthrough without an
> API bill, and the mental model for chunking.

## Catalog

### D1 (intro) — Your First RAG, For Free, On Your Own Docs
- **Difficulty:** Beginner
- **Type:** Tutorial
- **Hook:** "Chat with your docs this afternoon — no OpenAI key needed."
- **Description:** Built from the ground up: pick markdown files, embed with a
  local MiniLM model, store in ChromaDB, query it back. The reader ends with a
  working docs search and knows each moving part.
- **Grounding:** `docs/scripts/README.md`, `docs/packages/pole_rag/PLAN.md`.
- **Sellable angle:** Evergreen beginner funnel for the RAG topic.

### D2 (intro) — Why Chunking Breaks Code (and a Fix That's Free)
- **Difficulty:** Intermediate
- **Type:** Explainer + demo
- **Hook:** "Ask five coders where a 'chunk' begins and you get five answers — the splitter decides."
- **Description:** Why generic splitters cut mid-function and how
  code-specific separators fix retrieval quality, with a dependency-light
  implementation a beginner can follow.
- **Grounding:** `docs/scripts/rag_code.md`.
- **Sellable angle:** Niche but sticky — chunking is a constant RAG topic.