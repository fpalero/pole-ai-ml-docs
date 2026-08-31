# Ticket: PAIML-CREW-004

## Title
Phase-end guardrails

## Description
Apply the same guardrails from `guardrails.py` to the `crew/crew_phase_end.py` workflow, ensuring consistency across both CrewAI flows.

## What to Do
- Read `crew/crew_phase_end.py` to understand its agent/task structure
- Import `apply_guardrails` from `crew.guardrails`
- Apply `apply_guardrails()` to every agent created in `crew_phase_end.py`
- If `crew_phase_end.py` creates tasks with descriptions that should be validated, add appropriate `guardrail=` parameters
- Ensure the phase-end agents also respect `CREW_MAX_ITER` and `CREW_MAX_RPM`
- Test that the phase-end flow still works correctly with guardrails applied

## Acceptance Criteria
- [ ] All agents in `crew_phase_end.py` have guardrails applied
- [ ] `CREW_MAX_ITER` and `CREW_MAX_RPM` are respected in the phase-end flow
- [ ] Phase-end workflow completes successfully with guardrails
- [ ] No regressions in the phase-end gate behavior

## Dependencies
- **Blocked By**: PAIML-CREW-001, PAIML-CREW-003, PAIML-CREW-007
- **Blocks**: PAIML-CREW-005, PAIML-CREW-008
