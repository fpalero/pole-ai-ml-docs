# Fase 4 — Video Detail Tabs (right, detail mode) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Tareas

- [ ] App `AnalysisService.trigger` → `POST /api/analysis/videos/{id}/analyze` (202 job), poll `GET /api/analysis/jobs/{job_id}` hasta `done`; al terminar, refresh tabs + `analyzed=true`.
- [ ] Presentation `SummaryTab` → `GET /api/analysis/videos/{id}/summary` (metric cards: duraciones de fase, critical frame/phase/metric, max z-score).
- [ ] Presentation `HistogramTab` → `GET /api/analysis/videos/{id}/histogram` (resampled metrics + `scores`, chart con cohort marker de `signal_histograms`).
- [ ] Presentation `PoseTab` → frame analizado con skeleton overlay + correction hints (de `detections[].frame_image_path` / pose endpoint).
- [ ] Presentation `PlanTab` → texto `agent_reply` renderizado como improvement plan + errores detectados (parseados del último analysis turn).
- [ ] Test unit tests T4.x (job polling, mapping DTO de cada tab, chart data transform).

## Criterios de aceptación

- [ ] Detail mode con 4 tabs funcionales; tests T4.x verdes (UC-02/03/06).