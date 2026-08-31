# `pole_fe` — Guía de test E2E: Train (modelo desde 0) + Retrain (fine-tune)

Documento dirigido al **equipo de frontend (Angular)**. Describe, paso a paso y pensado para
ejecutarse desde la UI, el test end-to-end que valida el ciclo completo de entrenamiento del
backend `pola_api`:

1. Crear un **clasificador desde cero** (`train`, full) con los trucos `handspring` y `shouldermount`.
2. **Re-entrenar** (`retrain`, fine-tune) añadiendo una **clase nueva** (`invert`), generando sus
   clips con el `video_cutter` en modo **chroma-only**.

Incluye la **limpieza previa de MongoDB y ChromaDB** (y de vídeos/artefactos) para que cada
ejecución parta de un entorno limpio y reproducible.

> **Endpoints actualizados (2026-08-05):**
> - `POST /api/training/classes/{id}/train` → modelo NUEVO (full).
> - `POST /api/training/classes/{id}/retrain` → fine-tune de un modelo existente (requiere `base_model`).
> - No existen estados de clase (stateless): ni `chroma_only` ni `awaiting_training`. El modo
>   chroma-only es un **parámetro del endpoint de cut** (`chroma_only: true`); la preparación para
>   entrenar se mide por datos (`windows_embedded >= min_windows`).
> - Referencia: `docs/app/pola_api/slices.md` y `docs/app/pola_api/flows.md`.

---

## 0. Limpieza del entorno (MongoDB + ChromaDB + vídeos)

Ejecutar **antes de cada test** para partir de un estado reproducible.

### 0.1 MongoDB

Dos bases de datos implicadas:

- **`pola_api`** — datos de la app: `classes`, `videos`, `crawls`, `uploads`, `clips`, `jobs`, `model_runs`.
- **`skeleton_data`** — ventanas del ML: `skeleton_windows`, `training_runs`, `processing_errors`.

Limpiar con `mongosh`:

```js
// DB de la app
const app = db.getSiblingDB("pola_api");
["classes", "videos", "crawls", "uploads", "clips", "jobs", "model_runs"].forEach(
  c => app[c].deleteMany({})
);

// DB de ventanas/embeddings del ML
const ml = db.getSiblingDB("skeleton_data");
["skeleton_windows", "training_runs", "processing_errors"].forEach(
  c => ml[c].deleteMany({})
);
```

> **Nota:** `downloads/`, `uploads/` y `curated/` están en `.gitignore`; la limpieza de Mongo no
> borra los ficheros en disco.

### 0.2 ChromaDB

Chroma persiste en `app/pola_api/FeaturesEmbeddings/` (config `CHROMA_PERSIST_DIR`). Borrar el
directorio para resetear la colección `movement_embeddings`:

```bash
rm -rf app/pola_api/FeaturesEmbeddings
```

> Si el API está corriendo, reiniciarlo tras borrar (evita estado obsoleto en memoria).

### 0.3 Vídeos y artefactos en disco

| Path | Qué es | ¿Borrar? |
|---|---|---|
| `app/pola_api/uploads/` | Vídeos subidos por el endpoint de upload | **Sí** — `rm -rf app/pola_api/uploads` |
| `app/pola_api/curated/` | Clips generados por el endpoint de cut | **Sí** — `rm -rf app/pola_api/curated` |
| `app/pola_api/downloads/` | Vídeos descargados por el crawler (api) | **Sí** — `rm -rf app/pola_api/downloads` |
| `packages/pole-train-model/models/runs/*` | Runs de entrenamiento (`*.keras`, encoders, `active.json`) | **Sí** (si se quiere partir sin historial) |
| `packages/pole-train-model/models/lstm_model_normal_final.keras` + `_encoder.pkl` | Modelo base de referencia | **No** — es el modelo existente funcional; guardar backup antes de re-entrenar |
| `packages/pole-train-model/sources/videos/{handspring,shouldermount,transition}/` | Dataset fuente original | **No** — es el dataset de entrada |
| `packages/pole-crawler/ci/downloads/` | Vídeos ya descargados (350, p.ej. `inverts`) | **No** — fuente para el re-entrenamiento |

**Backup del modelo activo** (antes de entrenar un modelo nuevo):

```bash
cp packages/pole-train-model/models/lstm_model_normal_final.keras backups/model_backup_$(date +%Y%m%d_%H%M%S)/
cp packages/pole-train-model/models/lstm_model_normal_encoder.pkl backups/model_backup_$(date +%Y%m%d_%H%M%S)/
```

