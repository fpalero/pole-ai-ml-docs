# `pola_api` — API Reference (code-accurate)

Backend FastAPI de Pole AI. Organizado por slices: `crawler`, `training`, `video`, `tools` + `core` compartido.

**Base URL**: `http://0.0.0.0:8000`
**Content-Type**: `application/json` (except upload: `multipart/form-data`, clip video: `video/mp4`)
**Job pattern**: Async ops return `202 {job_id}`. FE polls `GET /{slice}/jobs/{job_id}` → `status: pending|running|done|failed`, `progress: 0.0-1.0`.

> **Modelo de estados:** las clases son **stateless**. No existe una máquina de estados de clase
> (`core/status.py` fue eliminado): la validación de cada operación se hace por operación, revisando
> las entidades relacionadas (videos, uploads, clips, windows). Ver §«Modelo de estados (clases)»
> más abajo.

---

## Modelo de estados (clases)

Las clases **no tienen campo `status`** y no hay transiciones de estado (`ALLOWED_TRANSITIONS`
eliminado en `603d2f1`). En su lugar, cada endpoint valida **qué entidades relacionadas existen**:
- `process` / `embed`: validan los `video_ids` (`clip=true`, no vacíos, de la clase).
- `train` / `retrain`: validan que las `classes` tengan windows con `selected_for_training=true`.
- `crawl`: requiere posts con `qc_status=accepted` para cortar.

La **preparación para entrenar** (antiguo `awaiting_training`) se expresa por datos, no por estado:
la clase es entrenable cuando tiene windows en `skeleton_windows` (label = clase) con
`selected_for_training=true`, y ChromaDB contiene sus embeddings (`embedding_models` no vacío).

**UI mapping** (pipeline): una clase se muestra en la etapa del pipeline según sus entidades —
`uploading`/`upload_verification` (uploads auto-verificados por el job de upload), `crawl` (crawls en curso),
`qc` (posts pendientes de QC), `cut`/`clip_review` (clips pendientes de review),
`process` (jobs de process/embed en curso), `retrain` (jobs de train/retrain en curso),
`approval` (model_runs pendientes de approve).

---

## Job Document (shared)

```json
{
    "_id": "ObjectId",
    "kind": "crawl|process|embed|promote|clip|retrain|upload|cut|delete|delete_class|create|histogram_analysis",
    "entity_id": "class_id or null",
    "slice": "crawler|training|video|tools",
    "status": "pending|running|done|failed|stopped",
    "progress": 0.65,
    "result_json": null,
    "error": null,
    "description": "Completed N, Skipped N, Failed N — ... or created <name>",
    "cancel_requested": false,
    "created_at": "2026-08-05T10:00:00Z",
    "finished_at": null
}
```

`status` **`stopped`** = el job fue cancelado (`POST /{slice}/jobs/{id}/cancel`) y revirtió su trabajo.
Los jobs por lote (`delete`, `promote`, `clip`) reportan en `result_json`:
`{"completed": [ids], "skipped": [{"video_id","reason"}], "failed": [{"video_id","reason"}]}`
y `description` con el resumen + motivos por elemento.

---

## Slice: Crawler

**Collections**: `crawls`, `videos` (shared, filtered by `source="crawler"`)

### Endpoints

---

### POST `/api/crawler/classes/{class_id}/crawl` → `202 {job_id}`

Lanza crawl de Instagram para una clase. Tags se normalizan: stripped, `#` removido, lowercase. Crea un crawl (`status` interno del job: `running`/`done`/`failed`) y descarga posts.

**Request (JSON)**:
```json
{
    "tags": ["handspring", "pole trick"],
    "limit": 10,
    "min_wait": 5,
    "max_wait": 10
}
```

`CrawlRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `tags` | `list[str]` | required | non-empty, cada tag non-empty, sin espacios |
| `limit` | `int` | `10` | `>= 1` |
| `min_wait` | `int` | `5` | `>= 0` |
| `max_wait` | `int` | `10` | `>= min_wait` |

**Response 202**:
```json
{"job_id": "64b0f1a2c3d4e5f6a7b8c9d0"}
```

**Errors**: `404` (class not found), `422` (validation)

---

### GET `/api/crawler/classes/{class_id}/crawls` → `200 list[dict]`

Historial de crawls de una clase.

**Response 200**:
```json
[
    {
        "_id": "64b...",
        "class_id": "64b...",
        "tags": ["handspring"],
        "limit": 10,
        "min_wait": 5,
        "max_wait": 10,
        "status": "done",
        "downloaded_count": 7,
        "error": null,
        "created_at": "2026-08-05T10:00:00Z",
        "finished_at": "2026-08-05T10:15:00Z"
    }
]
```

---

### GET `/api/crawler/classes/{class_id}/posts` → `200 list[dict]`

Lista posts descargados para QC. Filtrable por `qc_status`.

**Query**: `?qc_status=pending|accepted|rejected`

**Response 200**:
```json
[
    {
        "_id": "64b...",
        "class_id": "64b...",
        "local_path": "/.../downloads/handspring/vid_001.mp4",
        "kind": "video",
        "source": "crawler",
        "clip": false,
        "processed": false,
        "qc_status": "pending",
        "username": "pole_athlete",
        "timestamp": "2026-08-01",
        "caption": "New handspring!",
        "url": "https://instagram.com/p/...",
        "tag": "handspring",
        "created_at": "...",
        "updated_at": "..."
    }
]
```

---

### POST `/api/crawler/posts/{post_id}/qc` → `200 dict`

Acepta o rechaza un post. Aceptar habilita el post para el paso de corte (cut).

**Request (JSON)**:
```json
{"status": "accepted"}
```

`QcRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `status` | `str` | required | `"accepted"` o `"rejected"` |

**Response 200**: post actualizado con `qc_status: "accepted"`.

---

### GET `/api/crawler/jobs/{job_id}` → `200 dict`

Polling del job de crawl. Filtrado por `slice_name="crawler"`.

### POST `/api/crawler/jobs/{job_id}/cancel` → `202 {job_id}` **[NEW]**

Solicita la cancelación (Stop) de un job `pending|running`. El worker para entre elementos y revierte
el trabajo (descargas ya guardadas). Job ya `done`/inexistente → `409`/`404`.

---

## Slice: Training

**Collections**: `classes`, `videos` (shared), `model_runs`, `skeleton_windows` (en DB `skeleton_data`)

### Endpoints

---

### POST `/api/training/classes` → `201 dict`

Crea un nuevo trick (clase).

**Request (JSON)**:
```json
{
    "name": "handspring",
    "hashtags": ["#handspring", "#pole"],
    "min_videos": 5,
    "min_windows": 200,
    "cutter_config": {"fps": 30}
}
```

`ClassCreate` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `name` | `str` | required | `^[a-z0-9_]+$`, no reservado (`"transition"`), unique |
| `hashtags` | `list[str]` | `[]` | cada uno `^#[^\s#]+$`, deduplicados |
| `min_videos` | `int \| None` | `5` | `>= 0` |
| `min_windows` | `int \| None` | `200` | `>= 0` |
| `cutter_config` | `dict \| None` | `None` | dict arbitrario |

**Response 201**:
```json
{
    "_id": "64b...",
    "name": "handspring",
    "hashtags": ["#handspring", "#pole"],
    "min_videos": 5,
    "min_windows": 200,
    "cutter_config": {"fps": 30},
    "created_at": "2026-08-05T10:00:00Z",
    "updated_at": "2026-08-05T10:00:00Z"
}
```

### POST `/api/training/classes/jobs` → `202 {job_id}` **[NEW]**

Variante asíncrona de creación de clase: valida de forma síncrona (mismos errores 4xx) y lanza la
inserción como job `create` (slice training). **Response 202**: `{"job_id": "..."}`. El job termina
`done` con `result_json: {created, name}` y `description: "created <name>"`.

**Errors**: `409` (duplicate name), `422` (name/hashtag validation)

---

### GET `/api/training/classes` → `200 list[dict]`

Lista tricks (filtro por `name`). No hay filtro por estado de clase (clases stateless).

**Query**: `?name=handspring`

**Response 200**: array de clases.

---

### GET `/api/training/classes/{class_id}` → `200 dict`

Detalle de clase. La etapa del pipeline se deriva de las entidades relacionadas (ver §«Modelo de estados»).

**Errors**: `404`

---

### GET `/api/training/classes/{class_id}/stats` → `200 dict`

Metricas de skeleton windows y readiness. Los windows se cuentan desde la DB `skeleton_data`
(donde escribe `pole_ml`), no desde la DB de la app.

**Response 200**:
```json
{
    "class_id": "64b...",
    "label": "handspring",
    "samples_info": {
        "windows_total": 4281,
        "windows_embedded": 3402,
        "windows_pending": 879,
        "windows_trained": 0
    },
    "chroma_distribution": {},
    "readiness": false
}
```

`readiness = true` cuando `windows_embedded >= min_windows`.

