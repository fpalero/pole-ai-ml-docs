# Teaching RAG to Read Images

My RAG understood text perfectly — and was blind to figures. So I taught it to see.

Most RAG systems only index prose. Mine needed to answer questions about diagrams, anatomy, and technique images.

The fix: two collections, one store.
- Text chunks embedded with sentence-transformers
- Image descriptions (from a local VLM) embedded alongside them

Now a single query searches both — and retrieves "a picture of X" as naturally as "a paragraph about X."

This is the multimodal RAG behind AI Sport Agent's coaching knowledge base.

Are you indexing images in your RAG yet?

**Hashtags:** #RAG #MultimodalAI #AI #LLM
