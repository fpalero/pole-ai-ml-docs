# One LSTM, Two Outputs: Classifications AND Embeddings

One LSTM forward pass gives me two things: a class prediction AND a 128-dim embedding.

Most people train one model to classify and a second to embed. I trained one to do both.

The trick is the architecture: a sequence-to-vector LSTM whose bottleneck layer IS the embedding. Classification logits branch off one head; the 128-dim bottleneck feeds similarity search.

Why it matters:
- One model to maintain, not two
- Classification and retrieval share the same learned representation
- Embeddings stay aligned with what the classifier actually sees

This is the backbone of my AI Sport Agent's movement-recognition pipeline — the same pass that says "this is a shoulder mount" also makes it searchable.

Do you train separate models for classification and embeddings?

**Hashtags:** #MachineLearning #DeepLearning #LSTM #AI