---

## 1. Preparación del entorno

1. Asegurar MongoDB corriendo (`docker compose up -d` en `app/pola_api/` o contenedor existente).
2. Arrancar el backend: `pixi run api` (uvicorn en `http://0.0.0.0:8000`).
   - Requiere `MONGODB_URI` y, para el paso de crawl, sesión de Instagram
     (`make-session` + env vars).
3. Verificar: `GET /health` → `{"status":"ok"}`.

---

## 2. Test — Clasificador desde 0 (train full)

Objetivo: con `handspring` + `shouldermount` (de `packages/pole-train-model/sources/videos`),
crear un modelo LSTM nuevo.

### 2.1 Desde el FE (Tricks Registry)

1. **NEW TRICK** → crear `handspring` → `POST /api/training/classes` → 201 (draft).
2. **ADD VIDEOS → Upload** → seleccionar los `.mp4` de `sources/videos/handspring/` (21 vídeos)
   → `POST /api/video/classes/{id}/videos` (multipart) → `202 {job_id, uploads[]}`.
3. Polling de progreso: `GET /api/video/jobs/{job_id}` → `done`.
   - Auto-embed crea ventanas (MediaPipe) + embeddings (Chroma).
4. **Verify upload** → `POST /api/video/classes/{id}/uploads/{uid}/verify {accepted:true}`
   → datos listos para entrenar (ventanas + embeddings ya creados por el auto-embed).
5. Repetir 1–4 para `shouldermount` (25 vídeos de `sources/videos/shouldermount/`).
6. **Stats tab** → `GET /api/training/classes/{id}/stats` → `readiness` (windows_embedded ≥ min_windows).

### 2.2 Desde el FE (Training Studio)

7. Modo **Train from Scratch** → nombre del modelo.
8. Seleccionar `handspring` + `shouldermount` (TargetClassesSelector, min 2).
9. Opciones: `reembed: true`, `use_augmentation` opcional.
10. **START TRAINING** → `POST /api/training/classes/{first_class_id}/train {classes:["handspring","shouldermount"]}`
    → `202 {job_id, run_id}`.
11. Polling: `GET /api/training/jobs/{job_id}` → `done` (run `status=done`, NO activo).
    - Ficheros en `models/runs/<run_id>/`: `lstm_model_normal.keras`, `_encoder.pkl`, `metadata.json`.

### 2.3 Desde el FE (Model Registry)

12. Ver el run en ExecutionLogTable → `GET /api/training/models/{run_id}` (métricas).
13. **Approve & Activate** → `POST /api/training/models/{run_id}/approve` → run `active`.
14. ActiveModelBanner muestra el run; `GET /api/training/models/active` devuelve el run (2 clases).

**Resultado esperado:** modelo full activo con encoder `['handspring', 'shouldermount']`.

---

## 3. Test — Re-entrenar (retrain fine-tune) con clase nueva `invert`

Objetivo: añadir `invert` (truco nuevo) al clasificador, generando sus clips con el cutter en
modo **chroma-only** y re-entrenando el modelo existente.

### 3.1 Desde el FE (Tricks Registry)

1. **NEW TRICK** → crear `invert` → `POST /api/training/classes` → 201 (draft).
2. **ADD VIDEOS → Upload** → seleccionar un subconjunto de vídeos de
   `packages/pole-crawler/ci/downloads/inverts/pdstraddleinvert/*.mp4` (p.ej. 8)
   → `202 {job_id, uploads[]}` → poll job → `done` (ventanas embebidas).
3. **Verify upload** → datos listos para entrenar (ventanas embebidas).

### 3.2 Obtener vídeos nuevos para `invert` (crawler real de Instagram)

> Alternativa: usar los ya descargados en `ci/downloads/inverts/`. El crawl real genera posts
> nuevos en `app/pola_api/downloads/`.

4. **Scrape** → `POST /api/crawler/classes/{invert_id}/crawl {tags:["pdstraddleinvert"], limit:3}`
   → `202 {job_id}` → poll `GET /api/crawler/jobs/{job_id}` → `done` (3 posts).
   - Posts con `qc_status=pending`.
5. **QC** → aceptar ≥1 post → `POST /api/crawler/posts/{post_id}/qc {status:"accepted"}`.

