# Fase 26 — Analyst coach tools (chatbot) — ✅ DONE

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: recommendations review 2026-08-27 — extend the
> analyst chatbot (WS `/ws/analyst-chat`) from *interpret / classify / edit* to *coach*: session
> comparison, cohort standing, plans, per-metric and per-frame deep dives, trends, focus
> recommendations and injury-risk scanning.

## Contexto

The analyst chatbot currently exposes 7 tools (`list_videos`, `histogram`, `classify`,
`extract_frames`, `crop`, `get_coach_insights`, `segment_insight`). It interprets stored analysis
data but cannot answer the coach's core questions: *"did I improve vs last session?", "where do I
stand vs the cohort?", "what exactly is wrong at second 3 and what should I work on next?"*.

Phase 24 shipped the session-over-session delta backend (`MetricDeltasService`) for the FE; Phases
21–23 shipped LLM coach envelopes (`coach_summary`, `coach_plan`, `coach_pose`, `coach_insights`)
cached on the video doc; the histogram doc carries `resampled` curves, `z_mean`, `scores`,
`detections`, `phases` and `critical_*`. All eight tools below are **thin, read-only facade
adapters** over this existing infrastructure — the analysis pipeline, LSTM and edit tools are
unchanged.

## Alcance

One sync chatbot tool per recommendation, following the established pattern:
`AnalystFacade` method (structured `{"error": ...}` on invalid/missing data, never raises) → thin
`ToolSpec` handler in `analyst_chatbot/tools.py` → one line in `ANALYST_SYSTEM_PROMPT`.

### Tools (PAIML-POLE-API-074..082)

| Ticket | Tool | What it answers | Reused assets |
| :--- | :--- | :--- | :--- |
| 074 | `compare_sessions` | "Did I improve vs last session?" — per-metric `delta_pct` + peak flags | `MetricDeltasService.compute` (Phase 24) |
| 075 | `cohort_percentiles` | "Where do I stand vs the cohort on each metric?" — percentile rank + min/median/max | `AnalysisHistogramRepository.max_scores_by_trick` + new score-distribution aggregation |
| 076 | `improvement_plan` | "Give me a plan to master <trick>" — 4-week plan | `CoachService.plan` (Phase 21, cached `coach_plan`) |
| 077 | `metric_deep_dive` | "Why is my <metric> off at second 3?" — one metric curve + cohort band + worst frames | `video_histograms.resampled`, `skeleton_cohort_signals`, `compute_metric_z_score` |
| 078 | `frame_pose` | "What's wrong exactly at frame/second X?" — joint angles (deg) + metric snapshot + explanation | `CoachService.insights_for_frames`, `skeleton_landmarks.biomech_features` |
| 079 | `progress_trend` | "Am I plateauing?" — metric trend across all sessions of the same trick | `AnalysisHistogramRepository.find_baseline` chain + `numeric_scores` |
| 080 | `focus_recommendation` | "What should I work on next?" — top-N focus areas ranked by deviation | `video_histograms.detections` / `_deviations_by_phase` logic |
| 081 | `risk_scan` | "Any injury-risk moments?" — hyperextension / extreme joint-angle frames | `pose_service.build_pose_issues` + `biomech_features` |
| 082 | `get_coach_summary` | "What did the coach say before?" — read cached `coach_summary` / `coach_pose` | cached envelopes on the video doc (Phase 21) |

### Rules (shared by all nine)

- **Read-only, no LLM plumbing in the facade** (except the two that reuse `CoachService`'s own
  `_ask`): the chat LLM phrases the answer; the tools return structured data.
- **Never fabricate**: missing keys / no baseline / no cohort / no cached envelope → omit or
  return a structured error the agent relays cleanly (mirror the existing facade contract).
- **Analysis-DB id namespace** only (`analysis-db.videos` / `video_histograms` /
  `skeleton-landmarks` + `skeleton_data.skeleton_cohort_signals`), per Team-Lead decision.
- **Cap payloads** fed back to the LLM (frame lists, series) to keep ReAct reasoning small.

## Endpoints / wiring

No new REST endpoints — tools are registered on the existing analyst `ToolRegistry`
(`register_analyst_tools`) and reachable over the existing `WS /ws/analyst-chat`. The system
prompt's tool list (`ANALYST_SYSTEM_PROMPT`) is the only other surface to touch.

## Implementation Roadmap

### Phase A — Data-ready read tools (tickets 074, 075, 077, 079)
Repos/aggregations the rest depend on (`find_baseline` exists; add score-distribution aggregation,
trend-chain traversal). Delivered with their own sync tools.

### Phase B — Coach read tools (tickets 076, 078, 082)
Reuse the cached coach envelopes + `CoachService` actions as chatbot tools; pure cache reads first
(082), then generation-backed (076, 078).

### Phase C — Decision tools (tickets 080, 081)
Deterministic ranking / threshold scanning over existing detections + biomech features.

## Quality Gates

- **Unit Tests:** `pixi run test-api` (facade + tool-registry + pure-math tests; guarded
  `analysis_db_testing`).
- **Coverage Requirement:** ≥ 80%.
- **Prompt check:** `ANALYST_SYSTEM_PROMPT` lists the new tools; the existing "these N are the
  ONLY tools you can call" sentence stays accurate.
- **No cross-slice imports:** handlers stay thin adapters over `AnalystFacade` (the facade is the
  only module allowed to touch analysis/tools infrastructure).

## Dependencies

- **Blocks:** optional `pole_analyst` FE suggestions (chat auto-suggestion of new prompts).
- **Blocked By:** Phase 24 (`MetricDeltasService`, #114) and Phases 21–23 coach envelopes — merged.

## Open Questions

- Percentile method for `cohort_percentiles`: exact rank vs bucket (decile/quartile)?
  **RESOLVED (implemented): exact percentile rank only.** A decile fallback for small cohorts
  (< 10 videos) was prototyped but rejected as a behavioral no-op — with fewer than 10 values each
  decile bucket holds < 1 value, so bucketing is identical to the exact rank. `_cohort_percentile`
  is exact-rank (`count(<= value) / count`) for any cohort size; a fully-empty cohort is answered
  as a structured error.
- `risk_scan` thresholds: reuse `build_pose_issues` bands as-is in v1 (no new tuning).
  **RESOLVED (implemented):** `build_pose_issues` defines no angle bands (it formats detections
  into issues), so `scan_risk_frames` ships explicit v1 defaults (hyperextension >185°,
  deep flexion <100°, chosen from the joint-angle semantics where 180 = straight), injectable for
  tests. Only `*_deg` angle features are scanned — normalized extension/width/ratio features are
  never risk-flagged.