---

### PATCH `/api/training/classes/{class_id}` → `200 dict`

Actualizacion parcial de clase. Solo campos enviados se modifican.

**Request (JSON)**:
```json
{
    "hashtags": ["#newtag"],
    "min_videos": 10
}
```

`ClassPatch` DTO (todos opcionales, `exclude_unset=True`):
| Campo | Tipo | Validacion |
|---|---|---|
| `name` | `str \| None` | `^[a-z0-9_]+$`, unique |
| `hashtags` | `list[str] \| None` | `^#[^\s#]+$` |
| `min_videos` | `int \| None` | `>= 0` |
| `min_windows` | `int \| None` | `>= 0` |
| `cutter_config` | `dict \| None` | dict arbitrario |

**Errors**: `404`, `409` (duplicate name)

---

### DELETE `/api/training/classes/{class_id}` → `202 {job_id}`

Elimina clase en cascada mediante un job `delete_class` (slice training): borra clips, vídeos,
ficheros físicos, windows (`skeleton_windows`), embeddings (ChromaDB) y la propia clase. El job
reporta `{class_id, clips_deleted, videos_deleted, windows_purged, embeddings_purged}`.

**Response 202**: `{"job_id": "..."}`

**Errors**: `404`

---

### POST `/api/training/classes/{class_id}/process` → `202 {job_id}`

Extrae skeleton windows de los `video_ids` indicados y las guarda en Mongo (`processed=True`). No computa embeddings (úselo `embed`). **Solo clips** (flag `clip` o `kind='clip'`) pueden procesarse.

**Request (JSON)**:
```json
{
    "video_ids": ["64b..."],
    "stride": 5
}
```

`ProcessRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `video_ids` | `string[]` | — | no vacío, videos de la clase, `clip=true` |
| `stride` | `int` | `5` | `>= 1` |

**Response 202**:
```json
{"job_id": "64b..."}
```

**Errors**: `422` (video_ids vacío/inexistentes/clase distinta/no-clip/`local_path` no existe)

---

### POST `/api/training/classes/{class_id}/embed` → `202 {job_id}`

Embe en ChromaDB las ventanas ya extraídas de los `video_ids` indicados, solo las que el `model_id` aún no ha embebido (opción A: pending/stale). Añade el modelo a `embedding_models` (video y ventanas).

**Request (JSON)**:
```json
{
    "video_ids": ["64b..."],
    "model_id": null
}
```

`EmbedRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `video_ids` | `string[]` | — | no vacío, videos de la clase, `clip=true` |
| `model_id` | `str \| None` | `None` | path a modelo embedding alternativo (se valida que exista via `Path.is_file()`) |

**Response 202**:
```json
{"job_id": "64b..."}
```

**Errors**: `409` (status invalido), `422` (no hay videos, `no-clip`, `local_path` no existe, modelo no existe)

---

### POST `/api/training/classes/{class_id}/promote` → `202 {job_id}` **[NEW]**

Marca/desmarca `selected_for_training` de un lote de videos (job `promote`, slice training). Solo los **clips** pueden marcarse para entrenamiento; seleccionar un video no-clip o sin procesar → `422`.

**Request (JSON)**:
```json
{"video_ids": ["64b..."], "selected": true}
```

**Response 202**: `{"job_id": "..."}`

---

### POST `/api/training/classes/{class_id}/clip` → `202 {job_id}` **[NEW]**

Pone/quita el flag `clip` de un lote de videos (job `clip`, slice training). `clip=true` → marca como clip; `clip=false` → pasa `kind='video'` y limpia `selected_for_training`.

**Request (JSON)**:
```json
{"video_ids": ["64b..."], "clip": true}
```

**Response 202**: `{"job_id": "..."}`

---

### POST `/api/training/classes/{class_id}/videos` → `201 dict` **[NEW — no en docs originales]**

Registra un video manual para una clase.

**Request (JSON)**:
```json
{
    "local_path": "/path/to/video.mp4",
    "clip": false,
    "kind": "video",
    "parent_id": null,
    "source": "manual"
}
```

`VideoCreate` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `local_path` | `str` | required | fichero debe existir en disco |
| `clip` | `bool` | `false` | — |
| `kind` | `str` | `"video"` | `"video"` o `"clip"` |
| `parent_id` | `str \| None` | `None` | ObjectId del video padre (si kind=clip) |
| `source` | `str` | `"manual"` | `"manual"\|"upload"\|"cut"` |

**Response 201**: documento video.

---

