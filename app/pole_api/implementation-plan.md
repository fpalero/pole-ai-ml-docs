# `pola_api` — Plan de implementación por fases

Basado en los flujos de `docs/app/pola_api/flows.md`. Objetivo: implementar los endpoints de los
tres slices (training, crawler, video) de forma incremental, con cada fase entregando endpoints
funcionales y tests verdes.

**Estrategia transversal**

- Cada fase reutiliza los paquetes existentes (`pole_crawler`, `pole_ml`, `pole_tools`); no se escribe ML nuevo.
- Infra compartida (config, errores, Mongo, job runner) vive en `src/core/` (no es un slice; es el caso
  "no se puede aislar" → se estudia y se centraliza). Los repos de cada slice usan `src/core/mongo.py`.
- Tests: `pytest` con `fastapi.testclient.TestClient`. Unit tests con repos fake; tests de integración
  con Mongo real (docker-compose). Se añade la task `pixi run test-api` (cwd `app/pola_api`).
- Criterio de salida de cada fase: los UCs de la fase pasan (según assertions de `flows.md`) y no se
  rompen los tests existentes del workspace.

---

## Fase 1 — Fundamentos (infra compartida)

**Objetivo:** base estable y testeable de la app.

**Alcance (nuevo)**
- `src/core/config.py` — env settings: `MONGODB_URI`/`MONGO_URI`, `POLE_AI_ROOT`, `FFMPEG_BIN`, `INSTAGRAM_USERNAME`/`INSTAGRAM_CSRFTOKEN`/..., `SESSION_FILE_PATH`, `API_KEY` (opcional).
- `src/core/errors.py` — excepciones de dominio (`NotFound`→404, `Conflict`→409, `ValidationError`→422) + exception handlers en FastAPI.
- `src/core/mongo.py` — helper de conexión Mongo (client único para la app).
- `src/core/jobs.py` — job runner (threads/`BackgroundTasks`), colección `jobs` con `{kind, entity_id, status[pending|running|done|failed], progress, error}`. Base para los `GET /{slice}/jobs/{id}`.
- Setup de tests: `tests/` en `app/pola_api/`, fixtures, task `test-api` en `pixi.toml`.

**Verificación**
- `/health` 200.
- `GET /{slice}/jobs/{id}`: plantilla por slice devuelve `404` para id inexistente (UC-71).
- Unit tests del job runner (pending→running→done/failed).

**Entregable:** app con infra compartida y un test por slice que valide el wiring de routers.

---

## Fase 2 — Slice training: Classes + status machine

**Objetivo:** CRUD de clases completo (UC-01..06).

**Alcance (slice training)**
- `repositories/class_repository.py` — colección `classes` en Mongo.
- `services/class_service.py` — CRUD + validaciones (nombre único, `transition` reservado).
- `controllers/classes.py` — `POST/GET/GET{id}/PATCH/DELETE /api/training/classes...` + `/stats` (UC-04 stub: lectura de conteos).

**UC cubiertos:** UC-01, UC-02, UC-03, UC-04, UC-05, UC-06.
**Dependencias:** Fase 1.
**Touchpoints:** ninguno.

**Verificación:** assertions de UC-01..06 (201/404/409/422, clases stateless).

**Entregable:** clases gestionables; base para todos los flujos (todo referencia `{id}` de clase).

---

## Fase 3 — Slice training: Process + Jobs

**Objetivo:** procesar clips aceptados → ventanas Mongo + embeddings Chroma (UC-40..42).

**Alcance (slice training)**
- `repositories/job_repository.py` — jobs del slice.
- `services/process_service.py` — reutiliza `pole_ml`: `ProcessingPipeline.process_data` + `save_windows_embeddings`, `WindowRepository`, `SkeletonStorage`, `ChromaClassifier`. Idempotencia vía campos de Mongo (`embedding_status`/`embedding_model`).
- `services/process_service.py` — reutiliza `pole_ml`: `ProcessingPipeline.process_data` (extract-only) + `save_windows_embeddings` (embed), `WindowRepository`, `SkeletonStorage`, `ChromaClassifier`. Idempotencia vía `embedding_models` (lista por modelo).
- `controllers/process.py` — `POST /api/training/classes/{id}/process` (extract) y `POST /api/training/classes/{id}/embed`.
- `controllers/jobs.py` — `GET /api/training/jobs/{id}`.

