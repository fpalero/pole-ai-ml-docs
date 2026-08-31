# `pola_api` — Guía de test E2E: Train (modelo desde 0) + Retrain (fine-tune)

Documento dirigido al **equipo de backend (FastAPI)**. Describe, paso a paso y con comandos
reales (`curl` / `mongosh` / `pixi`), el test end-to-end que valida el ciclo completo de
entrenamiento:

1. Crear un **clasificador desde cero** (`train`, full) con los trucos `handspring` y `shouldermount`.
2. **Re-entrenar** (`retrain`, fine-tune) añadiendo una **clase nueva** (`invert`), generando sus
   clips con el `video_cutter` en modo **chroma-only**.

Incluye la **limpieza previa de MongoDB y ChromaDB** (y de vídeos/artefactos) para partir de un
entorno reproducible.

> **Modelo de estados (2026-08-05):**
> - `POST /api/training/classes/{id}/train` → modelo NUEVO (full).
> - `POST /api/training/classes/{id}/retrain` → fine-tune (requiere `base_model`).
> - No existe `chroma_only` como estado de clase ni estados de clase (stateless). El modo chroma-only
>   es un parámetro del endpoint de cut (`chroma_only: true`). La preparación para entrenar se mide
>   por datos (`windows_embedded >= min_windows` en `stats`).
> - Referencia completa: `docs/app/pola_api/slices.md` y `docs/app/pola_api/flows.md`.
> - Guía de FE equivalente: `docs/app/pole_fe/fe_train_retrain_test_guide.md`.

---

## 0. Limpieza del entorno (MongoDB + ChromaDB + vídeos)

Ejecutar **antes de cada test**.

### 0.1 MongoDB

Dos bases de datos:
- **`pola_api`** — `classes`, `videos`, `crawls`, `uploads`, `clips`, `jobs`, `model_runs`.
- **`skeleton_data`** — `skeleton_windows`, `training_runs`, `processing_errors`.

```bash
mongosh 'mongodb://admin:password@localhost:27017/?authSource=admin' --eval '
const app = db.getSiblingDB("pola_api");
["classes","videos","crawls","uploads","clips","jobs","model_runs"].forEach(c => app[c].deleteMany({}));
const ml = db.getSiblingDB("skeleton_data");
["skeleton_windows","training_runs","processing_errors"].forEach(c => ml[c].deleteMany({}));
'
```

### 0.2 ChromaDB

Persiste en `app/pola_api/FeaturesEmbeddings/` (`CHROMA_PERSIST_DIR`).

```bash
rm -rf app/pola_api/FeaturesEmbeddings
```

> Si el API está corriendo, reiniciarlo tras borrar.

### 0.3 Vídeos y artefactos en disco

| Path | Qué es | ¿Borrar? | Comando |
|---|---|---|---|
| `app/pola_api/uploads/` | Vídeos subidos | Sí | `rm -rf app/pola_api/uploads` |
| `app/pola_api/curated/` | Clips del cut | Sí | `rm -rf app/pola_api/curated` |
| `app/pola_api/downloads/` | Vídeos del crawler | Sí | `rm -rf app/pola_api/downloads` |
| `packages/pole-train-model/models/runs/*` | Runs de entrenamiento | Sí (historial) | `rm -rf packages/pole-train-model/models/runs/*` |
| `models/lstm_model_normal_final.keras` + `_encoder.pkl` | Modelo base de referencia | **No** | Backup antes de re-entrenar |
| `packages/pole-train-model/sources/videos/*` | Dataset fuente | **No** | — |
| `packages/pole-crawler/ci/downloads/` | Vídeos ya descargados (350) | **No** | — |

**Backup del modelo activo:**

```bash
BK="backups/model_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BK"
cp packages/pole-train-model/models/lstm_model_normal_final.keras "$BK/"
cp packages/pole-train-model/models/lstm_model_normal_encoder.pkl "$BK/"
```

---

## 1. Preparación del entorno

1. MongoDB arriba (contenedor `pole-mongodb` o `docker compose up -d` en `app/pola_api/`).
2. Sesión de Instagram (solo para el paso de crawl):

```bash
export INSTAGRAM_USERNAME=adeveloper266
export INSTAGRAM_CSRFTOKEN='...' INSTAGRAM_SESSIONID='...' \
       INSTAGRAM_DS_USER_ID='...' INSTAGRAM_IG_DID='...'
export SESSION_FILE_PATH="$PWD/app/pola_api/session-adeveloper266"
pixi run make-session
```

3. Arrancar el API:

```bash
export MONGODB_URI='mongodb://admin:password@localhost:27017/?authSource=admin'
pixi run api    # uvicorn main:app --reload --host 0.0.0.0 --port 8000 (cwd app/pola_api)
```

4. Verificar:

```bash
curl -s http://localhost:8000/health   # {"status":"ok"}
```

---

