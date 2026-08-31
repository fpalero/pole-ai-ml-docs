# Fase 3 — Video Library + Upload (right, default mode) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Tareas

- [ ] App `VideosService.list` → `GET /api/analysis/videos` (cada item con flag `analyzed`); thumbnail via `GET /api/analysis/videos/{id}/thumbnail`.
- [ ] App `VideosService.upload` → `POST /api/analysis/videos` (multipart `.mp4` → carpeta de análisis dedicada + `analysis-db.videos` con `analyzed=false`).
- [ ] Presentation `VideosLibraryPane`: search, `VideoCard` grid (thumbnail, filename, date, badge, acciones "Analyze"/"Open analysis"), `UploadDropzone`.
- [ ] Presentation empty-state + mensaje de bienvenida del chatbot (librería vacía).
- [ ] Test unit tests T3.x (list mapping, upload, badge logic, empty state).

## Criterios de aceptación

- [ ] Librería de videos + upload funcionales; tests T3.x verdes (UC-01/05/07).