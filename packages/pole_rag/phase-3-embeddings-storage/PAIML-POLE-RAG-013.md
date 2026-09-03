# Ticket: PAIML-POLE-RAG-013

## Title
[Infrastructure] Implement Ollama vision captions (`vision.py`)

## Description
Phase 3: `OllamaVision.describe(image_path) -> str` uses local Ollama with
`llama3.2-vision` (configurable `OLLAMA_MODEL`/`OLLAMA_HOST`) to generate image
descriptions for the `image_descriptions` collection. Per-image error isolation with a
fallback caption.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `OllamaVision` in `packages/pole_rag/src/pole_rag/vision.py` using
      `langchain_ollama.ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_HOST)`.
- [ ] Step 2: `describe(image_path) -> str`: open image via Pillow, send a caption prompt
      ("A detailed chart, diagram or image showing"), return decoded text.
- [ ] Step 3: Wrap in `try/except`; on failure return a stable fallback string (e.g.,
      `"Image could not be described"`) and log a warning.
- [ ] Step 4: Expose `describe_many(image_paths) -> list[str]`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `describe` returns a non-empty string for a valid image (live check optional).
- [ ] Failed images yield the fallback caption, not an exception.
- [ ] Unit tests are written and passing for this specific component (mock ChatOllama).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01: image captions populate `image_descriptions` during live seed.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-015
- **Blocked By**: PAIML-POLE-RAG-001, PAIML-POLE-RAG-005

## Estimated Effort
- [M]