### 3.3 Cortar clips en modo chroma-only (video_cutter)

6. **Crop AI** → `POST /api/video/classes/{invert_id}/cut`
   `{sources:[{kind:"post", ref: post_id}], chroma_only: true}`
   → `202 {job_id}`.
   - El cutter usa **solo ChromaDB** (sin LSTM) porque `invert` aún no está en el modelo.
7. Poll `GET /api/video/jobs/{job_id}` → `done` (clips creados en `curated/invert/`).
8. **Review clips** (VideoEditorModal) → **Accept** → `POST /api/video/clips/{clip_id}/accept {label:"invert"}`
   → crea vídeo entrenable `kind=clip`.
9. **Process** → en el bulk bar, click **Process** → el **Process Config modal** pide **Slides (stride)** (entero 1–30, default 5) → `POST /api/training/classes/{invert_id}/process {video_ids:[...], stride}` → `202` → poll → `done`
   (windows del clip en Mongo). Después **Embed** → `POST /api/training/classes/{invert_id}/embed {video_ids:[...]}`
   → embeddings en Chroma.
   - Total windows `invert` ≈ 200 listas para entrenar.

### 3.4 Re-entrenar (fine-tune) desde el FE (Training Studio)

10. Modo **Fine-tune Existing** → Base Model dropdown:
    `GET /api/training/models?status=done` → elegir el run full del paso 2 (o el activo).
11. Seleccionar la clase `invert` (TargetClassesSelector).
12. **START TRAINING** → `POST /api/training/classes/{invert_id}/retrain`
    `{classes:["invert"], base_model:"<run_id full>"}` → `202 {job_id, run_id}`.
    - Usa **solo ventanas no entrenadas** (`training_runs` vacío) de `invert` + encoder combinado
      (base + nuevas clases).
13. Poll `GET /api/training/jobs/{job_id}` → `done`.
    - Encoder del run: `['handspring','shouldermount','invert']` (3 clases).
    - Modelo activo sigue siendo el anterior (run `done`, no activo).

### 3.5 Aprobar (Model Registry)

14. **Approve & Activate** → `POST /api/training/models/{run_id}/approve` → run `active`.
15. `GET /api/training/models/active` → run fine-tune (3 clases).

**Resultado esperado:** modelo activo con 3 clases (`handspring`, `shouldermount`, `invert`).

---

## 4. Validación final

| Check | Endpoint / Lugar | Esperado |
|---|---|---|
| Clases listadas | `GET /api/training/classes` | handspring, shouldermount, invert |
| Modelo activo | `GET /api/training/models/active` | run fine-tune, classes: 3 |
| Encoder 3 clases | `models/runs/<run_id>/lstm_model_normal_encoder.pkl` | handspring, shouldermount, invert |
| Windows entrenadas | Mongo `skeleton_data.skeleton_windows` (`training_status: trained`, `training_runs`) | 44+46+200 |
| Clips generados | `app/pola_api/curated/invert/` | ≥1 clip aceptado |

---

## 5. Notas para el FE

- **Polling de jobs:** todos los pasos asíncronos devuelven `202 {job_id}`; el FE hace polling de
  `GET /{slice}/jobs/{job_id}` (crawler | video | training) hasta `done|failed`, mostrando
  `progress` (0–1) y `error`.
- **Estados visibles por clase** (pipeline_state, derivado en FE): `upload` → `upload_verification` → `crawl` →
  `qc` → `cut` → `clip_review` → `process` → `retrain` → `approval`. Los pasos sin entidades
  pendientes se saltan.
- **Readiness / PROMOTE:** el botón PROMOTE (Tricks page) marca los vídeos seleccionados con
  `selected_for_training: true` via `PATCH /api/training/videos/{video_id}`; la
  readiness viene de `GET /api/training/classes/{id}/stats`.
- **Bugs corregidos durante el test** (relevantes para el FE):
  - El job de train fallaba con `int64 is not JSON serializable` → corregido en `model_trainer`
    (serializa métricas a int/float nativos).
  - El cut fallaba por el `pose_landmarker_heavy.task` relativo al cwd → ahora el backend pasa el
    path absoluto (`pose_model_path`); el FE no necesita hacer nada.
  - El fine-tune guardaba un encoder con solo las clases base → ahora persiste el encoder
    combinado (base + nuevas), así que `GET /api/training/models/{run_id}` reporta las 3 clases.
