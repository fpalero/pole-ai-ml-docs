# Neural Nets Are Overconfident. My Fix: A Vector Database.

My classifier said 91% confident — and was wrong. A vector search caught it.

Deep learning models are confidently wrong on low-confidence inputs. So I stopped trusting a single number.

My hybrid classifier:
1. LSTM classifies first
2. If confidence < 0.7, a ChromaDB k-NN search takes over
3. The nearest neighbours vote

The result: low-confidence and *unseen* classes get rescued by retrieval instead of misclassified.

It's the pattern behind AI Sport Agent's movement recognition — a neural net for the easy cases, a vector database for the hard ones.

How do you handle low-confidence predictions?

**Hashtags:** #MachineLearning #RAG #AI #VectorSearch