### GET `/api/training/classes/{class_id}/videos` → `200 list[dict]` **[NEW]**

Lista todos los videos de una clase (todas las fuentes: crawler, upload, manual, cut).

**Query**: `?processed=false&kind=video`

**Response 200**:
```json
[
    {
        "_id": "64b...",
        "class_id": "64b...",
        "local_path": "/.../videos/handspring.mp4",
        "kind": "video",
        "parent_id": null,
        "source": "upload",
        "clip": false,
        "processed": false,
        "embedding_models": [],
        "created_at": "...",
        "updated_at": "..."
    }
]
```

---

### PATCH `/api/training/videos/{video_id}` → `200 dict` **[NEW]**

Actualiza flags de un video.

**Request (JSON)**:
```json
{
    "clip": false,
    "kind": "video",
    "selected_for_training": false
}
```

`VideoPatch` DTO:
| Campo | Tipo | Validacion |
|---|---|---|
| `clip` | `bool \| None` | debe ser bool |
| `kind` | `str \| None` | `"video"` o `"clip"` |
| `selected_for_training` | `bool \| None` | `StrictBool`. Solo clips pueden seleccionarse para training |

**Propagación**: al cambiar `selected_for_training`, el flag se replica a **todas las windows** del
video en la DB `skeleton_data` (`set_selected_for_training`). Las ventanas con
`selected_for_training=false` quedan excluidas de `train` y `retrain`.

**Errors**: `409` (not found), `422` (tipos inválidos / no-clip al seleccionar para training)

---

### POST `/api/training/classes/{class_id}/train` → `202 {job_id, run_id}`

Crea un **modelo LSTM nuevo desde cero** (full). Requiere que las clases tengan windows (`selected_for_training=true`).

**Request (JSON)**:
```json
{
    "classes": ["handspring", "shouldermount"],
    "reembed": true,
    "use_augmentation": false,
    "use_class_weight": true
}
```

`TrainRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `classes` | `list[str]` | required | non-empty, cada uno non-empty string |
| `reembed` | `bool` | `true` | re-construir Chroma embeddings tras entrenar |
| `use_augmentation` | `bool` | `false` | data augmentation en entrenamiento |
| `use_class_weight` | `bool` | `true` | class weighting para clases imbalanceadas |

**Response 202**:
```json
{
    "job_id": "64b...",
    "run_id": "20260805_143000"
}
```

`run_id` formato: `YYYYMMDD_HHMMSS[-N]` (sufijo opcional si colision).

**Selección de windows**: `train` usa **todas** las windows de `classes` con
`selected_for_training=true` (aunque ya hayan entrenado en otros modelos; se construye un modelo
desde cero). Cada window usada recibe un append de `run_id` en su lista `training_runs`.

**Errors**: `409` (classes no tienen windows entrenables), `422` (classes vacias)

---

### POST `/api/training/classes/{class_id}/retrain` → `202 {job_id, run_id}`

Hace **fine-tune de un modelo existente** sobre la clase. Requiere windows entrenables
(`selected_for_training=true`) y un `base_model` (o modelo activo como fallback).

**Selección de windows**: `retrain` usa **solo las windows NO entrenadas** (con `training_runs`
vacío) y `selected_for_training=true`. Las windows ya consumidas por otros modelos no se
re-utilizan, evitando re-entrenar con los mismos datos.

**Request (JSON)**:
```json
{
    "classes": ["handspring"],
    "base_model": "20260805_120000",
    "reembed": true,
    "use_augmentation": false,
    "use_class_weight": false
}
```

`RetrainRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `classes` | `list[str]` | required | non-empty, cada uno non-empty string |
| `reembed` | `bool` | `true` | re-construir Chroma embeddings tras entrenar |
| `base_model` | `str \| None` | `None` | run_id del modelo base. Requerido para fine-tune (o usa active model como fallback) |
| `use_augmentation` | `bool` | `false` | data augmentation en entrenamiento |
| `use_class_weight` | `bool` | `true` | class weighting para clases imbalanceadas |

**Response 202**:
```json
{
    "job_id": "64b...",
    "run_id": "20260805_143000"
}
```

`run_id` formato: `YYYYMMDD_HHMMSS[-N]` (sufijo opcional si colision).

**Errors**: `409` (classes no tienen windows entrenables), `422` (classes vacias, fine-tune sin base_model)

---

### GET `/api/training/models` → `200 list[dict]`

Lista runs de entrenamiento.

**Query**: `?mode=full|fine-tune&status=running|done|failed|active|rejected`

