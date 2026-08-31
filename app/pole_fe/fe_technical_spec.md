# `pole_fe` — Technical Specification

> Maps every Stitch UI component → Backend API endpoints, data models, use cases, and testing.
> **Stitch project**: `projects/8550978881667345493` — 12 screens (4 main pages, modals/interactions)
> **Backend API**: 28 endpoints across 3 slices (training, crawler, video) + `/health`

## 0. Quick Reference: All Stitch Screens

| Screen ID | Title | Type |
|---|---|---|
| `667f37a8` | Tricks Page | Main page |
| `295a0d71` | Training Studio | Main page |
| `1ec2a262` | Model Registry — Pole AI | Main page |
| `e10b1829` | System Jobs Dashboard | Main page |
| `307283a3` | Tricks Registry — Tab Switching | Main page (latest) |
| `8abe35e3` | Tricks — New Trick Modal | Modal |
| `49010cf4` | Tricks — Video Editor Modal Overlay | Modal |
| Various | Add Videos Modal, Bulk Actions, Stats | Sub-views |

## 0.1 Job Polling Pattern (shared)

All async operations (crawl, cut, process, retrain, upload) return `202 {job_id}`. The FE polls `GET /{slice}/jobs/{id}` every 2s via `JobPollingService`.

```
RxJS: timer(0, 2000) → switchMap → GET /{slice}/jobs/{job_id} → takeWhile(status===pending/running, true)
```

Jobs are tracked via `JobsStoreService` which maintains `activeJobs` and `historyJobs` signals. **Jobs history is session-only** (lost on page reload). There is no `GET /api/jobs` endpoint for historical retrieval.

## 0.2 Layout Shell

| Component | Data Model | Endpoints |
|---|---|---|
| Sidebar (240px) | `NavItem{ label, icon, route }` | None (client routing) |
| Top Bar | `Cluster{ id, name }` | None (future) |
| Footer | Static status + version hint | None (no system metrics) |

---

## 1. Page: Tricks Registry

### 1.0 Component Tree

```
TricksPage
├── TrickListPanel (left 40%)
│   ├── Header: "TRICK_REGISTRY" + NEW TRICK button
│   └── TrickCard[]
│       ├── TRK-ID + name + status badge (from API `status`)
│       ├── Hashtag chips
│       └── Actions: edit, delete, chevron_right (hover only)
├── TrickDetailPanel (right 60%)
│   ├── Breadcrumb: "Tricks / name" + ADD VIDEOS button (outlined)
│   ├── Tabs: Videos(non-clips) | Clips(clips) | Stats
│   ├── VideoGrid (Videos tab → non-clips; Clips tab → clips)
│   │   ├── Filter bar: ALL|NEW|PROCESSED|... pills with counts
│   │   ├── VideoCard[] (thumbnail, checkbox, VID-xxx ID, status badge, edit)
│   │   └── BulkActionBar: clip-conditional (Clip|Training|Process|Embed|Delete|Crop AI)
│   └── StatsPanel (Stats tab): stat cards + Recent Model Runs table + Chroma Distribution bars
├── NewTrickModal
├── AddVideosModal (with Crawl/Bulk radio toggle)
└── VideoEditorModal (player, timeline, transform tools, PROMOTE/Discard)
```

### 1.1 TrickListPanel

#### SearchBar
- **Search**: filter_list icon + input with placeholder; filters trick name and hashtags client-side

#### TrickCard
- **Data model**: `{ id: string, name: string, hashtags: string[], statusLabel: string }`
- **Endpoint for list**: `GET /api/training/classes` — all tricks loaded on page init
- **Endpoint for detail**: `GET /api/training/classes/{id}` — loads when trick selected
- **Actions**:
  - **edit** → emits event → parent opens Edit modal → `PATCH /api/training/classes/{id}`
  - **delete** → emits event → parent confirms → `DELETE /api/training/classes/{id}`
  - **select** → emits event → parent sets selectedTrickId → loads detail panel
