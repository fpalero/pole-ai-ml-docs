# Ticket: PAIML-POLE-RAG-010

## Title
[Application] Implement atomic table-preserving chunker (`chunker.py`)

## Description
Phase 2: `chunk_markdown_with_atomic_tables(markdown_text) -> list[str]` from the user's
reference design. Regex isolates complete Markdown `|...|` table blocks so they are never
split across vector chunks; up to 3 preceding lines are injected as context
(`--- CONTEXTO DE LA TABLA ---`); remaining text is split with
`RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)`.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `chunk_markdown_with_atomic_tables` in
      `packages/pole_rag/src/pole_rag/chunker.py` with
      `table_pattern = re.compile(r'((?:\|[^\n]*\|(?:\n|$))+)', re.MULTILINE)`.
- [ ] Step 2: Use `table_pattern.split(markdown_text)`; odd indexes are tables → keep
      atomic with context prefix (last ≤3 lines of previous chunk); even indexes →
      `text_splitter.split_text`.
- [ ] Step 3: Skip empty parts; strip each chunk.
- [ ] Step 4: Handle empty input → `[]`; text without tables → normal splitting.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] Table blocks remain a single chunk (never truncated mid-row).
- [ ] Context prefix injected before each table when previous text exists.
- [ ] Unit tests are written and passing for this specific component.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01 seed path: chunker output feeds `text_chunks` collection.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-011, PAIML-POLE-RAG-015
- **Blocked By**: PAIML-POLE-RAG-002, PAIML-POLE-RAG-005

## Estimated Effort
- [M]