**UC cubiertos:** UC-40, UC-41, UC-42, UC-70, UC-71.
**Dependencias:** Fases 1, 2.
**Touchpoints:** process/embed done → windows `processed` / `embedding_models` anotado (interno al slice).

**Verificación:** UC-40/41/42 (windows en Mongo, embeddings en Chroma, idempotencia).

**Entregable:** motor de embedding/process reutilizable por upload (Fase 5) y retrain (Fase 7).

---

## Fase 4 — Slice crawler: Crawl + QC

**Objetivo:** descargar vídeos de Instagram y QC humano (UC-20..24).

**Alcance (slice crawler)**
- `repositories/crawl_repository.py`, `post_repository.py`.
- `services/crawl_service.py` — reutiliza `pole_crawler`: `InstagramClient.get_posts`, `DiskWriter.save_video`, waits anti-bot (`random.uniform(min_wait, max_wait)`), `.meta.json`, crea posts `pending`.
- `services/post_service.py` — listado y QC.
- `controllers/crawls.py` — `POST /api/crawler/classes/{id}/crawl`, `GET .../crawls`, `GET .../posts`, `POST /api/crawler/posts/{id}/qc`.
- `controllers/jobs.py` — `GET /api/crawler/jobs/{id}`.

**UC cubiertos:** UC-20, UC-21, UC-22, UC-23, UC-24, UC-70/71.
**Dependencias:** Fases 1, 2.
**Touchpoints:** crawl done → `videos` `source=crawler` (crawler → training vía colección compartida).

**Verificación:** UC-20..24 (posts con `local_path`, `downloaded_count`, error rate-limit).

**Entregable:** crawler del pipeline; alimenta el cut (Fase 6).

---

## Fase 5 — Slice video: Upload + auto-embed

**Objetivo:** subir vídeos de una clase nueva y auto-embed (Workflow A, UC-10..12).

**Alcance (slice video)**
- `repositories/upload_repository.py`.
- `services/upload_service.py` — multipart (`.mp4`), guardado en `videos/<trick>/` (o ruta de upload), lanza job de auto-embed reutilizando `ProcessService` (training) o `pole_ml` directamente.
- `controllers/uploads.py` — `POST /api/video/classes/{id}/videos`, `GET .../uploads`, `POST .../uploads/{uid}/verify`.

**UC cubiertos:** UC-10, UC-11, UC-12, UC-70/71, UC-81 (parcial).
**Dependencias:** Fases 1, 2, 3 (auto-embed).
**Touchpoints:** upload done → uploads `verified`; verify humano confirma (video → training vía `videos` `source=upload`).

**Verificación:** UC-10..12 (uploads `verified`, ventanas+embeddings creados, error de job).

**Entregable:** ingestión manual de clases nuevas (Chroma-only).

---

## Fase 6 — Slice video: Cut + Review

**Objetivo:** cortar sources en clips y revisión humana (UC-30..35).

**Alcance (slice video)**
- `repositories/clip_repository.py`.
- `services/cutter_service.py` — reutiliza `pole_tools.VideoCutter` con `cutter_config` de la clase (de Mongo), sources = posts aceptados / uploads / rutas; clips → `curated/<trick>/`.
- `services/clip_service.py` — listado, streaming (`FileResponse`), accept/discard.
- `controllers/cut.py` — `POST /api/video/classes/{id}/cut`, `GET .../clips`, `GET /api/video/clips/{id}/video`, `POST /api/video/clips/{id}/accept|discard`.

