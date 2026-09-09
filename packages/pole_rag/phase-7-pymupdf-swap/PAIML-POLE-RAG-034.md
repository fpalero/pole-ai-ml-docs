# PAIML-POLE-RAG-034 — tqdm progress on the caption loop

## Context
`rag-seed` with captions spends hours inside `OllamaVision.describe_many`
(one blocking `llava` call per image). The loop is silent — the outer
`seeding` bar only ticks per-PDF — so long runs look stuck (observed
during the 4-resource captioned seed, Phase 7).

## Scope (pole-ai-ml repo only)
1. `packages/pole_rag/src/pole_rag/vision.py` — wrap the `describe_many`
   loop with `tqdm(paths, desc="captioning", unit="img")` (`tqdm` is
   already a dependency via the seeder). Per-image failure isolation
   unchanged (fallback caption, never abort).
2. Existing vision/seeder/CLI suites must stay green (`pixi run test-rag`).

## Out of scope
- Changing caption model, prompt, or fallback behavior.
- Touching `docs/` (pole-ai-ml-docs) or infra repos.

## Acceptance
- [ ] `rag-seed` (without `--skip-images`) shows a live `captioning: N/M img`
      bar with per-image rate + ETA.
- [ ] `pixi run test-rag` green (151 passed baseline, 3 integration deselected).
- [ ] PR against `develop` + `/oc review`, no blocking findings.

## Blocks / Blocked By
- Blocks: —
- Blocked By: — (ships independently; running seeds keep old in-memory code)
