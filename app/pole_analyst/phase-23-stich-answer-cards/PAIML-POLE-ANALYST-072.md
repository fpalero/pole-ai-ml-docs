# Ticket: PAIML-POLE-ANALYST-072

## Title
[FE] Stitch chatbot answer cards (structured blocks rendering)

## Description
Phase 23. Render the `PAIML-POLE-API-090` Task 6 structured block types as the Stitch
"Pole AI Coach" Multimodal Analysis Answer Card sections inside the analyst chat pane:
`score_summary` → executive summary + Kinetic Score badge; `image` (phase_label, chips)
→ CV telemetry frames bento; `phasic_feedback` → key movement observations list;
`metric_matrix` → biomechanical metric variance matrix table; `drills` → prescriptive
corrective protocol cards; `quick_replies` → quick-reply action pills; existing
`video_segment` → mobile video-reference card (reuse current render). Backend contract:
`PAIML-POLE-API-090` (`pole_api` Phase 30, Task 6 — block vocabulary + `RAG_DB_DESCRIPTIONS`
+ safe FE fallback). Design reference (no pasted HTML): Stitch screens desktop answer
card `e6a4363e82ac4a5db060426f97ae0bdd`, mobile variant `ed50e9f93f3748b98a3f62ad31c65883`,
mobile chat `8153376de3af4761875082b8950fd49a`; files under `/tmp/opencode/stitch-cards/`
(`answer-card.html`, `answer-card-desktop.png`, `chat-mobile.html`).

## What to Do (Implementation Steps)
- [ ] Per-block card components/rendering in `app/pole_analyst` for `score_summary`,
      `phasic_feedback`, `metric_matrix`, `drills`, `quick_replies`, and `image`
      (2-col bento with phase tag + metric chips); header metadata + feedback footer
      (thumbs) if present in the Stitch design.
- [ ] Chat-pane integration (`chat-pane.component.ts`) + block model update
      (`chat-message.ts`); keep the graceful unknown-block fallback from API-090 6c
      (no raw JSON, no crash).
- [ ] Desktop + mobile parity with the Stitch screens listed above (Angular 22,
      SignalStore, Tailwind per `pole_fe` conventions).
- [ ] Quick-reply pill actions as FE-side suggestions only (no backend calls).
- [ ] Unit tests ≥ 80% for the new card components + fallback cases; Playwright spec
      for the answer-card render path.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Each card section renders from its block JSON (`score_summary`, `phasic_feedback`,
      `metric_matrix`, `drills`, `quick_replies`, `image`, `video_segment`).
- [ ] Unknown-block graceful fallback preserved (from API-090 6c): no raw JSON, no crash.
- [ ] Design parity vs the Stitch answer-card screens (desktop + mobile).
- [ ] WCAG 2.1 AA for the new card components.
- [ ] No regressions in existing chat features (md/image/video_segment rendering,
      raw-JSON fallback from PAIML-POLE-ANALYST-071).

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Playwright (`npx playwright test`, specs en `app/pole_analyst/e2e/`) contra
      `pola_api` con `POLA_API_DB=pole_api_testing`, `SKELETON_DB=skeleton_data_testing`,
      `ANALYSIS_DB=analysis_db_testing`, `E2E_FAKES=1` (guardado por
      `scripts/guard-testing-db.sh`, nunca prod DBs).

## Dependencies
- **Blocks**: None
- **Blocked By**: None — NOTE AS PROSE ONLY: Starts after PAIML-POLE-API-090 merges
  (team-lead release gate; cross-project, not enforced by crew-validate). No formal
  cross-project `Blocked By` ID (crew-validate would reject it).

## Estimated Effort
- [L]
