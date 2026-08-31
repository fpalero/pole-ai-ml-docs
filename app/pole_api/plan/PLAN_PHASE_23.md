# Fase 23 — Coach UI (Summary tab cards + notification + chat auto-suggestion) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Dependencia: Phase 22 backend (coach insights, fps, pose frames)

## Contexto

Phase 22 delivers the backend: fps storage, lazy pose extraction, coach insights service, and
pipeline integration. Phase 23 wires the frontend to consume this data and surfaces analysis
completion to the user via notifications and chat.

## PO Decisions Locked

- **Q7=B**: Keep existing phase timeline + add time-based durations bar.
- **Q6**: Chat auto-sends agent_reply + FE shows notification banner.
- **Q8=FUTURE**: Chat→right-panel loading deferred.

## Alcance

### 1. Summary tab enhancement (ticket 070)
- `CoachInsightsCardComponent` — renders ✅/⚠️/❌ insight cards from `/coach-insights`.
- `DetectedErrorCardComponent` — renders top wrong insight as dedicated error card.
- `PhaseDurationsBarComponent` — time-based durations using stored fps.
- Keep existing phase timeline alongside.

### 2. Notification + chat auto-suggestion (ticket 071)
- `AnalysisNotificationComponent` — dismissible banner on analysis completion.
- Chatbot auto-sends `agent_reply` with deviation summary after analysis.

## Implementation Roadmap

### Phase A: Summary tab (ticket 070)
- [ ] Three new standalone components.
- [ ] Wire into SummaryTabComponent.
- [ ] Unit tests.

### Phase B: Notification + chat (ticket 071)
- [ ] Notification banner component.
- [ ] Chat auto-suggestion in worker.
- [ ] Unit tests.

## Quality Gates

- **Unit Tests:** `pixi run test-analyst` (FE), `pixi run test-api` (backend).
- **Coverage Requirement:** ≥ 80%.
- **UX:** notification auto-dismiss 8s; insights cards render in < 1s.

## Risks and Mitigations

- **Risk:** Notification conflicts with existing ProgressPanelComponent. **Mitigation:** notification
  is a separate banner above the progress panel, not overlapping.
- **Risk:** Chat auto-suggestion fires for every analysis (noisy). **Mitigation:** only fire when
  there are deviations (|z| > 2); silent for clean analyses.