- **Status label**: Computed from `dto.status` returned by the API (e.g. `AWAITING_UPLOAD_VERIFICATION`, `PROMOTED`)
- **Pipeline stepper**: Removed; not needed for the current workflow

### 1.2 TrickDetailPanel

#### Tabs & Their Endpoints

| Tab | Content | Endpoint |
|---|---|---|
| Videos | Video grid with filter bar | `GET /api/training/classes/{id}/videos` |
| Stats | 4 cards + Model Runs table + Chroma Distribution | `GET /api/training/classes/{id}/stats` + `GET /api/training/models` |

#### VideoCard
- **Actions**:
  - **checkbox** → toggles selection → shows BulkActionBar
  - **more_vert** → opens VideoEditorModal with that video
  - **click card** → toggles selection
- **Status badges**: "processed" or "training_ready" based on `v.processed`
- **Duration**: Not shown (backend does not expose video duration)
- **Filter bar**: Pill buttons (PROCESSED, EMBEDDED, PROMOTED, INGESTED) filter the displayed videos client-side. "ALL" resets filter.

#### BulkActionBar
Appears when 1+ videos selected. Content depends on whether the selection are clips. Wired to API (all run as System Jobs):

| Button | Endpoint | Real/Mock |
|---|---|---|
| **Clip** (toggle) | `POST /api/training/classes/{id}/clip` `{video_ids, clip}` (batch job) | **REAL** |
| **Training** (ADD/REMOVE toggle) | `POST /api/training/classes/{id}/promote` `{video_ids, selected}` (batch job) | **REAL** |
| **Embed** | `POST /api/training/classes/{id}/embed` `{video_ids, model_id}` (job, clips only) | **REAL** |
| **Process** | `POST /api/training/classes/{id}/process` `{video_ids, stride}` (job, opens config modal, clips only) | **REAL** |
| **Delete** | `POST /api/video/videos/delete` `{video_ids}` (batch job) | **REAL** |
| **Crop AI** | `POST /api/video/classes/{id}/cut` `{sources: [{kind:'video', ref}]}` (job) | **REAL** |

#### ProcessConfigModal
- **Opens**: Bulk actions bar "Process" with ≥1 clip selected.
- **Field**: "Slides" (stride) — number input, **integer between 1 and 30 (inclusive)**. Defaults to 5. "START PROCESSING" is disabled when stride is out of range.
- **Confirm**: `POST /api/training/classes/{id}/process` `{video_ids: [selected], stride}` → `202 {job_id}`, tracked via `JobsStoreService.track('training', ...)`.
- **Cancel / backdrop click**: dismisses modal without submitting.

#### EmbedConfigModal
- **Opens when clicking bulk actions bar "Embed" with ≥1 clip selected.**
- **Field**: Model select (generated LSTM runs, value = run `model_path`) mapped to `EmbedRequestDto.model_id`.
- **Confirm**: `POST /api/training/classes/{id}/embed` `{video_ids, model_id}` → `202 {job_id}`.


#### StatsPanel
- **4 stat cards**:
  - **Total Videos**: Count of videos returned by `GET /api/training/classes/{id}/videos`
  - **Total Windows**: `samples_info.windows_total` from `GET /api/training/classes/{id}/stats`
  - **Avg Windows / Video**: `windows_total / total_videos`
  - **Readiness %**: `(windows_embedded / min_windows) * 100`, capped at 100
- **Readiness bar**: Computed from API stats
- **Recent Model Runs table**: Data from `GET /api/training/models` — filtered to show runs matching the current trick name. Shows "--" if no model runs exist.
- **Chroma Distribution bars**: Percentages computed from `windows_embedded`, `windows_pending`, `windows_total`. Labels are "Embedded", "Pending", "Total".

### 1.3 NewTrickModal
- **Endpoint**: `POST /api/training/classes` `{name, hashtags[]}` → `201`
- **Fields**: Trick Name input, Data Source radio (Upload Videos / Scrape from Instagram), Choose Videos button (for upload), Hashtags input (for scrape)
- **States**: idle, submitting ("Creating..."), disabled when name empty
- **After success**: modal closes, list refreshes, auto-selects new trick

