# `pola_api` — Endpoint Flows / Use Cases

Documento de **casos de uso** de la app `pola_api` construidos sobre los endpoints definidos
en `docs/app/pola_api/slices.md`. Objetivos:

1. **Testing**: cada caso de uso sirve como guion de test de los endpoints (happy paths + errores/edge).
2. **FE**: cada caso de uso lista los elementos de interfaz necesarios para soportar el flujo.

Decisiones asumidas (confirmadas): estado en **MongoDB**, `classes` en slice **training`,
`uploads` en slice **video**, **jobs por slice** (`GET /{slice}/jobs/{id}`), clases **stateless**
(no hay máquina de estados de clase; la validación se hace por entidades relacionadas).

---

## 1. Referencia: modelo de estados de clase

Las clases **no tienen campo `status`** y no hay transiciones de estado. La "etapa" de una clase se
deriva de sus entidades relacionadas (uploads, posts, clips, videos, windows, model_runs), no de un
estado almacenado. El FE deriva la etapa en la UI.

La **preparación para entrenar** (antes `awaiting_training`) se expresa por datos: la clase es
entrenable cuando sus videos seleccionados tienen windows en `skeleton_windows` (label = clase) con
`selected_for_training=true` (ventana) y ChromaDB contiene sus embeddings (`embedding_models` no
vacío).

> **Nota:** No existe el estado `chroma_only` ni estados de clase. El modo chroma-only es un flag
> del `video_cutter` (`POST /api/video/classes/{id}/cut` → `chroma_only: true`), no parte del flujo
> de entrenamiento. La promoción a candidata de entrenamiento es un flag manual por video:
> `PATCH /api/training/videos/{video_id}` `{selected_for_training: true}`.

## 2. Convenciones

- Todos los endpoints devuelven JSON salvo `GET /api/video/clips/{id}/video` (mp4) y DELETE (204).
- Los jobs se lanzan en background (threads). El FE hace **polling** con
  `GET /{slice}/jobs/{id}` hasta `done|failed`; `progress` (0–1) y `error` cuando falla.
- `{id}` de clase y `{run_id}` de modelo son strings.
- Las clases son stateless: ninguna operación cambia un estado de clase; cada endpoint valida las
  entidades relacionadas (videos `clip`, clips `accepted`, windows, model_runs).

---

## 3. Casos de uso — Clases (slice training)

### UC-01 — Crear una clase (trick) nueva
- **Slice(s):** training
- **Actores:** Usuario (FE), `ClassService`, job
- **Precondiciones:** Ninguna.
- **Flujo:**
  1. `POST /api/training/classes` (síncrono, `201` + objeto clase) **o** `POST /api/training/classes/jobs` (asíncrono, `202` + `{job_id}`) con `{name, hashtags, min_videos?, min_windows?, cutter_config?}`.
  2. El sistema valida nombre (único, no vacío, no reservado). En el modo job, la validación es síncrona (4xx inmediato) y la inserción corre como job monitorizable (slice training, descripción `created <name>`).
- **Estado final:** clase creada.
- **Assertions de test:**
  - `201` / `202` + `{job_id}` (job `done` al final).
  - `name` duplicado → `409`; `name` reservada/vacía / hashtags sin `#` → `422`.
  - `GET /api/training/classes` la lista.
- **Elementos FE:** formulario "Nuevo trick" (nombre, hashtags, umbrales, config cutter); el alta aparece en System Jobs.

### UC-02 — Listar clases
- **Slice(s):** training
- **Flujo:**
  1. `GET /api/training/classes?name=`
- **Assertions de test:** 200 + array; filtro `name`; las clases candidatas a entrenar se derivan de
  videos con `selected_for_training=true`.
- **Elementos FE:** listado de tricks con badge de "candidato a promocionar".

### UC-03 — Ver detalle de una clase (+ pipeline state)
- **Flujo:**
  1. `GET /api/training/classes/{id}`