## 2. Test — Clasificador desde 0 (train full)

Vídeos fuente: `packages/pole-train-model/sources/videos/handspring/` (21) y
`.../shouldermount/` (25).

### 2.1 Crear clases

```bash
BASE=http://localhost:8000/api
curl -s -X POST $BASE/training/classes -H 'Content-Type: application/json' \
  -d '{"name":"handspring","hashtags":["#handspring","#handspring_pole"],"min_windows":100}'
# 201 {_id: <handspring_id>, status: draft}
curl -s -X POST $BASE/training/classes -H 'Content-Type: application/json' \
  -d '{"name":"shouldermount","hashtags":["#shouldermount"],"min_windows":100}'
# 201 {_id: <shouldermount_id>, status: draft}
```

> `transition` está reservado (clase especial del modelo) y no puede crearse por API.

### 2.2 Batch upload (Workflow A — auto-embed)

```bash
cd packages/pole-train-model/sources/videos/handspring
args=(); for f in *.mp4; do args+=(-F "files=@$f"); done
curl -s -X POST $BASE/video/classes/<handspring_id>/videos "${args[@]}"
# 202 {job_id, uploads[]}
```

Repetir para `shouldermount` (`.../sources/videos/shouldermount`).

### 2.3 Polling del job de upload

```bash
curl -s $BASE/video/jobs/<job_id>   # running 0.xx → done
# done: {windows: 44, embedded: true, videos: 21}   (handspring)
```

### 2.4 Verify → datos listos

```bash
UP=$(curl -s $BASE/video/classes/<handspring_id>/uploads | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['_id'])")
curl -s -X POST $BASE/video/classes/<handspring_id>/uploads/$UP/verify \
  -H 'Content-Type: application/json' -d '{"accepted":true}'
# {"status":"verified", "video_id": "..."}
```

Repetir para `shouldermount`.

### 2.5 Stats (readiness)

```bash
curl -s $BASE/training/classes/<handspring_id>/stats
# samples_info.windows_embedded >= min_windows → readiness true
```

### 2.6 Train full

```bash
curl -s -X POST $BASE/training/classes/<handspring_id>/train \
  -H 'Content-Type: application/json' \
  -d '{"classes":["handspring","shouldermount"]}'
# 202 {job_id, run_id: "YYYYMMDD_HHMMSS"}
```

Polling:

```bash
curl -s $BASE/training/jobs/<job_id>   # running 0.3 → done
```

- Run `done` (no activo).
- Ficheros en `packages/pole-train-model/models/runs/<run_id>/`:
  `lstm_model_normal.keras`, `lstm_model_normal_encoder.pkl`, `metadata.json`.

### 2.7 Approve

```bash
curl -s -X POST $BASE/training/models/<run_id>/approve
# {"status":"active", ...}
curl -s $BASE/training/models/active    # run full, classes: [handspring, shouldermount]
```

**Resultado esperado:** modelo full activo, encoder `['handspring', 'shouldermount']`.

---

## 3. Test — Re-entrenar (retrain fine-tune) con clase nueva `invert`

Vídeos fuente nuevos: `packages/pole-crawler/ci/downloads/inverts/pdstraddleinvert/*.mp4` (94).

### 3.1 Crear clase + upload

```bash
curl -s -X POST $BASE/training/classes -H 'Content-Type: application/json' \
  -d '{"name":"invert","hashtags":["#invert"],"min_windows":50}'
# 201 {_id: <invert_id>}

cd packages/pole-crawler/ci/downloads/inverts/pdstraddleinvert
args=(); for f in $(ls *.mp4 | head -8); do args+=(-F "files=@$f"); done
curl -s -X POST $BASE/video/classes/<invert_id>/videos "${args[@]}"   # 202
# poll $BASE/video/jobs/<job_id> → done (windows ≈ 175)
# verify → datos listos (auto-embed ya metió ventanas+embeddings)
```

### 3.2 Crawl real (Instagram) para generar posts nuevos

```bash
curl -s -X POST $BASE/crawler/classes/<invert_id>/crawl \
  -H 'Content-Type: application/json' \
  -d '{"tags":["pdstraddleinvert"],"limit":3,"min_wait":0,"max_wait":0}'
# 202 {job_id}
# poll $BASE/crawler/jobs/<job_id> → done {downloaded:3}
# posts pending (el QC las acepta)
```

> Si Instagram responde `429` (rate-limit), esperar ~10 min o usar los vídeos ya descargados.

### 3.3 QC + Cut en modo chroma-only

```bash
POST_ID=$(curl -s $BASE/crawler/classes/<invert_id>/posts | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['_id'])")
curl -s -X POST $BASE/crawler/posts/$POST_ID/qc \
  -H 'Content-Type: application/json' -d '{"status":"accepted"}'
# qc_status: accepted, can_process: true

curl -s -X POST $BASE/video/classes/<invert_id>/cut \
  -H 'Content-Type: application/json' \
  -d "{\"sources\":[{\"kind\":\"post\",\"ref\":\"$POST_ID\"}],\"chroma_only\":true}"
# 202 {job_id}
# poll $BASE/video/jobs/<job_id> → done {clips:1}
# clip en app/pola_api/curated/invert/
```