### 1.4 AddVideosModal
- **Visual**: "Add Videos to [name]" title, Data Source radio (Crawl from Instagram / Bulk Upload)
- **Crawl mode**: Shows hashtag input → `POST /api/crawler/classes/{id}/crawl` → `202 {job_id}`
- **Bulk mode**: Shows file picker (native `<input type="file">` styled as button) → `POST /api/video/classes/{id}/videos` (multipart .mp4) → `202 {uploads[], job_id}`
- **File input**: Uses native browser file picker. Accepts `.mp4`, `multiple` enabled. Files are appended to `FormData` under key `"files"`.
- **Upload button**: Disabled when no files selected. Shows "Uploading..." during upload.
- **Job tracking**: After submit, job is tracked via `JobsStoreService.track('video', job_id, ...)` and visible in System Jobs page.

### 1.5 VideoEditorModal
- **Visual**: Video player (canvas with play icon + timeline controls), Transform tools (Crop AI, Shift), Metadata (Label, UID), PROMOTE/Discard buttons
- **Opens**: When clicking `more_vert` button on any video card
- **Endpoints**:
  - Video source: `GET /api/video/clips/{id}/video` (streaming URL)
  - **PROMOTE**: Placeholder — calls `processVideos` (same as bulk Promote)
  - **Discard**: `POST /api/video/clips/{id}/discard`
- **Note**: Crop AI, Shift, and timeline controls are visual/mock only. Trim/crop is not yet implemented client-side.

### 1.6 Testing Cases — Tricks Page

| # | Test | Steps | Expected | Status |
|---|---|-------|----------|--------|
| TC-01 | Create trick | NEW TRICK → fill name → Create | 201, appears in list, auto-selected | ✅ Real |
| TC-02 | Duplicate name | Create trick with existing name | 409 error displayed or toast | ✅ Real |
| TC-03 | Search tricks | Type in search bar | Client-side filter by name and hashtags | ✅ Real |
| TC-04 | Delete trick | Click delete → confirm | Trick removed from list, detail clears | ✅ Real |
| TC-05 | Select trick auto-load | Navigate to tricks page | First trick auto-selected, detail panel loads | ✅ Real |
| TC-06 | Upload video (bulk) | ADD VIDEOS → Bulk Upload → select files → UPLOAD | Job starts, video appears in grid after completion | ✅ Real |
| TC-07 | Scrape video (crawl) | ADD VIDEOS → Crawl → enter hashtags → PROCEED | Crawl job starts, progress tracked | ✅ Real |
| TC-08 | Bulk delete videos | Select 2+ videos → Delete → confirm | Batch delete job starts; grid refreshes on completion | ✅ Real |
| TC-09 | Bulk process | Select 2+ clips → Process | Process job starts, statuses update to processed | ✅ Real |
| TC-10 | Bulk promote | Select 2+ clips → Training → confirm | Promote job starts; only clips allowed | ✅ Real |
| TC-10b | Toggle clip | Select videos → Clip | Clip flag job runs; selection moves to Clips tab | ✅ Real |
| TC-11 | Video filter by status | Click PROCESSED pill → click ALL | Only processed videos shown, then all shown | ✅ Real |
| TC-12 | Edit video | Click more_vert on video → editor opens | Video editor modal appears with video data | ✅ Real |
| TC-13 | Empty video grid | Select trick with 0 videos | "No videos yet" empty state | ✅ Real |
| TC-14 | Stats tab — load | Click Stats tab | 4 stat cards show real data from API | ✅ Real |
| TC-15 | Stats tab — model runs | View Recent Model Runs table | Shows real model runs filtered by trick name, or "No model runs yet" | ✅ Real |
| TC-16 | Stats tab — chroma | View Chroma Distribution bars | Shows embedded/pending/total from real stats | ✅ Real |
| TC-17 | API error | Simulate 500 on GET classes | Error state with retry button | ✅ Real |
| TC-18 | Upload non-mp4 | Try uploading .txt file | File filtered out (only .mp4 accepted) | ✅ Real |
| TC-19 | File input click | Click SELECT FILES in Bulk Upload modal | Native file browser opens | ✅ Real |