- **Assertions de test:** 200 + clase; la etapa de pipeline se deriva de entidades (videos, clips, windows), no de un campo `status`. `{id}` inexistente → `404`.
- **Elementos FE:** pantalla de detalle del trick mostrando en qué paso está (para saber qué acción humana toca).

### UC-04 — Ver stats de una clase
- **Flujo:**
  1. `GET /api/training/classes/{id}/stats`
- **Respuesta:** samples-info (windows embebidas/pendientes/entrenadas por label, leídos de la DB
  `skeleton_data`), distribución en Chroma, readiness de promoción.
- **Assertions de test:** 200; conteos coherentes con Mongo/Chroma; readiness `true` solo si hay suficientes windows.
- **Elementos FE:** panel de métricas del trick + botón "Promocionar" habilitado según readiness.

### UC-05 — Editar una clase
- **Flujo:**
  1. `PATCH /api/training/classes/{id}` con campos parciales (`hashtags`, `cutter_config`, umbrales).
- **Assertions de test:** 200 + clase actualizada; cambiar `name` a uno existente → `409`.
- **Elementos FE:** edición inline de hashtags/umbrales/config.

### UC-06 — Eliminar una clase
- **Slice(s):** training
- **Flujo:**
  1. `DELETE /api/training/classes/{id}` → lanza un job `delete_class` (slice training, `202` + `{job_id}`) que borra en cascada: clips, vídeos, ficheros físicos, windows, embeddings y la propia clase.
- **Assertions de test:** `202` + job que termina `done`; siguiente `GET /api/training/classes/{id}` → `404`. Puede detenerse (Stop) quedando parcial.
- **Elementos FE:** confirmación de borrado; el job aparece en System Jobs.

---

## 4. Casos de uso — Workflow A: trick nuevo por upload (auto-embed)

### UC-10 — Subir vídeos de una clase nueva (Chroma-only)
- **Slice(s):** video (upload) + training (auto-embed)
- **Actores:** Usuario (FE), `UploadService`, job, `ProcessService`
- **Precondiciones:** clase existente.
- **Flujo:**
  1. `POST /api/video/classes/{id}/videos` (multipart, ficheros `.mp4`).
  2. `UploadService` guarda ficheros, crea `uploads` `pending→processing`, lanza job de auto-embed (process-data → ventanas a Mongo + process-embeddings → ChromaDB).
  3. `GET /api/video/classes/{id}/uploads` muestra los uploads.
  4. Job termina → `uploads` `processing→verified` (auto-verificado por el job).
- **Estado final:** uploads `verified`.
- **Assertions de test:**
  - 202/201 + `uploads[]` + `job_id`.
  - Fichero no `.mp4` → `422`.
  - Polling `GET /api/video/jobs/{id}`: `running` → `done`.
  - Tras done: ventanas en Mongo (label=trick) y vectores en Chroma.
- **Elementos FE:** drag & drop de vídeos, barra de progreso del job, lista de uploads.

### UC-11 — Verificación de upload (automática)
- **Slice(s):** video
- **Flujo:**
  1. El job de upload **auto-verifica** los ficheros en background
     (`uploads.status: pending → processing → verified | failed`); no existe endpoint humano de
     verify (`POST .../uploads/{uid}/verify` fue eliminado).
- **Assertions de test:** tras `done`, `uploads.status == "verified"` (o `"failed"` con `error`);
  los uploads verificados quedan listos para `process`/`embed`.
- **Elementos FE:** estado del upload por fila (sin modal de confirmación manual).

### UC-12 — Error de upload (job falla)
- **Flujo:**
  1. Subida OK → job falla (p.ej. ffmpeg/MediaPipe falla).
  2. `uploads.status → failed`, `GET /api/video/jobs/{id}` devuelve `error`.
- **Assertions de test:** job `failed` con `error` no vacío; re-subida posible tras corregir.
- **Elementos FE:** mensaje de error + reintento de subida.

---

