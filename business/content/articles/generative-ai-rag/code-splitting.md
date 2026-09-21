# Language-Aware Code Splitting Without tree-sitter

**Section:** Generative AI & RAG

## What it delivers
A code-aware RAG that doesn't mangle your source — chunking that respects code
structure without shipping native dependencies.

## How it's built
A dependency-light splitter using code-specific separators and source-suffix
selection that skips node_modules, builds, and lockfiles — the tree-sitter-free
alternative for teams that can't ship native deps.

## Proof
- **Code:** [packages/pole_rag](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole_rag)
- **Live in the pole app:** the per-project code RAG indexer