---

## 2. Page: Training Studio

### 2.0 Component Tree

```
TrainingPage
├── Header: "TRAINING STUDIO" + subtitle
├── TrainingConfig (left)
│   ├── ExecutionModeCard (Train From Scratch / Fine-Tune Existing)
│   ├── TargetClassesSelector
│   │   └── ClassRow[] (checkbox, name, progress bar, window count)
│   └── TrainingOptions (Data Augmentation, Re-embed Features toggles)
├── Buttons: START TRAINING, SAVE CONFIGURATION
└── JobSummary (right)
    ├── Total Videos (sum of windows_total from selected classes)
    └── Total Classes (selected count)
```

### 2.1 ExecutionModeCard
- **Train From Scratch**: `POST /api/training/classes/{id}/train` `{classes[], ...}`
- **Fine-Tune Existing**: `POST /api/training/classes/{id}/retrain` `{classes[], base_model: run_id, ...}`
- **Base model dropdown**: `GET /api/training/models?status=done`

### 2.2 TargetClassesSelector

#### ClassRow
- **Data model**: `{ class name, checkbox, progress bar, window count (e.g. "250 windows") }`
- **Endpoints**:
  - List: `GET /api/training/classes` (all classes)
  - Stats per class: `GET /api/training/classes/{id}/stats` (called for every candidate)
- **Window count**: Displays `windows_total` from stats (total windows stored in MongoDB)
- **Progress bar**: Shows `windows_total / min_windows * 100` ratio. Green when ≥ 100%.
- **Selection**: Checkbox toggles, minimum 2 required for START TRAINING

### 2.3 TrainingOptions

| Option | Default | Sent in train/retrain body |
|---|---|---|
| Data Augmentation | true | `use_augmentation: true` |
| Re-embed Features | true | `reembed: true` |

### 2.4 JobSummary

- **Total Videos**: Sum of `windows_total` from selected classes' stats
- **Total Classes**: Count of selected classes

### 2.5 Buttons

| Button | Endpoint | Status |
|---|---|---|
| **START TRAINING** | `POST /api/training/classes/{id}/train` or `retrain` | ✅ Real |
| **SAVE CONFIGURATION** | None (disabled; persistence not yet implemented) | 🟡 Disabled placeholder |

### 2.6 Testing Cases — Training Studio

| # | Test | Steps | Expected |
|---|---|---|
| TC-20 | Load candidates | Navigate to page | All classes loaded with window counts and progress bars |
| TC-21 | Window count display | Observe class rows | Shows e.g. "250" for a class with 250 windows stored |
| TC-22 | Progress bar | Class with windows >= min_windows | Green bar at 100%+ |
| TC-23 | Mode selection | Click "Fine-tune Existing" | Base model dropdown appears |
| TC-24 | Base model dropdown | Open dropdown | Lists completed models from API |
| TC-25 | Class selection (insufficient) | Only 1 class selected | START TRAINING disabled (needs ≥2) |
| TC-26 | Start training | Select 2+ classes → START TRAINING → confirm | Job starts, progress polling begins |
| TC-27 | Training progress | Wait for polling | Progress bar updates with epoch % |
| TC-28 | Job summary | Select classes | Shows real total windows and class count |

---

## 3. Page: Model Registry

### 3.0 Component Tree

```
ModelRegistryPage
├── Header: "MODEL REGISTRY" + tabs: MANAGE|TRAIN|EVALUATE|DEPLOY
├── ActiveModelBanner
│   ├── "Production Environment LIVE" + ACTIVE MODEL: #R-xxxx
│   └── Metrics: Val Accuracy, Val Loss (from API model metrics)
├── ExecutionLogTable
│   ├── Filters: Filter + Sort buttons
│   └── RunRow[] (run_id, mode, classes, status, accuracy, loss, created, actions)
└── Footer: Pole AI Systems
```