## 5. Casos de uso — Workflow B parte 1: crawl → QC

### UC-20 — Lanzar crawl para una clase
- **Slice(s):** crawler
- **Actores:** Usuario (FE), `CrawlService`, job
- **Precondiciones:** clase existente (puede añadir más datos en cualquier momento).
- **Flujo:**
  1. `POST /api/crawler/classes/{id}/crawl` `{tags: ["handspring"], limit: 10, min_wait: 5, max_wait: 10}`.
  2. Job descarga vídeos a `downloads/<trick>/` y crea `posts` con `qc_status=pending`.
  3. Polling `GET /api/crawler/jobs/{id}` → `done`.
- **Estado final:** crawl `done`; posts `pending`.
- **Assertions de test:** 202 + `job_id`; tras done: `GET /api/crawler/classes/{id}/crawls` muestra 1 crawl `done` con `downloaded_count`; `GET /api/crawler/classes/{id}/posts` devuelve los posts con `local_path` existente.
- **Elementos FE:** formulario de crawl (tags, límite, esperas), progreso del job.

### UC-21 — Listar crawls de una clase
- **Flujo:** `GET /api/crawler/classes/{id}/crawls`
- **Assertions de test:** 200 + array con status/progreso/errores históricos.
- **Elementos FE:** historial de crawls.

### UC-22 — Listar posts para QC
- **Flujo:** `GET /api/crawler/classes/{id}/posts?qc_status=pending`
- **Assertions de test:** 200; filtro `qc_status`; posts con metadatos (username, timestamp, url).
- **Elementos FE:** galería de vídeos descargados para revisar.

### UC-23 — QC de un post (paso humano)
- **Flujo:**
  1. `POST /api/crawler/posts/{id}/qc` `{status: "accepted"|"rejected"}`.
- **Assertions de test:** 200 + post actualizado; al menos 1 aceptado habilita el siguiente paso (cut).
- **Elementos FE:** botones Aceptar/Rechazar por vídeo.

### UC-24 — Error de crawl (sin descargas / anti-bot)
- **Flujo:**
  1. IG devuelve rate-limit o 0 posts → job `failed` (o `done` con `downloaded_count=0`).
- **Assertions de test:** job `failed` con `error` (rate-limit) o `done` con 0 descargas; el FE muestra el estado del crawl y permite reintentar.
- **Elementos FE:** estado de error + botón reintentar.

---

## 6. Casos de uso — Workflow B parte 2: cut → review

### UC-30 — Cortar sources en clips
- **Slice(s):** video
- **Actores:** Usuario (FE), `CutterService`, job
- **Precondiciones:** clase con ≥1 post aceptado (para sources de tipo `post`).
- **Flujo:**
  1. `POST /api/video/classes/{id}/cut` `{sources: [{kind: "post", ref: "post_id"}], cutter_override?, model_id?, chroma_only?}`.
  2. Job construye `VideoCutter` con el `cutter_config` de la clase y corta cada source → clips en `curated/<trick>/`.
  3. Polling `GET /api/video/jobs/{id}` → `done`; clips `pending`.
- **Estado final:** clips `pending`.
- **Assertions de test:** 202 + `job_id`; `GET /api/video/classes/{id}/clips?status=pending` lista los clips; source inexistente → `422`.
- **Elementos FE:** selección de sources (posts aceptados / uploads / ruta) + progreso del job.

### UC-31 — Listar clips
- **Flujo:** `GET /api/video/classes/{id}/clips?status=`
- **Assertions de test:** 200 + array; filtro por status.
- **Elementos FE:** grid de clips con su status.

### UC-32 — Reproducir un clip (revisión)
- **Flujo:** `GET /api/video/clips/{id}/video`
- **Assertions de test:** 200 + `video/mp4`; `{id}` inexistente → `404`.
- **Elementos FE:** reproductor de vídeo inline.