**Response 200**:
```json
[
    {
        "_id": "64b...",
        "run_id": "20260805_143000",
        "mode": "full",
        "classes": ["handspring", "shouldermount"],
        "class_id": "64b...",
        "base_model": null,
        "status": "done",
        "active": false,
        "metrics": {
            "val_accuracy": 0.955,
            "val_loss": 0.142
        },
        "model_path": "models/runs/20260805_143000/lstm_model_normal.keras",
        "encoder_path": "models/runs/20260805_143000/lstm_model_normal_encoder.pkl",
        "metadata_path": "models/runs/20260805_143000/metadata.json",
        "window_count": 4281,
        "error": null,
        "created_at": "...",
        "updated_at": "..."
    }
]
```

---

### GET `/api/training/models/active` → `200 dict|null`

Devuelve el modelo activo (el que tiene `active=true`).

---

### GET `/api/training/models/{run_id}` → `200 dict`

Detalle de un run con metricas. `404` si no existe.

---

### POST `/api/training/models/{run_id}/activate` → `200 dict`

Activa un run manualmente (pointer). Desactiva todos los demas. Escribe `active.json` en el directorio del run.

**Errors**: `404`, `409` (run failed)

---

### POST `/api/training/models/{run_id}/approve` → `200 dict`

Gate humano: activa el run (pointer). Requiere run `status=done`.

**Errors**: `404`, `409` (run not done)

---

### POST `/api/training/models/{run_id}/reject` → `200 dict`

Rechaza run → `status: "rejected"`. No puede rechazar runs activos.

**Errors**: `404`, `409` (run is active)

---

### GET `/api/training/jobs/{job_id}` → `200 dict`

Polling de jobs de training (process/embed/promote/clip/create/delete_class). Filtrado por `slice_name="training"`.

### POST `/api/training/jobs/{job_id}/cancel` → `202 {job_id}` **[NEW]**

Solicita la cancelación (Stop) de un job `pending|running`; el worker revierte el trabajo (windows,
embeddings, flags, clase creada). Job ya `done`/inexistente → `409`/`404`.

---

## Slice: Video

**Collections**: `uploads`, `clips`, `videos` (shared)

### Endpoints

---

### POST `/api/video/classes/{class_id}/videos` → `202 {job_id, uploads[]}`

Sube videos .mp4, auto-procesa (skeleton + embeddings).

**Request**: `multipart/form-data`, campo `files` (lista de `UploadFile` .mp4)

**Response 202**:
```json
{
    "job_id": "64b...",
    "uploads": [
        {
            "_id": "64b...",
            "class_id": "64b...",
            "video_id": "64b...",
            "filename": "handspring_01.mp4",
            "local_path": "/.../uploads/handspring/uuid_handspring_01.mp4",
            "size": 5242880,
            "status": "processing"
        }
    ]
}
```

**Errors**: `409` (clase no existe), `422` (no .mp4, sin ficheros, modelo no existe)

---

### GET `/api/video/classes/{class_id}/uploads` → `200 list[dict]`

Lista uploads de una clase.

> Los uploads se **auto-verifican** en el job de upload en background
> (`pending → processing → verified | failed`); el endpoint humano de verify
> (`POST .../uploads/{upload_id}/verify`) fue eliminado.

---

### POST `/api/video/classes/{class_id}/cut` → `202 {job_id}`

Corta sources (posts/uploads/videos) en clips usando `VideoCutter`.

**Request (JSON)**:
```json
{
    "sources": [
        {"kind": "post", "ref": "64b_post_id_1"},
        {"kind": "upload", "ref": "64b_upload_id_1"},
        {"kind": "video", "ref": "64b_video_id_1"},
        {"kind": "path", "ref": "/abs/path/to/video.mp4"}
    ],
    "cutter_override": {"fps": 30},
    "model_id": null,
    "chroma_only": false
}
```

`CutRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `sources` | `list[CutSource]` | required | non-empty |
| `cutter_override` | `dict \| None` | `None` | sobreescribe cutter_config de la clase |
| `model_id` | `str \| None` | `None` | modelo de clasificacion alternativo |
| `chroma_only` | `bool` | `false` | `true` → el `VideoCutter` usa solo ChromaDB (sin LSTM). Para clases aun sin modelo entrenado |

`CutSource` DTO:
| Campo | Tipo | Validacion |
|---|---|---|
| `kind` | `"post"\|"upload"\|"video"\|"path"` | required |
| `ref` | `str` | non-empty string. post_id/upload_id/video_id/path absoluto |

Validacion especifica por kind:
- `post`: debe existir en videos con `source="crawler"` y `qc_status="accepted"`
- `upload`: debe existir en uploads con `status="verified"`
- `video`: debe existir en videos con `source="manual"`
- `path`: fichero debe existir en disco

**Response 202**:
```json
{"job_id": "64b..."}
```

**Errors**: `409` (clase no existe), `422` (sources invalidos, post no aceptado, upload no verificado)

---

### GET `/api/video/classes/{class_id}/clips` → `200 list[dict]`

Lista clips generados. Filtrable por status.

**Query**: `?status=pending|accepted|discarded`

**Response 200**:
```json
[
    {
        "_id": "64b...",
        "class_id": "64b...",
        "local_path": "/.../curated/handspring/clip_001.mp4",
        "source_kind": "post",
        "source_ref": "64b_post_id_1",
        "parent_id": "64b_video_id_1",
        "status": "pending",
        "label": null,
        "accepted_at": null,
        "created_at": "...",
        "updated_at": "..."
    }
]
```

---

### GET `/api/video/clips/{clip_id}/video` → `200 video/mp4`

Streaming del archivo de clip. `FileResponse`. `404` si clip o fichero no existe.

---

### POST `/api/video/clips/{clip_id}/accept` → `200 dict`

Acepta un clip. Crea registro de video entrenable (`kind="clip"`, `can_process=true`, `source="cut"`) en la coleccion `videos`.

**Request (JSON)**:
```json
{"label": "handspring"}
```

`AcceptRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `label` | `str \| None` | `None` | si None, usa el nombre de la clase |

**Response 200**: clip actualizado con `status: "accepted"`, `label: "handspring"`.

---

### POST `/api/video/clips/{clip_id}/discard` → `200 dict`

Descarta clip → `status: "discarded"`.

---

### GET `/api/video/jobs/{job_id}` → `200 dict`

Polling de jobs de video (upload/cut/delete). Filtrado por `slice_name="video"`.

### POST `/api/video/jobs/{job_id}/cancel` → `202 {job_id}` **[NEW]**

Solicita la cancelación (Stop) de un job `pending|running`; el worker revierte el trabajo (clips
creados, uploads). Job ya `done`/inexistente → `409`/`404`.

### POST `/api/video/videos/delete` → `202 {job_id}` **[NEW]**

Borra un lote de videos (job `delete`, slice video): fichero físico, doc Mongo, windows y
embeddings. Los videos con hijos se omiten (se reportan como `skipped`) sin detener el lote.
`DELETE /api/video/videos/{video_id}` hace lo mismo para un solo video (204).

---

## Slice: Tools

**Collections**: `skeleton_histograms` + `signal_histograms` (en DB `skeleton_data`, gestionadas por `pole_ml`)

### Endpoints

---

### POST `/api/tools/histograms/analysis` → `202 {job_id}` **[NEW]**

Lanza el análisis de histogramas de métricas de trick (8 señales M-01..M-08) en **background**
(job `histogram_analysis`, slice `tools`) sobre una lista de clips ya extraídos. Pipeline de **dos
pasadas**: (1) resamplea cada vídeo a 300 puntos (100 por fase) y agrega la **cohorte**
`mean`/`std` en `signal_histograms` (un doc por `(trick_label, metric)`, `ddof=1`); (2) contra la
cohorte actualizada calcula `z_mean`/`scores` (0-100) y `detections` (`|z| > 1`, un JPEG por punto
detectado) y los persiste en el doc por-vídeo. Aislamiento de errores: un vídeo que falla no
cancela el job — termina `done` con `processed/skipped/failed` en `result_json`.

**Request (JSON)**:
```json
{"video_ids": ["64b_video_1", "64b_video_2"]}
```

`HistogramAnalysisRequest` DTO:
| Campo | Tipo | Default | Validacion |
|---|---|---|---|
| `video_ids` | `list[str]` | required | non-empty (`min_length=1`) |

**Response 202**:
```json
{"job_id": "64b0f1a2c3d4e5f6a7b8c9d0"}
```

**Job result** (`result_json`):
```json
{
  "processed": ["64b_video_1"],
  "skipped": [{"video_id": "64b_video_2", "reason": "no phase_frames"}],
  "failed": [],
  "histograms": 8
}
```

**Errors**: `422` (video_ids vacío o ausente)

---

### GET `/api/tools/histograms/{video_id}` → `200 dict` **[NEW]**