### 3.1 ActiveModelBanner
- **Endpoint**: `GET /api/training/models/active`
- **Metrics**: Reads `val_accuracy` and `val_loss` from `activeModel().metrics`. Shows "--" if no active model or metrics missing.
- **LIVE badge**: Shown when active model exists, hidden otherwise

### 3.2 ExecutionLogTable — RunRow
- **Endpoint**: `GET /api/training/models`
- **Actions**:

| Action | Endpoint | Status |
|---|---|---|
| View (visibility) | None | 🟡 Disabled (no detail view yet) |
| Stop (stop_circle) | `POST /api/training/models/{id}/reject` | ✅ Real |
| Download | None | 🟡 Disabled (no download endpoint yet) |
| Approve (check) | `POST /api/training/models/{id}/approve` | ✅ Real |
| Delete | None | 🟡 Not wired |

- **Status dots**: completed=green, running=blue, failed=red, awaiting_approval=yellow, archived=grey

### 3.3 Tabs
- MANAGE | TRAIN | EVALUATE | DEPLOY — visual only, no routing

### 3.4 Testing Cases — Model Registry

| # | Test | Steps | Expected |
|---|---|---|
| TC-29 | Load registry | Navigate to page | Table loads with runs from API |
| TC-30 | Active model banner | Check banner | Shows real metrics or "--" if none active |
| TC-31 | Approve run | Click check button on awaiting_approval run → confirm | Run approved, model activated |
| TC-32 | Filter/Sort | Click Filter or Sort buttons | Buttons are disabled (placeholder) |
| TC-33 | Status dots | Observe table rows | Color-coded status indicators |
| TC-34 | LATEST/DEPLOYED tags | Observe table rows | Tags shown on matching runs |

---

## 4. Page: System Jobs

### 4.0 Component Tree

```
SystemJobsPage
├── Header: "SYSTEM JOBS" + subtitle
├── FilterBar: Slice pills (All|Crawler|Training|Video)
├── ActiveJobsSection
│   └── JobCard[] (job ID, slice badge, entity, progress bar, status, Stop button)
└── RecentJobsHistory (collapsible, sorted by date desc)
    └── JobHistoryRow[] (job, kind, entity, status, Date dd-mm-yyyy HH:MM:ss.mmm, Description)
```

### 4.1 JobCard
- **Data source**: `JobsStoreService` shared signals (`activeJobs`, `historyJobs`)
- **Jobs are tracked by**: `TrickDetailPage` (crop/process/embed/promote/clip/delete), `TricksDashboardPage` (create/delete trick), `TrainingStudioPage` (training)
- **Polling**: `JobPollingService.pollJob(slice, jobId)` every 2s
- **Stop button**: `jobsStore.stop(slice, jobId)` → `POST /api/{slice}/jobs/{id}/cancel` with confirm; the job ends in `stopped` and rolls back its work.
- **Date column**: `formatDate()` renders `dd-mm-yyyy HH:MM:ss.mmm`; history sorted most-recent-first.
- **Description**: per-item batch summary `Completed N, Skipped N, Failed N` with reasons, or `created <name>`.
- **Limitations**: Jobs history is **session-only** (lost on page reload). No `GET /api/jobs` endpoint exists.

### 4.2 Testing Cases — System Jobs

| # | Test | Steps | Expected |
|---|---|---|---|
| TC-35 | Active jobs appear | Trigger upload from Tricks → navigate to Jobs | Upload job card appears with progress |
| TC-36 | Progress updates | Wait 2+ seconds | Progress % and status text update |
| TC-37 | Job completes | Wait for done | Card moves to history section |
| TC-38 | Filter by slice | Select "Crawler" filter | Only crawler jobs shown |
| TC-39 | Empty state | No active jobs | "No active jobs. System is idle." message |
| TC-40 | History collapsible | Click history summary | Shows completed/failed/stopped jobs with Date + Description |
| TC-41 | Stop job | Click Stop on active job → confirm | Job ends `stopped`, rolls back work, moves to history |
| TC-42 | Date column | View history | Each row shows dd-mm-yyyy HH:MM:ss.mmm; recent first |