### UC-33 — Aceptar un clip
- **Flujo:** `POST /api/video/clips/{id}/accept` `{label?: "handspring"}`
- **Assertions de test:** 200 + clip `accepted`; label por defecto = clase.
- **Elementos FE:** botón Aceptar en el reproductor.

### UC-34 — Descartar un clip
- **Flujo:** `POST /api/video/clips/{id}/discard`
- **Assertions de test:** 200 + clip `discarded`.
- **Elementos FE:** botón Descartar.

### UC-35 — Error de cut
- **Flujo:** fuente corrupta / ffmpeg falla → job `failed` con `error`.
- **Assertions de test:** job `failed` con `error`; reintento posible.
- **Elementos FE:** error + reintento.

---

## 7. Casos de uso — Workflow B parte 3: process (explicito)

### UC-40 — Procesar/embeder clips (ventanas)
- **Slice(s):** training
- **Actores:** Usuario (FE), `ProcessService`, job
- **Precondiciones:** clase con ≥1 **clip** (flag `clip=true` o `kind='clip'`); solo los clips pueden procesarse/embeberse/entrenarse.
- **Flujo:**
   1. `POST /api/training/classes/{id}/process` `{video_ids[], stride?}` → extrae ventanas de los videos indicados a Mongo y marca `processed`.
   2. `POST /api/training/classes/{id}/embed` `{video_ids[], model_id?}` → embede las ventanas pending/stale a ChromaDB y anota `embedding_models`.
   3. Polling `GET /api/training/jobs/{id}` → `done`.
- **Estado final:** ventanas `processed` y embebidas por el modelo.
- **Assertions de test:** `202` + `job_id`; videos **no clip** → `422` ("only clips can be processed/embedded"); ventanas en Mongo con label=clase; ChromaDB con vectores; `embed` idempotente por modelo.
- **Elementos FE:** botones "Process" / "Embed" (modal de `stride` / `model_id`) + progreso; solo visibles sobre clips.

### UC-43 — Marcar/desmarcar un vídeo como clip (flag)
- **Slice(s):** training
- **Flujo:**
  1. `POST /api/training/classes/{id}/clip` `{video_ids[], clip: bool}` → job que pone `clip=true`, o quita `clip` y pasa `kind='video'` (y limpia `selected_for_training`) cuando `clip=false`.
- **Assertions de test:** `202` + job `done`; los videos con `clip=true` (o `kind='clip'`) son clips; al desmarcar, `selected_for_training` queda `false`.
- **Elementos FE:** botón "Clip" (toggle) en la barra de acciones; pestaña Clips.

### UC-41 — Process/Embed idempotente
- **Flujo:** llamar `POST /api/training/classes/{id}/embed` dos veces con el mismo modelo.
- **Assertions de test:** 2ª llamada no duplica embeddings (Mongo `embedding_models` evita re-embed con el mismo modelo).
- **Elementos FE:** — (aplica automáticamente).

### UC-42 — Error de process (sin datos)
- **Flujo:** `video_ids` vacío/inexistentes o clase sin videos `clip` → `422`.
- **Assertions de test:** error claro sin crear ventanas.
- **Elementos FE:** aviso "no hay videos seleccionados".

---

## 8. Casos de uso — Model registry (slice training)

### UC-50 — Listar runs
- **Flujo:** `GET /api/training/models?mode=&status=`
- **Assertions de test:** 200 + lista de runs (run_id, mode, clases, status, created_at).
- **Elementos FE:** historial de modelos.

### UC-51 — Ver modelo activo
- **Flujo:** `GET /api/training/models/active`
- **Assertions de test:** 200 + run activo; si no hay → `404`/`null` explícito.
- **Elementos FE:** badge "modelo activo".

### UC-52 — Ver detalle de un run
- **Flujo:** `GET /api/training/models/{run_id}`
- **Assertions de test:** 200 + métricas, clases, paths (`models/runs/<run_id>/`); `{run_id}` inexistente → `404`.
- **Elementos FE:** panel de métricas de un run.