### 3.4 Review + Process

```bash
CLIP_ID=$(curl -s $BASE/video/classes/<invert_id>/clips | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['_id'])")
curl -s -X POST $BASE/video/clips/$CLIP_ID/accept \
  -H 'Content-Type: application/json' -d '{"label":"invert"}'
# clip accepted; registra video kind=clip, can_process=true

VIDEO_ID=$(curl -s $BASE/training/classes/<invert_id>/videos | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['_id'])")

curl -s -X POST $BASE/training/classes/<invert_id>/process \
  -H 'Content-Type: application/json' -d "{\"video_ids\":[\"$VIDEO_ID\"],\"stride\":5}"
# 202 {job_id}; poll $BASE/training/jobs/<job_id> → done {windows:25}

curl -s -X POST $BASE/training/classes/<invert_id>/embed \
  -H 'Content-Type: application/json' -d "{\"video_ids\":[\"$VIDEO_ID\"]}"
# 202 {job_id}; embede ventanas a ChromaDB → done {embedded:25}
# total invert ≈ 200 windows listas para entrenar
```

### 3.5 Retrain (fine-tune)

```bash
curl -s -X POST $BASE/training/classes/<invert_id>/retrain \
  -H 'Content-Type: application/json' \
  -d '{"classes":["invert"],"base_model":"<run_id_full>"}'
# 202 {job_id, run_id}
# poll $BASE/training/jobs/<job_id> → done
# usa solo ventanas no entrenadas (training_runs vacío); encoder combinado base+invert
```

Verificar encoder del run nuevo:

```bash
pixi run python -c "
import pickle
with open('packages/pole-train-model/models/runs/<run_id>/lstm_model_normal_encoder.pkl','rb') as f:
    print([str(c) for c in pickle.load(f).classes_])
"
# ['handspring', 'shouldermount', 'invert']
```

### 3.6 Approve

```bash
curl -s -X POST $BASE/training/models/<run_id>/approve   # run active
curl -s $BASE/training/models/active                      # run fine-tune, 3 clases
```

---

## 4. Validación final

| Check | Comando | Esperado |
|---|---|---|
| Clases listadas | `curl -s $BASE/training/classes` | handspring, shouldermount, invert |
| Modelo activo | `curl -s $BASE/training/models/active` | run fine-tune, 3 clases |
| Encoder | leer `.../runs/<run_id>/lstm_model_normal_encoder.pkl` | 3 clases |
| Windows entrenadas | `mongosh ... skeleton_data.skeleton_windows` (`training_status:trained`) | 44+46+200 |
| Clips | `ls app/pola_api/curated/invert/` | ≥1 clip aceptado |

---

## 5. Notas de backend (bugs corregidos durante el test)

1. **`int64 is not JSON serializable`** en el job de train: `model_trainer._save_training_metadata`
   guardaba numpy (`best_epoch`, `final_*_accuracy`) con `json.dump`. Corregido serializando a
   `float()` / `int()` nativos.
2. **Cut fallaba por el pose model**: `VideoCutter` construía `SkeletonExtractor()` con el default
   `models/pose_landmarker_heavy.task` relativo al cwd. Como la API corre desde `app/pola_api`,
   no lo encontraba. Corregido: `VideoCutter` acepta `pose_model_path` (absoluto) y
   `cutter_service` pasa `settings.pose_model_path`.
3. **Fine-tune guardaba encoder con solo las clases base**: `y` se codificaba solo con las clases
   nuevas y el encoder persistido era el base (2 clases) mientras el modelo tenía 3 salidas.
   Corregido: encoder combinado (`base_classes + new_classes`) alineado con las salidas del head.
4. **Migración de tracking**: `pixi run migrate-windows` aplica `backfill_tracking_fields`
   (añade `training_runs`/`selected_for_training` y migra `last_training_run: str` → lista).

---

## 6. Limpieza post-test (opcional)

Para dejar el entorno como estaba antes del test:

```bash
# Data de la app + ML
mongosh 'mongodb://admin:password@localhost:27017/?authSource=admin' --eval '
const app = db.getSiblingDB("pola_api");
["classes","videos","crawls","uploads","clips","jobs","model_runs"].forEach(c => app[c].deleteMany({}));
const ml = db.getSiblingDB("skeleton_data");
["skeleton_windows","training_runs","processing_errors"].forEach(c => ml[c].deleteMany({}));
'
rm -rf app/pola_api/FeaturesEmbeddings app/pola_api/uploads app/pola_api/curated app/pola_api/downloads
rm -rf packages/pole-train-model/models/runs/*
```
