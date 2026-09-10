# Ticket: PAIML-POLE-API-118

## Title
M-code to metric-name mapping before metric_deep_dive (batch-3 Q9 residual)

## Status
📋 PLANNED

## Description
Phase 36 staging gate (image `8425896` FRESH, batch-3 `20260910-233736`):

- **Q:** *"Analyse my latest handspring video — I can also do Butterfly,
  what should I focus on first?"*
- Primera llamada `metric_deep_dive` con `{"metric": "M-05",
  "video_id": "6a9e65efc910c95e7f430d6a"}` → `ok:false`:
  `metric 'M-05' not found for video '6a9e65efc910c95e7f430d6a';
  available metrics: angular_speed, body_tilt, hip_height,
  torso_tilt_speed, wrist_stability` (verbatim en `batch3-frames.json`).
  El agente pasa códigos `M-01..M-05` donde `metric_deep_dive` espera
  nombres → `analysis_failed` en ese intento.
- El turno se recupera (retry con `body_tilt` OK; 10/11 tools OK:
  `list_videos`, `focus_recommendation`, `get_coach_insights`,
  `query_pole`, `query_biomechanics`, `query_calisthenics`,
  `metric_deep_dive`, `frame_pose`×2, `query_pole`) y la precedencia de
  vídeo se mantiene (handspring analizado, sin secuestro de Butterfly).
  El residuo es el intento fallido + el coste/latencia del retry
  (turno: 81 s).
- Evidence: `app/pole_analyst/test-results/coach-150q/batch3-20260910-233736/batch3-transcript.jsonl`
  (`BATCH3-Q9`, `all_tool_calls` con un `metric_deep_dive ok:false`) y
  `batch3-frames.json` (error verbatim).

What to do (no code in this ticket — spec for the implementer):

- [ ] Normalizar M-codes a nombres ANTES de la llamada a insights: tool
      spec (enum de métricas válidas), prompt (instruir nombres, no
      códigos), o capa de mapeo en el facade (implementer elige; una sola
      capa, no las tres).
- [ ] El vocabulario válido es por-vídeo (`available metrics` del error);
      nunca inventar nombres fuera de él.
- [ ] Mantener la precedencia de vídeo (label del histograma > mención
      free-text Butterfly) — verificado en este turno, no regressar.

## Files Affected
- `metric_deep_dive` tool spec / prompt / facade mapping layer
  (`app/pole_api/src/analyst_chatbot/`; implementer to locate)
- tests: M-code normalization (new, co-located)

## Unit-Test Requirement
- [ ] `metric_deep_dive` invoked with `M-05` (o cualquier `M-0X`) →
      mapped to the video's valid metric name before dispatch (assert: no
      `analysis_failed`, no `not found` error).
- [ ] Unknown/invalid code outside `M-01..M-05` and outside the video
      vocabulary → clean error/delegation, never a fabricated metric name.
- [ ] Video precedence (histogram label > free-text mention) preserved.

## Integration Tests
- [ ] Re-run staging Q9 only green: first-attempt `metric_deep_dive`
      succeeds (no `ok:false`), turn completes, video precedence holds
      (handspring, no Butterfly hijack).
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] Q9 completes with zero `metric … not found` failures.
- [ ] No fabricated metric names; mapping constrained to the video's
      available metrics.
- [ ] No regression to video-precedence or the 10/11 tool path.

## Dependencies
- **Blocks**: none.
- **Blocked By**: none (independent of PAIML-POLE-API-117).

## Estimated Effort
- [S]
