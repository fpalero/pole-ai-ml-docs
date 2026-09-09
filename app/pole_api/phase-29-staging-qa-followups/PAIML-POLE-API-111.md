# Ticket: PAIML-POLE-API-111

## Title
Analyst output-contract enforcement: progress routing + drills emission + tool hygiene

## Description
User-approved (2026-09-09) follow-up to the 007 gate evidence. Consolidates
the REMAINING analyst-path errors into one output-contract ticket — shared
enforcement across the formatter / `convert_supergraph_blocks` fallback
templates. Grounded in 007 gate run 5 evidence + `tools.py` on develop
`2c9e521`.

`pole_coach` stays langchain-free; all tool/prompt work lives on the
`app/pole_api` analyst path.

## Evidence (007 ticket gate runs)
Source: `packages/pole-coach/phase-5-integration-tests-e2e/PAIML-POLE-COACH-007.md`
(gate run 5) + `tools.py` on develop `2c9e521`.

- **Progress routing:** PR-02/03/04/05 bypass `get_progress_matrix` (108 tool)
  via `compare_sessions` / `progress_trend` / bare-md table instead; PR-01
  fires it but emits TWO `metric_matrix` cards (separate spec issue, see §4).
  Root cause: the new 108 tool requires `trick_label` (required) while the old
  tools `progress_trend` / `compare_sessions` only need `video_id` (zero
  inference) — the LLM picks the frictionless old tools; no prompt steering;
  overlapping descriptions.
- **Drills emission:** TP-04/05 emit md-only despite successful `query_*` RAG
  calls — no `drills` block, no explicit "data unavailable" block.
- **Tool hygiene:** `query_psicology` typo fires successfully on
  TP-04/05, IN-02/03/04/05 — cosmetic but load-bearing for RAG domain routing.

## What to Do (Implementation Steps)
- [ ] (1) **PROGRESS ROUTING — make `trick_label` OPTIONAL.**
  Change the `get_progress_matrix` tool schema so `trick_label` is optional;
  infer it server-side from the current video's stored `trick_label`
  (co-located with `video_id`, user-confirmed) when omitted.
- [ ] (2) **PROGRESS ROUTING — prompt steering + description.**
  Add a prompt routing line: progress/trend/comparison questions →
  `get_progress_matrix` first (old `progress_trend` / `compare_sessions` stay
  for narrow per-metric queries). Differentiate the `get_progress_matrix`
  description: "one-stop data-backed matrix; `trick_label` optional, inferred
  from current video when omitted".
- [ ] (3) **DRILLS EMISSION — block-contract minimums.** Training-plan turns
  must emit a `drills` block (from RAG-hit / registry candidates) or an
  explicit "data unavailable" block — never silent bare-md. Enforce in the
  formatter / `convert_supergraph_blocks` fallback templates (shared with #1
  as output-contract enforcement).
- [ ] (4) **TOOL HYGIENE — rename `query_psicology` → `query_psychology`.**
  Ride-along in the same files. Update tool name, description/registration,
  prompt references, and RAG domain routing. Keep a deprecated alias only if
  the harness still calls the old name (remove otherwise).
- [ ] (5) Re-run the affected test files green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) `get_progress_matrix` fires on ALL progress turns with no explicit
  `trick_label` (server-side inference from current video).
- [ ] (2) `training_plan` turns always emit `drills`-or-`unavailable` — never
  silent bare-md.
- [ ] (3) `query_psicology` typo fixed (no remaining references to the
  misspelled name outside a deliberate deprecated alias, if kept).

## Out of Scope (explicitly out — separate decisions pending)
- 107 fail-safes (terminal fallback frame + deterministic disclaimer —
  `PAIML-POLE-API-107.md`, separate ticket; reference, do not re-implement).
- 110 catalog stores (`trick_catalog` Mongo + catalog RAG — separate ticket;
  this ticket consumes its gates/drill candidates, does not build it).
- 006 decision / translation.
- FE work.
- `metric_matrix` tool-vocabulary hygiene (separate, undecided).
- Full-150 run.

## Spec-side notes (007-branch fixes, NOT app code — listed for completeness)
- PR-01 double `.matrix-card` strict-violation: spec asserts a single element;
  product renders Latest-vs-Previous + cohort → relax the spec with `.first()`.
- TP-01 "broken image" is a proven harness FALSE POSITIVE: server returns 200
  PNG; FE `loading="lazy"` image not yet loaded when the spec probes
  `naturalWidth` → scroll-into-view / await-load before probing.

## Integration Tests to Run (Local Verification)
- [ ] Routing test: progress/trend/comparison prompt with `video_id` only
  (no `trick_label`) invokes `get_progress_matrix` with the inferred label.
- [ ] Drills test: training-plan turn with RAG hits emits a `drills` block;
  no-hit case emits the explicit "data unavailable" block (never bare-md).
- [ ] Hygiene test: `query_psychology` resolves; old misspelling absent
  (or alias-only, if kept).
- [ ] 25-gate progress/training-plan suite green on the enforced contract.
- [ ] `pixi run test-api` (full task — must stay GREEN).

## Unit-Test Requirement
- [ ] Schema test: `trick_label` optional; omission infers the current video's
  stored label (asserted).
- [ ] Description/routing test: `get_progress_matrix` description carries the
  one-stop/optional-label text; progress/trend/comparison prompts route to it
  first.
- [ ] Formatter test: drills-or-unavailable block asserted for both RAG-hit
  and no-hit paths.
- [ ] Rename test: `query_psychology` registered and routed; misspelled name
  unregistered (or alias-only).

## Dependencies
- **Blocks**: 25 re-run green.
- **Blocked By**: 108 (merged), 110 (catalog, for gates/drill candidates).

## Estimated Effort
- [S]
