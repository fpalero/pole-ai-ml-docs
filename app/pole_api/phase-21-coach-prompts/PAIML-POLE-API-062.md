# Ticket: PAIML-POLE-API-062

## Title
[Application] Coach prompt registry — templates + builder functions + JSON schemas

## Description
Phase 21 (§1, PLAN_PHASE_21.md Phase A). Create `analysis/services/coach_prompts.py`: three
task-specific prompt templates with strict JSON output contracts, builder functions that fill
each template from deterministic inputs, and JSON schema constants for validation.

Templates:
1. **SUMMARY_COACH_PROMPT** — "State of the Union" performance summary from training statistics.
2. **PLAN_COACH_PROMPT** — time-bound 4-week progression roadmap toward a target trick.
3. **POSE_COACH_PROMPT** — biomechanical breakdown of the pose at the annotated frame (text-only,
   no images — uses landmarks + biometric data + signal data).

Each prompt grounds every claim in supplied numbers (never invents metrics), mirrors user language
(ES/EN), and demands **strict JSON** matching the declared schema.

## What to Do (Implementation Steps)
- [ ] Create `analysis/services/coach_prompts.py` with three template constants.
- [ ] Builder function per template: `build_summary_prompt(data)`, `build_plan_prompt(data, target_trick, athlete_notes)`, `build_pose_prompt(data)`.
- [ ] Each builder accepts a typed `TypedDict`/dataclass input contract and returns a `PromptTemplate` (or plain string + schema dict).
- [ ] JSON schema constants: `SUMMARY_OUTPUT_SCHEMA`, `PLAN_OUTPUT_SCHEMA`, `POSE_OUTPUT_SCHEMA`.
- [ ] Unit tests: builders fill every field; templates forbid invented metrics; schemas documented.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Three templates exist with correct variable interpolation.
- [ ] Builder functions fill every field from typed inputs.
- [ ] JSON schemas declare all expected output fields.
- [ ] No template references metrics the system does not track.
- [ ] Coverage ≥ 80% for the new module.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: PAIML-POLE-API-063
- **Blocked By**: None

## Estimated Effort
- [S]