### UC-53 — Activar un run (pointer manual)
- **Flujo:** `POST /api/training/models/{run_id}/activate`
- **Assertions de test:** 200; `GET /api/training/models/active` devuelve ese run; se escribe `active.json`.
- **Elementos FE:** botón "Establecer como activo".

### UC-54 — Rechazar un run
- **Flujo:** `POST /api/training/models/{run_id}/reject`
- **Assertions de test:** 200; run `rejected`; no pasa a activo.
- **Elementos FE:** botón Rechazar tras retrain.

---

## 9. Casos de uso — Workflow C: crear modelo / promocionar clase

### UC-60 — Train full (modelo nuevo → LSTM)
- **Slice(s):** training
- **Actores:** Usuario (FE), `TrainService`, job
- **Precondiciones:** las clases indicadas tienen windows con `selected_for_training=true` y embeddings en Chroma (readiness derivada de `stats`).
- **Flujo:**
   1. `POST /api/training/classes/{id}/train` `{classes: ["handspring","shouldermount"], reembed: true}`.
   2. Job reconstruye la red, entrena, escribe `models/runs/<run_id>/` (`.keras`, `_encoder.pkl`, `metadata.json`), marca windows `trained`, re-embebe.
   3. Polling `GET /api/training/jobs/{id}` → `done`; run `status=done` (NO activo).
- **Estado final:** run `done`.
- **Assertions de test:** 202 + `job_id` + `run_id`; ficheros del run existen; `GET /api/training/models/active` sigue siendo el anterior.
- **Elementos FE:** selector de clases a incluir + botón "Entrenar" + progreso.

### UC-61 — Retrain fine-tune (añadir clase a modelo existente)
- **Flujo:** `POST /api/training/classes/{id}/retrain` `{classes, base_model: <run_id>}`
- **Assertions de test:** 202; run `done`; encoder incluye las nuevas clases; pesos base congelados.
- **Elementos FE:** opción "retrain" con base_model.

### UC-62 — Aprobar run (gate humano → activar)
- **Flujo:**
  1. `GET /api/training/models/{run_id}` (revisión de métricas).
  2. `POST /api/training/models/{run_id}/approve`.
- **Estado final:** run `active`.
- **Assertions de test:** 200; `active` apunta al run.
- **Elementos FE:** pantalla de aprobación con métricas + botón Aprobar.

### UC-63 — Error de train/retrain (datos insuficientes / inconsistencias)
- **Flujo:** clases inexistentes, windows insuficientes, o encoder/Chroma desincronizados → job `failed` con `error`.
- **Assertions de test:** job `failed` con `error` accionable.
- **Elementos FE:** error + detalle.

### UC-64 — Más datos de una clase ya integrada en el modelo activo
- **Flujo:** `crawl` → `qc` → `cut` → `review` → `process` → `embed` → `retrain` (fine-tune) de la clase.
- **Assertions de test:** tras retrain los nuevos windows quedan en Mongo/Chroma y el run queda `done` para su gate humano.
- **Elementos FE:** mismos que B + retrain.

---

## 9bis. Casos de uso — Tools (histogram analysis)

> Contrato definido en `PLAN.md` §8.5 (UC-91..94) y §9.5 (UC-95..98). El resumen
> por-vídeo (`GET /api/tools/histograms/summary/{video_id}`) es **Fase 12** y
> está documentado aquí (UC-95..98).

### UC-91 — Submit histogram analysis (happy path) → poll → read back
- **Slice(s):** tools
- **Precondiciones:** ≥2 clips extraídos con `phase_frames` (via `PUT /api/training/clips/{id}/phase-frames`).
- **Flujo:**
  1. `POST /api/tools/histograms/analysis` `{video_ids: ["A","B"]}` → `202 {job_id}`.
  2. Polling `GET /api/tools/jobs/{id}` hasta `done` (`result_json.processed == ["A","B"]`).
  3. `GET /api/tools/histograms/A` → documento completo (8 métricas, `resampled` 300-pt, `phases`, `z_mean`/`scores`/`detections`).
