# I Stopped Using Generic Splitters on Code

Generic text splitters mangle code. I stopped using them.

Chunking code by character count splits functions in half and buries imports away from their usage. So I built a dependency-light splitter that respects code structure:

- Code-specific separators (defs, classes, imports)
- Source-suffix selection per language
- Skips node_modules, builds, and lockfiles

No tree-sitter, no native deps — just a splitter that understands what a "logical chunk" of code is.

It powers my code RAG, where agents retrieve exactly the function they need instead of a wall of tokens.

How do you index code for RAG?

**Hashtags:** #RAG #AI #SoftwareEngineering #LLM
