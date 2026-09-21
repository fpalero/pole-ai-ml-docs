# ChromaDB in Practice: k-NN Voting & the Config-Bug Case Study

**Section:** Machine Learning · **Featured:** ✅

## What it delivers
Vector search you can trust — plus the cautionary tale of silently losing data
to a config bug, so you don't repeat it.

## How it's built
128-d embeddings stored in ChromaDB with cosine search and k-NN voting, driven
by canonical config and idempotent indexing to avoid split-persist-dir bugs.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py](https://github.com/fpalero/pole-ai-ml/blob/develop/packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py)
- **Live in the pole app:** `movement_embeddings` (7,712 entries) in ChromaDB