- **Assertions de test:** `skeleton_histograms` tiene un doc por vídeo; `signal_histograms` tiene
  la cohorte `mean`/`std` por `(trick_label, metric)`; la cohorte NO está en el doc por-vídeo.
- **Elementos FE:** botón "Analizar histogramas" + progreso del job + vista del doc.

### UC-92 — Patch forbidden field (validation/domain failure)
- **Flujo:** `PATCH /api/tools/histograms/A` con `{"metrics": {...}}` (o cualquier campo distinto de `phases`).
- **Assertions de test:** `422` `{"detail": ...}` y el documento NO cambia.
- **Elementos FE:** deshabilitar edición de campos derivados.

### UC-93 — GET / PATCH a missing video (not-found)
- **Flujo:** `GET` o `PATCH /api/tools/histograms/X` sin documento.
- **Assertions de test:** `404` `{"detail": "histogram not found"}`; no se crea documento.
- **Elementos FE:** estado vacío "sin histograma" + CTA a ejecutar análisis.

### UC-94 — One video errors — job is NOT cancelled (resilience / error isolation)
- **Precondiciones:** clips `A` (válido) y `C` (sin `phase_frames` o landmarks corruptos).
- **Flujo:** `POST /api/tools/histograms/analysis` `{video_ids: ["A","C"]}`.
- **Assertions de test:** `202`; job termina `done` (NO `failed`);
  `result_json.processed == ["A"]` y `skipped`/`failed` incluye `C` con motivo; la `description`
  del job resume "Processed N, Skipped M, Failed K".
- **Elementos FE:** errores por vídeo en el detalle del job.

### UC-95 — Summary happy path (returns stored summary)
- **Precondiciones:** vídeo `A` con doc `skeleton_histograms` cuyo job de `analysis` ya
  persistió `z_mean`/`scores`/`detections` (con `frame`/`frame_image_path`, `critical_*` opcional).
- **Flujo:** `GET /api/tools/histograms/summary/A`.
- **Assertions de test:** `200` con los valores **almacenados sin recalcular**; `skeleton_histograms`
  y `signal_histograms` NO cambian (read-only e idempotente: GETs repetidos idénticos).
- **Elementos FE:** tab Summary (scores por métrica + frames detectados).

### UC-96 — No summary stored (analysis not run)
- **Precondiciones:** vídeo `A` con doc `skeleton_histograms` pero sin los campos de resumen
  (el análisis nunca corrió sobre el vídeo, o corrió antes de la actualización que escribe el resumen).
- **Flujo:** `GET /api/tools/histograms/summary/A`.
- **Assertions de test:** `404` `{"detail": "summary not available for 'A'; run histograms/analysis first"}`;
  no hay recompute ni extracción de frames.
- **Elementos FE:** estado "sin resumen" + CTA a ejecutar análisis.

### UC-97 — Missing histogram (unknown video)
- **Flujo:** `GET /api/tools/histograms/summary/X` sin doc de histograma.
- **Assertions de test:** `404` `{"detail": "histogram not found"}`.
- **Elementos FE:** estado vacío "sin histograma".

### UC-98 — Read-only + detection semantics (no recompute; stored detections honor |z|>1)
- **Flujo:** `GET /api/tools/histograms/summary/A` dos veces seguidas; comparar respuestas.
- **Assertions de test:** ambas respuestas idénticas; `detections` respeta la regla
  `|z| > 1` (definida en la Fase 11) y cada detección tiene `frame` + `frame_image_path`.
- **Elementos FE:** cacheable; sin estado de "recargar".

---

## 10. Casos de uso — Jobs

### UC-70 — Polling de un job
- **Flujo:**
  1. Lanzar cualquier job (crawl/cut/process/retrain/upload/delete/clip/create/histogram_analysis).
  2. `GET /{slice}/jobs/{id}` en bucle.