Devuelve el documento por-vídeo completo de `skeleton_data.skeleton_histograms` (métricas
crudas + `resampled` 300-pt + `phases` + `z_mean`/`scores`/`detections` almacenados por el job de
análisis). La cohorte `mean`/`std` NO está en este doc — vive en `signal_histograms`.

**Response 200**:
```json
{
  "video_id": "64b_video_1",
  "trick_label": "handspring",
  "total_frames": 100,
  "extraction_stride": 5,
  "phases": {"init": {"start": 0, "end": 25}, "execution": {"start": 26, "end": 70}, "exit": {"start": 71, "end": 99}},
  "metrics": {"horizontal_speed": [0.0, "..."], "...": "..."},
  "resampled": {"horizontal_speed": [0.0, "..."], "...": "..."},
  "z_mean": {"horizontal_speed": 0.42, "...": "..."},
  "scores": {"horizontal_speed": 81.0, "...": "..."},
  "detections": [{"index": 152, "phase": "execution", "metric": "vertical_speed", "z_score": 2.3, "frame": 58, "frame_image_path": "/abs/.../frame_58.jpg"}],
  "generated_at": "2026-08-13T00:00:00Z"
}
```

**Errors**: `404` (`{"detail": "histogram not found"}`)

---

### PATCH `/api/tools/histograms/{video_id}` → `200 dict` **[NEW]**

Actualización **parcial de las fases** (`phases`) del documento de histograma. No recalcula arrays
derivados (re-ejecute `analysis` para refrescar `resampled`/`z_mean`/`scores`/`detections`).

**Request (JSON)**:
```json
{"phases": {"execution": {"start": 27, "end": 71}}}
```

Solo se permite el campo `phases` (subconjunto de `init`/`execution`/`exit`, cada uno `{start, end}`).

**Errors**: `422` (cualquier campo distinto de `phases`, o `phases` vacío/inválido), `404` (doc no existe)

---

### GET `/api/tools/histograms/summary/{video_id}` → `200 dict` **[NEW]**

Devuelve el **resumen por-vídeo almacenado** (Fase 12, `PLAN.md` §9): los campos
`z_mean`/`scores`/`detections` (y los opcionales `critical_*`) que el job de
`analysis` persistió en el doc `skeleton_histograms` — **verbatim**, sin
recalcular, sin job y sin extraer frames en lectura. Es **read-only** e
idempotente (GETs repetidos devuelven el mismo resumen almacenado).

**Response 200**:
```json
{
  "video_id": "64b_video_1",
  "trick_label": "handspring",
  "z_mean": {"horizontal_speed": 0.42, "...": "..."},
  "scores": {"horizontal_speed": 81.0, "...": "..."},
  "detections": [{"index": 152, "phase": "execution", "metric": "vertical_speed", "z_score": 2.3, "frame": 58, "frame_image_path": "/abs/.../frame_58.jpg"}],
  "critical_frame": 58,
  "critical_phase": "execution",
  "critical_metric": "vertical_speed"
}
```
(`critical_*` se omiten cuando el doc almacenado no tiene detecciones.)

**Errors**: `404` (`{"detail": "histogram not found"}` sin doc), `404`
(`{"detail": "summary not available for '<id>'; run histograms/analysis first"}`
cuando el doc existe pero el análisis nunca corrió).

---

### GET `/api/tools/jobs/{job_id}` → `200 dict` **[NEW]**

Polling de jobs del slice `tools` (`histogram_analysis`). Filtrado por `slice_name="tools"`.

### POST `/api/tools/jobs/{job_id}/cancel` → `202 {job_id}` **[NEW]**

Solicita la cancelación (Stop) de un job `pending|running`; el worker revierte el trabajo
(histogramas/cohorte parciales). Job ya `done`/inexistente → `409`/`404`.

### GET `/api/tools/health` → `200 dict`

Health de dependencias del slice tools (modelo de pose + directorio de salida escribible).
`status: "ok" | "degraded"`.

---

## PROMOTE semantics

### Por que existe `selected_for_training`

La promocion de un video a candidato de entrenamiento es **manual**: un humano decide cuando un
video tiene datos de calidad. Se materializa en el flag por video `selected_for_training`
(`PATCH /api/training/videos/{video_id}`), desacoplado de cualquier procesamiento automatico. El
flag se propaga a las windows del video (`set_selected_for_training`) y estas quedan incluidas o
excluidas de `train`/`retrain`.

**Regla**: `selected_for_training` solo se establece a `true` manualmente (via PATCH desde el FE). Nunca se modifica automaticamente.

### Flujo de promocion

