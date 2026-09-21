# Replacing Marker/Surya with PyMuPDF: Know Your Corpus First

**Section:** Generative AI & RAG

## What it delivers
A lighter, cheaper RAG pipeline by inspecting the data *before* reaching for
heavy tools — dependency diets that start with the corpus, not the tooling.

## How it's built
A five-minute corpus scan showed every PDF already had embedded text, so
PyMuPDF swapped in for multi-GB Surya OCR weights and the heavy GPU lane died.

## Proof
- **Code:** [packages/pole_rag](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole_rag)
- **Live in the pole app:** the PDF ingestion path