- **Assertions de test:** `pending`/`running` con `progress`; al final `done`, `failed` o `stopped`; `error`/`description` describe el resultado (los jobs por lotes reportan `Completed N, Skipped N, Failed N` con motivos por elemento).
- **Elementos FE:** componente de progreso reusable.

### UC-72 — Cancelar (Stop) un job con rollback
- **Flujo:**
  1. `POST /{slice}/jobs/{id}/cancel` sobre un job `pending|running` → marca `cancel_requested` (202).
  2. El worker para entre elementos y **revierte** los efectos ya hechos según el tipo: windows (`process`), embeddings (`embed`), flags de training/clip (`promote`/`clip`), clase creada (`create`), clips creados (`cut`), descargas (`crawl`), uploads (`upload`), histogramas/cohorte parciales (`histogram_analysis`). Los ficheros ya borrados por un job de borrado no se restauran (se reportan como irreversibles).
  3. El job termina en `stopped` con la descripción de lo revertido.
- **Assertions de test:** `202`; job ya `done`/inexistente → `409`/`404`; tras cancelar, estado `stopped` y efectos revertidos.
- **Elementos FE:** botón **Stop** (con confirmación) en las tarjetas de jobs activos de System Jobs.

### UC-71 — Job inexistente
- **Flujo:** `GET /{slice}/jobs/{id}` con id no válido.
- **Assertions de test:** `404`.
- **Elementos FE:** —.

---

## 11. Flujo end-to-end

### UC-80 — Workflow B completo (crawl → modelo)
1. `POST /api/training/classes`
2. `POST /api/crawler/classes/{id}/crawl`
3. `GET /api/crawler/classes/{id}/posts` + `POST /api/crawler/posts/{id}/qc` (aceptar ≥1)
4. `POST /api/video/classes/{id}/cut`
5. `GET /api/video/classes/{id}/clips` + `POST /api/video/clips/{id}/accept` (≥1)
6. `POST /api/training/classes/{id}/process` + `POST /api/training/classes/{id}/embed` `{video_ids}`
7. `GET /api/training/classes/{id}/stats` (readiness)
8. `POST /api/training/classes/{id}/train` `{classes}`
9. `GET /api/training/models/{run_id}` + `POST /api/training/models/{run_id}/approve` → run `active`

- **Assertions de test:** test E2E que recorre la secuencia completa verificando los datos en Mongo/Chroma al final.
- **Elementos FE:** wizard/stepper del pipeline que refleja la etapa de la clase en cada paso.

### UC-81 — Workflow A completo (upload → datos listos)
1. `POST /api/training/classes`
2. `POST /api/video/classes/{id}/videos` (upload, auto-embed; el job auto-verifica)
3. `GET /api/training/classes/{id}/stats` → readiness (auto-embed ya metió datos)

---

## 12. Matriz de cobertura (endpoint → use case)