**UC cubiertos:** UC-30..35, UC-70/71.
**Dependencias:** Fases 1, 2, 4 (posts como sources).
**Touchpoints:** cut done → clips `pending`; `ClipService.accept` crea el video entrenable (`kind=clip`).

**Verificación:** UC-30..35 (clips `pending`, streaming mp4, accept/discard).

**Entregable:** corte y curado de vídeo; alimenta process (Fase 3).

---

## Fase 7 — Slice training: Model registry + Retrain

**Objetivo:** versionado de modelos y promoción de clases (UC-50..64).

**Alcance (slice training)**
- `repositories/model_run_repository.py` — `model_runs` en Mongo + `active.json` en `models/runs/<run_id>/`.
- `services/model_registry_service.py` — listado, detalle, `activate`, `approve`, `reject`.
- `services/train_service.py` — reutiliza `pole_ml`: `ProcessingPipeline.train_model_normal` / `fine_tune_model`, `ModelTrainer.fine_tune`, `WindowRepository.insert_training_run`/`mark_trained`, `ModelPersistence`; escribe `models/runs/<run_id>/` y re-embebe.
- `controllers/models.py` — `GET /api/training/models...`, `POST .../activate|approve|reject`.
- `controllers/retrain.py` — `POST /api/training/classes/{id}/retrain`.

**UC cubiertos:** UC-50..54, UC-60..64, UC-70/71.
**Dependencias:** Fases 1, 2, 3.
**Touchpoints:** retrain done → run `done` (no activo); approve → run `active` (pasa a modelo LSTM activo).

**Verificación:** UC-50..64 (runs versionados, encoder con n+1 clases, active pointer, gate de aprobación).

**Entregable:** ciclo completo de promoción de una clase a LSTM.

---

## Fase 8 — Integración E2E + touchpoints cross-slice + housekeeping

**Objetivo:** flujos completos funcionando de extremo a extremo.

**Alcance**
- **Coordinación cross-slice**: clases stateless (sin transiciones de estado); la coordinación
  ocurre vía la colección compartida `videos` (un video se refiere por id, con `can_process` como
  gate de elegibilidad) y los jobs por slice. Afectaba a: crawl, cut, upload, process/embed,
  train/retrain (ver `flows.md` §13).
- **Tests E2E**: UC-80 (Workflow B completo) y UC-81 (Workflow A completo) contra app real + Mongo.
- **Housekeeping**: `.env.example`, `README.md` de la app, `docker-compose.yml` dev (Mongo), actualizar `docs/app/pola_api/slices.md` y `flows.md` si hubo cambios de diseño.

**Mecanismo elegido (implementado):** clases **stateless** — la máquina de estados se eliminó
(`src/core/status.py` quedó como placeholder). Cada slice validada por entidades relacionadas y
escribe la colección compartida `videos`; los assets comunes viven en `core/`
(`video_repository.py`, `embed_runner.py`). Ningún slice importa a otro; el desacoplamiento se
verifica con tests `test_*_does_not_import_training`. Detalle en `flows.md` §13.

**Verificación:** UC-80 y UC-81 verdes de punta a punta.

**Entregable:** app funcional completa para Workflows A y B.

---

## Fase 9 — Futuro (fuera de este plan)

- Auth opcional `X-API-Key` (`API_KEY` env) — prevista en el spec.
- `pole_fe` (frontend) — consumirá los endpoints según los elementos FE de `flows.md`.
- Celery/Redis para jobs distribuidos (sustituye al runner de threads) cuando se desplegue en k8s.

---

## Mapa fases ↔ flows

| Fase | Slice(s) | UCs | Workflow |
|---|---|---|---|
| 1 | core | health, UC-70/71 (base) | — |
| 2 | training | UC-01..06 | base |
| 3 | training | UC-40..42 | B (final) / A (auto-embed) |
| 4 | crawler | UC-20..24 | B (inicio) |
| 5 | video | UC-10..12 | A |
| 6 | video | UC-30..35 | B (medio) |
| 7 | training | UC-50..64 | C / D |
| 8 | todos | UC-80, UC-81 | A+B E2E |