---

## 5. Complete Endpoint-to-Component Map

### 5.1 Training Slice

| Endpoint | Method | Component(s) | Status |
|---|---|---|---|
| `/api/training/classes` | POST | NewTrickModal | ✅ Real |
| `/api/training/classes` | GET | TrickCard, TargetClassesSelector | ✅ Real |
| `/api/training/classes/{id}` | GET | TrickDetailPanel | ✅ Real |
| `/api/training/classes/{id}` | PATCH | EditModal | ✅ Real |
| `/api/training/classes/{id}` | DELETE | TrickCard delete | ✅ Real |
| `/api/training/classes/{id}/stats` | GET | StatsPanel, TrainingStudio | ✅ Real |
| `/api/training/classes/{id}/process` | POST | ProcessConfigModal (bulk Process) | ✅ Real |
| `/api/training/classes/{id}/embed` | POST | EmbedConfigModal (bulk Embed) | ✅ Real |
| `/api/training/classes/{id}/train` | POST | START TRAINING (from scratch) | ✅ Real |
| `/api/training/classes/{id}/retrain` | POST | START TRAINING (fine-tune) | ✅ Real |
| `/api/training/models` | GET | ModelRegistry, TrainingStudio | ✅ Real |
| `/api/training/models/active` | GET | ModelRegistry banner | ✅ Real |
| `/api/training/models/{id}/approve` | POST | ModelRegistry approve | ✅ Real |
| `/api/training/classes/{id}/videos` | GET | VideoGrid | ✅ Real |
| `/api/training/videos/{id}` | PATCH | VideoCard | ✅ Real |
| `/api/training/jobs/{id}` | GET | JobCard polling | ✅ Real |

### 5.2 Crawler Slice

| Endpoint | Method | Component(s) | Status |
|---|---|---|---|
| `/api/crawler/classes/{id}/crawl` | POST | AddVideosModal (scrape) | ✅ Real |
| `/api/crawler/classes/{id}/crawls` | GET | (not shown in current UI) | ✅ Real |
| `/api/crawler/jobs/{id}` | GET | JobCard polling | ✅ Real |

### 5.3 Video Slice

| Endpoint | Method | Component(s) | Status |
|---|---|---|---|
| `/api/video/classes/{id}/videos` | POST | AddVideosModal (upload) | ✅ Real |
| `/api/video/classes/{id}/uploads` | GET | (not shown in current UI) | ✅ Real |
| `/api/video/classes/{id}/cut` | POST | (not shown in current UI) | ✅ Real |
| `/api/video/clips/{id}/video` | GET | VideoEditorModal (streaming) | ✅ Real |
| `/api/video/clips/{id}/accept` | POST | VideoEditorModal Accept | ✅ Real |
| `/api/video/clips/{id}/discard` | POST | BulkDelete, VideoEditor Discard | ✅ Real |
| `/api/video/jobs/{id}` | GET | JobCard polling | ✅ Real |

### 5.4 Placeholder / Mock Status

| Component | Item | Status |
|---|---|---|
| ModelRegistryPage | TRAIN/EVALUATE/DEPLOY tabs | 🟡 Visual only |
| ModelRegistryPage | TRAIN/EVALUATE/DEPLOY tabs | 🟡 Visual only |
| ModelRegistryPage | Filter/Sort/View/Download buttons | 🟡 Disabled (no API endpoints) |
| TrainingStudioPage | SAVE CONFIGURATION | 🟡 Disabled (persistence not implemented) |
| VideoEditorModal | Crop AI, Shift, timeline controls | 🟡 Visual only |
| VideoEditorModal | PROMOTE button | 🟡 Calls processVideos |
| Footer | GPU/CPU/RAM metrics | Removed |
| TrickCard | Pipeline stepper bar | Removed |
| JobsStoreService | History persistence | 🟡 Session-only |

*Document version: 3.0 | 2026-08-05*