> **Nota:** No existen estados de clase. El modo chroma-only del `video_cutter` se elige por
> request: `POST /api/video/classes/{id}/cut` con `chroma_only: true`.

1. **Clase con datos pero sin modelo**: la clase tiene windows + embeddings en ChromaDB pero su label NO esta en el modelo LSTM activo. El `video_cutter` se usa en modo `chroma_only=true` para detectar clips de clases pendientes de ser incluidas en el modelo.

2. **PROMOTE (boton en Tricks page)**: Cuando una clase alcanza `readiness=true` (suficientes `windows_embedded >= min_windows`, calculado en `GET /api/training/classes/{id}/stats`), el boton PROMOTE marca los videos seleccionados con `selected_for_training=true` via `PATCH /api/training/videos/{video_id}`. Los videos marcados (y sus windows) son candidatos a entrenamiento. Esta accion es MANUAL y requiere decision humana.

3. **Selección de clases entrenables**: `GET /api/training/classes` + `stats` derivan qué clases tienen videos con `selected_for_training=true`. Estas aparecen en el selector de clases de la pagina Training Studio.

4. **train / retrain + approve**: 
   - Modelo nuevo desde cero: `POST /api/training/classes/{id}/train {classes: [...]}`.
   - Añadir clase a modelo existente (fine-tune): `POST /api/training/classes/{id}/retrain {classes: [...], base_model}`.
   Tras entrenar y aprobar (`POST /api/training/models/{run_id}/approve`), el run se activa y el label de la clase pasa a formar parte del modelo LSTM activo.

5. **Clase en el modelo activo**: El `video_cutter` ahora usa el modelo LSTM (hybrid) para clasificar clips de esta clase.

### Implementacion

- `video` tiene el flag `selected_for_training` (default `false`), editable via `PATCH /api/training/videos/{video_id}`.
- `set_selected_for_training` replica el flag a las windows del video en `skeleton_data`.
- `train`/`retrain` solo usan windows con `selected_for_training=true`.

---

## Health

### GET `/health` → `200 {"status": "ok"}`

No requiere autenticacion. No lleva prefijo `/api`.

---

## MongoDB Collections

| Coleccion | DB | Slice(s) | Campos clave |
|---|---|---|---|
| `classes` | pola_api | training | name (unique), hashtags, min_videos, min_windows, cutter_config |
| `videos` | pola_api | crawler, training, video | class_id, local_path, kind, source, can_process, processed, qc_status, selected_for_training |
| `crawls` | pola_api | crawler | class_id, tags, status, downloaded_count |
| `uploads` | pola_api | video | class_id, video_id, local_path, status |
| `clips` | pola_api | video | class_id, local_path, source_kind, status, label |
| `jobs` | pola_api | all (via core/jobs) | kind, entity_id, slice, status, progress, result_json, error |
| `model_runs` | pola_api | training | run_id (unique), mode, classes, status, active, metrics |
| `skeleton_windows` | skeleton_data | pole_ml | label, embedding_models, training_status |
| `skeleton_histograms` | skeleton_data | tools | video_id, trick_label, total_frames, phases, metrics, resampled, z_mean, scores, detections |
| `signal_histograms` | skeleton_data | tools | trick_label, metric, mean (300-pt), std (300-pt), count, phase_bounds, generated_at |

---

## Cross-slice touchpoints

1. **`videos` collection compartida**: Crawler escribe con `source="crawler"`, Training con `source="manual"\|"upload"`, Video con `source="cut"`. Consultas filtran por `source`.

2. **Clases stateless**: no hay máquina de estados de clase (`core/status.py` eliminado). Crawler y video validan por entidades relacionadas sin importar training.

3. **`run_embed()` compartido**: `training/ProcessService` y `video/UploadService` usan la misma funcion de `pole_ml` para skeleton extraction + Chroma embedding.

4. **`ClipService.accept()` crea videos entrenables**: Al aceptar un clip, inserta directamente en `videos` un documento con `kind="clip", can_process=True, source="cut"`.

5. **MongoDB separado para skeletons**: `skeleton_data` es una DB distinta gestionada por `pole_ml.repositories`.

6. **Histogramas por-vídeo + cohorte**: el job `histogram_analysis` (slice tools) escribe el doc
   por-vídeo en `skeleton_histograms` y la cohorte `mean`/`std` en `signal_histograms` (un doc por
   `(trick_label, metric)`); la cohorte no se desnormaliza en el doc por-vídeo.

---

*Document version: 2.1 | Code-accurate | 2026-08-13*