| Endpoint | UC |
|---|---|
| POST `/api/training/classes` | UC-01, UC-80, UC-81 |
| POST `/api/training/classes/jobs` | UC-01 |
| GET `/api/training/classes` | UC-02 |
| GET `/api/training/classes/{id}` | UC-03, UC-62, UC-80 |
| GET `/api/training/classes/{id}/stats` | UC-04, UC-80, UC-81 |
| PATCH `/api/training/classes/{id}` | UC-05 |
| DELETE `/api/training/classes/{id}` | UC-06 |
| POST `/api/training/classes/{id}/process` | UC-40, UC-41, UC-42, UC-80 |
| POST `/api/training/classes/{id}/embed` | UC-40, UC-41, UC-80 |
| POST `/api/training/classes/{id}/promote` | UC-43, UC-80 |
| POST `/api/training/classes/{id}/clip` | UC-43 |
| POST `/api/training/classes/{id}/train` | UC-60, UC-63, UC-80 |
| POST `/api/training/classes/{id}/retrain` | UC-61, UC-63, UC-64 |
| GET `/api/training/models` | UC-50 |
| GET `/api/training/models/active` | UC-51, UC-60 |
| GET `/api/training/models/{run_id}` | UC-52, UC-62, UC-80 |
| POST `/api/training/models/{run_id}/activate` | UC-53 |
| POST `/api/training/models/{run_id}/approve` | UC-62, UC-80 |
| POST `/api/training/models/{run_id}/reject` | UC-54 |
| GET `/api/training/jobs/{id}` | UC-70, UC-71 |
| POST `/api/training/jobs/{id}/cancel` | UC-72 |
| POST `/api/crawler/classes/{id}/crawl` | UC-20, UC-24, UC-80 |
| GET `/api/crawler/classes/{id}/crawls` | UC-21 |
| GET `/api/crawler/classes/{id}/posts` | UC-22, UC-80 |
| POST `/api/crawler/posts/{id}/qc` | UC-23, UC-80 |
| GET `/api/crawler/jobs/{id}` | UC-70, UC-71 |
| POST `/api/crawler/jobs/{id}/cancel` | UC-72 |
| POST `/api/video/classes/{id}/videos` | UC-10, UC-12, UC-81 |
| GET `/api/video/classes/{id}/uploads` | UC-10, UC-11 |
| POST `/api/video/classes/{id}/cut` | UC-30, UC-35, UC-80 |
| GET `/api/video/classes/{id}/clips` | UC-31, UC-80 |
| GET `/api/video/clips/{id}/video` | UC-32 |
| POST `/api/video/clips/{id}/accept` | UC-33, UC-80 |
| POST `/api/video/clips/{id}/discard` | UC-34 |
| GET `/api/video/jobs/{id}` | UC-70, UC-71 |
| POST `/api/video/jobs/{id}/cancel` | UC-72 |
| POST `/api/video/videos/delete` | UC-70 (borrado en lote) |
| DELETE `/api/video/videos/{id}` (borrado individual) | — |
| POST `/api/tools/histograms/analysis` | UC-91, UC-94, UC-70 |
| GET `/api/tools/histograms/{video_id}` | UC-91, UC-93 |
| PATCH `/api/tools/histograms/{video_id}` | UC-92, UC-93 |
| GET `/api/tools/histograms/summary/{video_id}` | UC-95, UC-96, UC-97, UC-98 |
| GET `/api/tools/jobs/{id}` | UC-91, UC-70, UC-71 |
| POST `/api/tools/jobs/{id}/cancel` | UC-72 |
| GET `/api/tools/health` | — |

---

## 13. Touchpoints cross-slice (resueltos)

Las clases son **stateless**: no hay transiciones de estado que un slice tenga que disparar. La
coordinación entre slices ocurre vía la colección compartida `videos` y los jobs:

- Crawl `done` → `videos` con `source="crawler"`; training los recupera por id cuando los necesita.
- Cut `done` → clips creados; `ClipService.accept` registra en `videos` (`kind=clip`, `clip`, `source="cut"`).
- Upload auto-embed `done` → `videos` con `source="upload"` + windows en `skeleton_data`; el propio job auto-verifica el upload.
- Process/Embed `done` → windows `processed` / `embedding_models` anotado (interno al slice training).
- Histogram analysis `done` → doc por-vídeo en `skeleton_histograms` + cohorte `signal_histograms`
  (un doc por `(trick_label, metric)`), consumidos por `GET/PATCH /api/tools/histograms/{video_id}`.
- Retrain `done` → run `done` (no activo) hasta el gate humano: `approve` → run `active`.

### Desacoplamiento slice ↔ slice (completado)

Todos los slices escriben la colección compartida `videos` (crawler `source="crawler"`, video
`source="cut"`, upload `source="upload"`). Los assets compartidos viven en `core/`:
`core/repositories/video_repository.py` y `core/services/embed_runner.py`. Los tests
`test_*_does_not_import_training` verifican el desacoplamiento.
