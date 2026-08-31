# Ticket: PAIML-CREW-003

## Title
Apply guardrails to agents + tasks

## Description
Wire the `apply_guardrails()` function from `guardrails.py` onto all 5 CrewAI agents in `crew_implement.py`, and add task-level guardrail validation functions to the dev, review, and test tasks.

## What to Do
- Import `apply_guardrails`, `validate_dev_output`, `validate_review_output`, `validate_test_output` from `crew.guardrails`
- In `build_crews()`, after creating each agent, call `apply_guardrails(agent)`:
  - `developer = apply_guardrails(developer)`
  - `reviewer = apply_guardrails(reviewer)`
  - `tester = apply_guardrails(tester)`
  - `doc_agent = apply_guardrails(doc_agent)`
  - `developer_fix = apply_guardrails(developer_fix)`
- In `implement_ticket()`, add `guardrail=` to task creation:
  - `dev_task = Task(..., guardrail=validate_dev_output)`
  - `review_task = Task(..., guardrail=validate_review_output)`
  - `test_task = Task(..., guardrail=validate_test_output)`
- Also add guardrails to the bug-fix loop tasks:
  - `fix_task = Task(..., guardrail=validate_dev_output)`
  - `re_review = Task(..., guardrail=validate_review_output)`
  - `re_test = Task(..., guardrail=validate_test_output)`
- Ensure the `resolve_task` (merge conflict resolution) also gets `guardrail=validate_dev_output`

## Acceptance Criteria
- [ ] All 5 agents have `max_iter` and `max_rpm` set after `apply_guardrails()`
- [ ] `dev_task`, `fix_task`, `resolve_task` use `guardrail=validate_dev_output`
- [ ] `review_task`, `re_review` use `guardrail=validate_review_output`
- [ ] `test_task`, `re_test` use `guardrail=validate_test_output`
- [ ] Guardrail validation errors are fed back to the agent for self-correction

## Dependencies
- **Blocked By**: PAIML-CREW-001, PAIML-CREW-002, PAIML-CREW-007
- **Blocks**: PAIML-CREW-004, PAIML-CREW-005, PAIML-CREW-008
