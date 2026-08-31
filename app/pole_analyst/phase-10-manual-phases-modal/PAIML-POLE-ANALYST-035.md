# Ticket: PAIML-POLE-ANALYST-035

## Title
[Presentation] Flujo LSTM-fail (preguntar truco) + prompt de reproceso

## Description
Phase 10 (§2, §3). If LSTM classification returns `null` (low confidence), the FE asks the athlete for
the trick name (free input with suggestions of existing classes). On re-upload of an already-analyzed
video, the FE asks "¿Reprocesar?" — never reprocesses automatically except corrupt video.

## What to Do (Implementation Steps)
- [ ] Trick-name prompt when `trick_label=null` (free input + existing class suggestions).
- [ ] Submit via `submitTrickName` → final feedback/analysis.
- [ ] Reprocess prompt on re-upload of analyzed video (not automatic except corrupt video).
- [ ] Unit tests: LSTM-fail prompt + reprocess prompt flows.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] LSTM fail → trick-name prompt; re-upload of analyzed video → reprocess prompt (not automatic).
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-036, PAIML-POLE-ANALYST-037
- **Blocked By**: PAIML-POLE-ANALYST-033, PAIML-POLE-ANALYST-034, PAIML-POLE-API-049, PAIML-POLE-API-054

## Estimated Effort
- [M]