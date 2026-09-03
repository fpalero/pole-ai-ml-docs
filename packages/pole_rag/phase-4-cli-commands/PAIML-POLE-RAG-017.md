# Ticket: PAIML-POLE-RAG-017

## Title
[Presentation] Implement `rag-seed` CLI (`cli/seed.py`)

## Description
Phase 4: first public CLI. `rag-seed -i <folder> -o <dir> --name <db>` validates input,
runs `seed_resource` (full rebuild) and prints per-PDF progress + final counts. Exit 0 on
success, 1 on total failure.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `main(argv=None)` in `packages/pole_rag/src/pole_rag/cli/seed.py` with
      argparse: `-i/--input` (required), `-o/--output` (default `config.default_data_dir()`),
      `--name` (required).
- [ ] Step 2: Validate input dir exists and is a directory; error message + exit 1 otherwise.
- [ ] Step 3: Call `seed_resource(...)`; print progress lines and final counts.
- [ ] Step 4: Catch unexpected exceptions → clean error + exit 1.
- [ ] Step 5: Add `if __name__ == "__main__": main()`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `rag-seed -i missing` fails with actionable error and exit 1.
- [ ] Unit tests are written and passing for this specific component (arg parsing,
      mocked seed).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01: seed `sources/psicology` → `data/` → both collections populated.
- [ ] Run UC-04: corrupt PDF + valid PDF → warning + success exit.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-021
- **Blocked By**: PAIML-POLE-RAG-015

## Estimated Effort
- [M]