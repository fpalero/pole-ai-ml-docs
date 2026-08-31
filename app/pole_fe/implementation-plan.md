# `pole_fe` — Phased Implementation Plan

> **Pole AI Workflow Manager** — Frontend application phased build plan.
> **Design**: Stitch project `8550978881667345493` (12 screens)
> **API docs**: `docs/app/pola_api/slices.md` + `docs/app/pola_api/flows.md`
> **Tech spec**: `docs/app/pole_fe/fe_technical_spec.md`

## Phase Overview

| Phase | Name | Duration | Dependencies |
|---|---|---|---|
| 1 | Foundation & App Shell | 1 week | None |
| 2 | Tricks Page — CRUD | 1 week | Phase 1 |
| 3 | Tricks Page — Video Management | 1.5 weeks | Phase 2, API: training.slice (UC-01..06 ready) |
| 4 | Tricks Page — Video Editor | 1 week | Phase 3, API: video.slice (UC-30..34 ready) |
| 5 | Training Studio | 1 week | Phase 2, API: video.slice (UC-10 ready), API: training.slice |
| 6 | Model Registry | 1 week | Phase 5, API: training.slice (UC-50..64 ready) |
| 7 | System Jobs | 0.5 weeks | Phase 3, API: all slices |
| 8 | Integration, E2E & Polish | 1 week | All phases |

**Total**: ~8 weeks (single developer). Critical path: 1→2→3/4→5→6→8.

---

## Phase 1: Foundation & App Shell

### 1.1 Feature Description

Set up the Angular 18+ project in `app/pole_fe/`. Configure the shell layout (sidebar, top bar, content area, system status bar), routing with lazy loading, API client infrastructure with interceptors, job polling service, TypeScript types, and shared UI atom components.

**Deliverables**:
- Angular 22 project scaffolded with esbuild, Tailwind, `@angular/build:unit-test` (vitest runner); Playwright added in Phase 8
- CSS custom properties with all Stitch design tokens (dark theme, colors, typography, spacing)
- Layout shell: Sidebar (240px, nav items: Tricks/Training/Model Registry/System Jobs), Top Bar (search, cluster selector, notifications, account), System Status Bar (GPU/CPU/RAM health)
- Lazy-loaded routing for 4 feature modules (tricks, training, model-registry, system-jobs)
- `core/api/api-client.ts`: HttpClient wrapper with get/post/patch/delete/upload/streamUrl
- `core/api/api.interceptor.ts`: error normalization (404/409/422/500 → ApiError format)
- `core/api/job-polling.service.ts`: reactive job polling (RxJS timer + switchMap + takeWhile)
- `core/api/models.ts`: all TypeScript interfaces (Job, TrickClass, ModelRun, Clip, Crawl, etc.)
- `environments/environment.ts` and `.prod.ts` with `API_BASE_URL`
- 13 shared UI atom components: Badge, Button, Card, Chip, Dialog, DragDropZone, EmptyState, ProgressBar, Stepper, Table, VideoPlayer, Icon, Toast

**Shared UI components states**:
- Button: idle, hover, active, disabled, loading (spinner)
- Dialog: open (with backdrop, focus trap), closing (ESC/backdrop click), closed
- ProgressBar: empty (0%), filling (animated), complete (100%), error (red)
- Stepper: step states = completed (green check), active (blue highlight + spinner if processing), pending (grey), error (red X)
- Table: loading (skeleton rows), empty ("No data"), populated (sortable columns), error
- EmptyState: illustration, title, subtitle, CTA button
- Toast: success (green), error (red), warning (yellow), info (blue); auto-dismiss 5s; max 3 visible

### 1.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T1.1 | ApiClient GET returns typed data | `apiClient.get<TrickClass[]>('/api/training/classes')` with mocked HttpClient | Correctly maps response to TrickClass[] |
| T1.2 | ApiClient POST sends body | `apiClient.post('/api/training/classes', body)` | HTTP POST called with correct body and headers |
| T1.3 | ApiClient upload reports progress | `apiClient.upload('/api/video/classes/id/videos', formData)` | HttpEvent stream emits upload progress |
| T1.4 | ApiInterceptor normalizes 404 error | Mock 404 response | Catches HttpErrorResponse, emits ApiError with detail |
| T1.5 | ApiInterceptor normalizes 409 error | Mock 409 with `{detail: "duplicate"}` | ApiError.detail = "duplicate" |
| T1.6 | ApiInterceptor normalizes 422 error | Mock 422 | ApiError emitted |
| T1.7 | ApiInterceptor normalizes 500 error | Mock 500 | ApiError with generic message |
| T1.8 | ApiInterceptor passes through 200 | Mock 200 | Response passed through unchanged |
| T1.9 | JobPollingService polls until done | Mock job: pending→running→done over 3 emissions | Observable completes after 'done', emits all 3 states |
| T1.10 | JobPollingService stops on failed | Mock job: running→failed | Observable completes after 'failed' |
| T1.11 | JobPollingService does not emit duplicates | Mock identical running responses | distinctUntilChanged prevents duplicates |
| T1.12 | Sidebar renders all nav items | Render SidebarComponent | 4 nav items visible with correct icons and labels |
| T1.13 | Sidebar highlights active route | Navigate to /training | Training nav item has active class |
| T1.14 | Sidebar click navigates | Click "Model Registry" nav item | Router navigates to /model-registry |
| T1.15 | TopBar renders search input | Render TopBarComponent | Search input visible |
| T1.16 | TopBar search emits on input (debounced) | Type "handspring" in search | Event emitted after 300ms debounce with "handspring" |
| T1.17 | SystemStatusBar polls /health | Mock /health → `{status: "ok"}` | Shows "Healthy" status text |
| T1.18 | SystemStatusBar shows disconnected | Mock /health → network error | Shows "Disconnected" banner, retries after 30s |
| T1.19 | Button renders all variants | Render primary, secondary, danger, ghost buttons | Each has correct CSS classes |
| T1.20 | Button disabled state | Pass `disabled=true` | Button has disabled attribute, cannot be clicked |
| T1.21 | Button loading state | Pass `loading=true` | Shows spinner, text hidden, disabled |
| T1.22 | Dialog opens and closes | Open dialog → press ESC | Dialog visible → dialog closed, backdrop removed |
| T1.23 | Dialog traps focus | Open dialog → press Tab repeatedly | Focus cycles within dialog, never escapes to background |
| T1.24 | Dialog closes on backdrop click | Open dialog → click backdrop | Dialog closes |
| T1.25 | ProgressBar shows percentage | Pass `progress=0.65` | Bar filled 65%, label shows "65%" |
| T1.26 | ProgressBar at 0% | Pass `progress=0` | Empty bar, no label overflow |
| T1.27 | ProgressBar at 100% | Pass `progress=1` | Full bar, green color |
| T1.28 | Stepper renders steps | Pass 4 steps, active=2 | Step 1 check, Step 2 highlighted, Steps 3-4 grey |
| T1.29 | Table sorts column | Click "Accuracy" column header | Rows reorder by accuracy descending/ascending |
| T1.30 | Table empty state | Pass `data=[]` | Empty state message shown |
| T1.31 | EmptyState renders with CTA | Pass title, subtitle, actionLabel | Action button visible and clickable |
| T1.32 | Toast auto-dismisses | Show toast | Toast removed after 5s |
| T1.33 | Toast max 3 visible | Show 5 toasts rapidly | Only 3 visible, "and 2 more" summary |
| T1.34 | Toast manual dismiss | Click X on toast | Toast removed immediately |
| T1.35 | Lazy loading: tricks module | Navigate to /tricks | Separate chunk loaded in network tab |

### 1.3 Use Cases Covered

| UC | Description | Status |
|---|---|---|
| UC-70 | Poll job | JobPollingService implemented |
| UC-71 | Job not found | ApiInterceptor handles 404 |

### 1.4 Flow to Test: App Initialization

1. Open browser at `http://localhost:4200`
2. App loads → redirect to `/tricks`
3. Sidebar renders with 4 nav items highlighted (Tricks active)
4. Top bar shows search, cluster selector, notification bell, account avatar
5. System Status Bar polls `/health` → shows "SYSTEM_STATUS: NOMINAL" with GPU/CPU stats
6. Content area shows lazy-loaded Tricks page placeholder
7. Click "Training" nav → URL changes to `/training`, Training nav highlights, module lazy-loads
8. Click "Model Registry" → `/model-registry`
9. Click "System Jobs" → `/jobs`
10. Switch cluster selector → state updates (future)

---

## Phase 2: Tricks Page — CRUD

### 2.1 Feature Description

Implement the left panel of the Tricks page: trick list with filter bar, trick cards with status badges and pipeline stepper, and the NewTrickModal for creating tricks. Also implement trick edit and delete functionality.

**Deliverables**:
- `features/tricks/tricks.service.ts`: CRUD methods wrapping `GET/POST/PATCH/DELETE /api/training/classes` + `GET /api/training/classes/{id}` + `GET /api/training/classes/{id}/stats`
- `features/tricks/models.ts`: TrickClass, ClassStatus, PipelineState, CutterConfig, TrickStats types
- `features/tricks/store/tricks-store.ts`: SignalStore with classes[], selectedClassId, selectedClass, filter, loading, error states
- `TrickFilterBar`: Pill toggles (ALL|PROMOTED|CHROMA_ONLY|DRAFT), "Promo Candidates only" toggle, search input. Each pill/filter triggers `GET /api/training/classes?status=X&promotion_candidates=bool`
- `TrickCard`: TRK-ID + name, hashtag chips (#gymnastics), status badge (color by status), 4-step mini pipeline (Ingest→Extract→Train→Promo), edit/delete/chevron_right actions
- `TrickCard` states: normal (all data visible), promoted (green badge), draft (grey badge), failed (red badge), promotable ("Promo Candidate" badge), hovering (subtle lift), selected (blue left border)
- `NewTrickModal` (`NewTrickDialogComponent`): Trick Name (text, required, unique validation), Data Source radio (Upload Videos / Scrape from Instagram), Hashtags (tag input, required, # prefix), Cancel/Create Trick buttons
- `EditTrickModal`: Same as NewTrickModal but pre-filled with existing data, Save Changes/Cancel
- Trick deletion via confirmation dialog

**Component states by TrickCard status**:
| Status | Badge Color | Stepper Progress | Available Actions |
|---|---|---|---|
| draft | grey | Step 1 highlighted | edit, delete, view |
| crawling | yellow | Step 1 check, Step 2 active | view (opens detail) |
| awaiting_qc | yellow | Steps 1-2 check | view |
| cutting | yellow | — | view |
| reviewing | yellow | — | view |
| processing | yellow | — | view |
| chroma_only | blue | Steps 1-3 check | edit, delete, view |
| retraining | yellow | — | view |
| awaiting_approval | yellow | Steps 1-4 check | view |
| promoted | green | All 4 steps check | edit, view |
| failed | red | Error icon at failed step | edit, delete, view, retry |

### 2.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T2.1 | TricksService.getClasses with status filter | `service.getClasses({ status: 'promoted' })` | HttpClient calls `/api/training/classes?status=promoted` |
| T2.2 | TricksService.getClasses with promotion_candidates | `service.getClasses({ promotion_candidates: true })` | Calls with `?promotion_candidates=true` |
| T2.3 | TricksService.getClass by id | `service.getClass('trk-001')` | Calls `GET /api/training/classes/trk-001`, returns TrickClass |
| T2.4 | TricksService.create class | `service.create({ name: 'handspring', hashtags: ['#gym'] })` | POST with body, returns 201 TrickClass |
| T2.5 | TricksService.update class | `service.update('trk-001', { hashtags: ['#new'] })` | PATCH with partial body, returns 200 |
| T2.6 | TricksService.delete class | `service.delete('trk-001')` | DELETE, returns 204 |
| T2.7 | TricksService.getStats | `service.getStats('trk-001')` | Calls `GET /api/training/classes/trk-001/stats` |
| T2.8 | TricksStore.loadClasses | Call `store.loadClasses()` with mocked service | store.classes() populated, store.loading() transitions false→true→false |
| T2.9 | TricksStore.loadClasses error | Mock service to throw 500 | store.error() populated, store.loading() = false |
| T2.10 | TricksStore.setFilter | `store.setFilter({ status: 'promoted' })` | Triggers reload with filter params |
| T2.11 | TricksStore.selectClass | `store.loadClass('trk-001')` | store.selectedClassId() = 'trk-001', store.selectedClass() populated |
| T2.12 | TricksStore.createClass | `store.createClass(formData)` | store.classes() includes new class, toast shown |
| T2.13 | TricksStore.deleteClass | `store.deleteClass('trk-001')` | Class removed from store, toast "Trick deleted" |
| T2.14 | TrickCard renders promoted trick | Render with status='promoted' | Green "PROMOTED" badge, all 4 stepper steps checked |
| T2.15 | TrickCard renders draft trick | Render with status='draft' | Grey "DRAFT" badge, step 1 highlighted |
| T2.16 | TrickCard emits selected on click | Click card | selected event emitted with trick id |
| T2.17 | TrickCard edit button | Click edit icon | edit event emitted |
| T2.18 | TrickCard delete button | Click delete icon | delete event emitted |
| T2.19 | TrickCard hashtags rendered | Render with hashtags: ['#gym', '#acro'] | Two chip elements with text "#gym" and "#acro" |
| T2.20 | TrickFilterBar pill toggle | Click "PROMOTED" pill | Pill gets active class, active pill stored in signal |
| T2.21 | TrickFilterBar emits filter change | Click "CHROMA_ONLY" | filterChange event with { status: 'chroma_only' } |
| T2.22 | TrickFilterBar promo candidates toggle | Click toggle | promotionCandidatesChange event with true |
| T2.23 | TrickFilterBar search input | Type "hand" | debounced 300ms, searchChange event with "hand" |
| T2.24 | NewTrickModal creates trick | Fill name="kickflip", hashtags="#skate" → click Create | POST /api/training/classes called, modal closes, toast shown |
| T2.25 | NewTrickModal validates empty name | Leave name empty → click Create | "Name is required" error, Create button disabled |
| T2.26 | NewTrickModal validates hashtags without # | Enter "gym" as hashtag | "Hashtags must start with #" error |
| T2.27 | NewTrickModal shows 409 duplicate | Mock POST returns 409 | "This trick name already exists" error below name field |
| T2.28 | NewTrickModal shows 422 validation error | Mock POST returns 422 | "Invalid input" error displayed |
| T2.29 | NewTrickModal ESC closes | Press ESC | Modal closes, no API call made |
| T2.30 | NewTrickModal backdrop click closes | Click backdrop | Modal closes |
| T2.31 | NewTrickModal Data Source radio switches | Click "Scrape from Instagram" | Upload area hidden, scrape hint shown |
| T2.32 | NewTrickModal submit button disabled when invalid | Leave name empty | Create Trick button has disabled attribute |
| T2.33 | NewTrickModal submit shows spinner | Fill valid form → click Create | Button text changes to spinner, form fields disabled during submit |
| T2.34 | EditTrickModal pre-fills data | Open with existing trick data | Name, hashtags pre-filled in inputs |
| T2.35 | EditTrickModal saves changes | Edit hashtags → Save | PATCH called with partial body, toast "Trick updated" |
| T2.36 | Delete trick confirmation dialog | Click delete → dialog appears | Dialog shows trick name, "DELETE TRICK" (danger) / "CANCEL" |
| T2.37 | Delete trick confirm | Click "DELETE TRICK" | DELETE called, trick removed from list, toast "Trick deleted" |
| T2.38 | Delete trick cancel | Click "CANCEL" | Dialog closes, trick untouched |
| T2.39 | Empty trick list | Render with classes=[] | EmptyState component with "Create your first trick" CTA |
| T2.40 | Loading skeleton | Set store.loading = true | 3 skeleton cards with shimmer animation |

### 2.3 Use Cases Covered

| UC | Description | Component |
|---|---|---|
| UC-01 | Create class | NewTrickModal |
| UC-02 | List classes | TrickFilterBar, TrickCard |
| UC-03 | View class detail | TrickCard (chevron_right) |
| UC-05 | Edit class | EditTrickModal |
| UC-06 | Delete class | TrickCard (delete) |

### 2.4 Flow to Test: Create → List → Edit → Delete Trick

1. **Create**: Open page at `/tricks`. Click "NEW TRICK" button → NewTrickModal opens
2. Fill name: "handspring", hashtags: "#gymnastics", select "Upload Videos" data source
3. Click "Create Trick" → POST /api/training/classes → 201
4. Modal closes. Toast "Trick created successfully"
5. Trick appears in list as first card with "DRAFT" badge
6. **Edit**: Click edit icon on the new card → EditTrickModal opens with pre-filled data
7. Change hashtags to "#gym #acro" → Click "Save Changes" → PATCH → 200
8. Toast "Trick updated". Card refreshes with updated hashtags
9. **Filter**: Click "DRAFT" pill → only draft tricks shown. New trick visible
10. Click "PROMOTED" pill → draft trick hidden. Click "ALL" → all visible
11. **Delete**: Click delete icon on handspring card → confirmation dialog
12. Confirm → DELETE → 204. Toast "Trick deleted". Card removed from list
13. Try to delete again → card already gone, no API call

---

## Phase 3: Tricks Page — Video Management

### 3.1 Feature Description

Implement the right panel of the Tricks page when a trick is selected: breadcrumb, status badge, EDIT DEFINITION button, 4 tabs (Videos, Crawl, Upload, Stats), video grid with checkboxes and bulk actions, crawl form, upload zone, stats panel, and the AddVideosModal.

**Deliverables**:
- `features/tricks/pages/detail/*`: DetailComponent, PipelineStepperComponent, CrawlFormComponent, UploadZoneComponent, MetricsPanelComponent, WorkflowJobCardComponent
- `features/tricks/pages/dashboard/*`: NewTrickDialogComponent (already in Phase 2, now enhanced with data source flow)
- Detail tabs: Videos (default), Crawl, Upload, Stats
- `VideoGrid` + `VideoCard`: Thumbnails with status badges (pending=amber, processed=blue), play/edit buttons, UID display, checkboxes for multi-select
- `BulkActionBar`: Floating bar with "N Selected" counter + action buttons: Delete (`POST /api/video/clips/{id}/discard`), Crop AI (`POST /api/video/classes/{id}/cut`), Process (`POST /api/training/classes/{id}/process`), PROMOTE (class-level: checks readiness → navigates to Training Studio for fine-tune)
- `CrawlFormComponent`: Tags (comma-separated, pre-filled from trick hashtags), Limit (number), Min/Max Wait (seconds), Sort (dropdown), EXECUTE CRAWL button → `POST /api/crawler/classes/{id}/crawl` → job_id → poll progress
- Crawl history: `GET /api/crawler/classes/{id}/crawls` → table with date, tags, limit, status, downloaded count
- `UploadZoneComponent`: Drag & drop zone (Angular CDK DragDrop + hidden file input), .mp4 only, max 10 files. File list with size/name/remove. UPLOAD & PROCESS button → `POST /api/video/classes/{id}/videos` (multipart) → per-file progress via HttpEvent
- `StatsPanel` (MetricsPanelComponent): Total Videos, Promoted, Processed, Pending counts from `GET /api/training/classes/{id}/stats`. Training Readiness circular gauge. Chroma Distribution bar chart (ng2-charts). "Retrain" button if readiness sufficient.
- `AddVideosModal`: Overlay modal. Data Source radio (Upload / Scrape from Instagram). File drop zone (upload). Hashtags field (scrape, pre-filled). Cancel / Add Videos buttons.
- Pipeline stepper: 5-step visual reflecting class status through the flow
- Job progress: `WorkflowJobCardComponent` polls job and shows progress bar + status text
- Conditionally shown sections based on class status (draft=new crawl+upload forms, crawling=job progress, awaiting_qc=link to QC, etc.)

**BulkActionBar actions**:
- **Delete**: Per-video `POST /api/video/clips/{id}/discard` (for clips) or remove from videos collection. Confirmation dialog: "Delete N videos? This cannot be undone."
- **Crop AI**: `POST /api/video/classes/{id}/cut` with sources. Returns job_id. Poll cut job.
- **Process**: `POST /api/training/classes/{id}/process` with `{stride: 5}`. Returns job_id. Poll training job. Marks videos as `processed=true` and creates skeleton windows in `skeleton_data`.
- **PROMOTE** (class-level): Sets `promotion=true` on the class via `PATCH /api/training/classes/{id}`. Requires `readiness=true` from stats. Promoted classes appear in `GET /api/training/classes?promotion_candidates=true` and are eligible for fine-tune in Training Studio. Only `chroma_only` classes can be promoted. This is NOT a video-level action — it promotes the entire class for model training.

### 3.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T3.1 | DetailComponent loads on trick selection | Set selectedClassId → render | Breadcrumb shows "Tricks > handspring", PROMOTED badge visible |
| T3.2 | DetailComponent shows draft content | Class status = draft | Crawl form + Upload zone visible |
| T3.3 | DetailComponent shows processing content | Class status = processing | Job progress bar visible |
| T3.4 | DetailComponent shows chroma_only content | Class status = chroma_only | Metrics panel + Process/Retrain buttons |
| T3.5 | DetailComponent shows promoted content | Class status = promoted | Success state with metrics, no action forms |
| T3.6 | VideoGrid loads videos | Mock GET /api/training/classes/{id}/videos → 3 videos | 3 VideoCards rendered, tab shows "Videos (3)" |
| T3.7 | VideoGrid empty state | Mock response → [] | "No videos yet" empty state |
| T3.8 | VideoGrid loading state | Loading=true | Skeleton grid (6 placeholder cards) |
| T3.9 | VideoCard status badge: pending | Render with can_process=true, processed=false | Amber "pending" badge |
| T3.10 | VideoCard status badge: processed | Render with processed=true | Blue "processed" badge |
| T3.11 | VideoCard checkbox toggles selection | Click checkbox | Card gets selected border, bulk bar appears |
| T3.12 | VideoCard checkbox deselects | Click checked checkbox | Card deselected, bulk bar updates count |
| T3.13 | VideoCard play button | Click play_arrow | Opens video player modal, streamUrl called |
| T3.14 | VideoCard edit button | Click edit | Opens VideoEditorModal (Phase 4) |
| T3.15 | VideoCard shows UID | Render with uid='8f92a1' | "UID: 8f92a1" text visible |
| T3.16 | BulkActionBar appears when 1+ selected | Select 1 video | Bar slides up, "1 Selected" shown |
| T3.17 | BulkActionBar disappears when 0 selected | Deselect all | Bar slides away |
| T3.18 | Bulk Delete action | Select 2 → click Delete → confirm | POST discard called per clip, clips removed from grid |
| T3.19 | Bulk Delete confirmation shows count | Select 3 → click Delete | Dialog shows "Delete 3 videos?" |
| T3.20 | Bulk Process action | Select 2 → click Process → confirm | POST process called, job_id returned, polling starts |
| T3.21 | Bulk Process disabled when no unprocessed | All selected are already processed | Process button hidden or disabled |
| T3.22 | Bulk Crop AI action | Select 1 → click Crop AI | POST cut called, job polling starts |
| T3.23 | PROMOTE action (class-level) | Check stats → readiness=true → click PROMOTE | Navigates to Training Studio with class pre-selected |
| T3.24 | CrawlForm fields pre-filled from trick | Open with trick.hashtags=['#gym'] | Tags input shows "#gym" |
| T3.25 | CrawlForm EXECUTE CRAWL triggers job | Fill form → click EXECUTE CRAWL | POST crawl called, job_id returned, polling starts |
| T3.26 | CrawlForm disabled during active job | Crawl job running | Form fields disabled, button shows "Crawling..." |
| T3.27 | CrawlForm shows error state | Job fails with "rate limited" | Error message with retry button |
| T3.28 | Crawl history table | Mock GET crawls → 2 crawls | Table with 2 rows, status/downloaded count shown |
| T3.29 | UploadZone drag & drop | Drag .mp4 file onto zone | File added to list with name and size |
| T3.30 | UploadZone rejects non-.mp4 | Drop .pdf file | "Only .mp4 files accepted" error |
| T3.31 | UploadZone max files validation | Add 11 files | "Maximum 10 files" error |
| T3.32 | UploadZone remove file | Click remove button on file | File removed from list |
| T3.33 | UploadZone UPLOAD & PROCESS | Add 2 files → click upload | POST videos (multipart), per-file progress shown |
| T3.34 | UploadZone upload progress | HttpEvent reports 50% | Progress bar at 50% per file |
| T3.35 | UploadZone upload complete | All files uploaded, job done | Toast "Videos processed successfully", grid refreshes |
| T3.36 | StatsPanel loads metrics | Mock GET stats → { total: 124, promoted: 86, processed: 32, pending: 6 } | Counts displayed correctly in cards |
| T3.37 | StatsPanel readiness gauge | readiness=0.42 | Circular gauge shows 42% |
| T3.38 | StatsPanel readiness = 100% | readiness=1.0 | Gauge full green, "Ready to promote" shown |
| T3.39 | StatsPanel shows retrain button | readiness=0.85 (above threshold) | "Retrain" button enabled |
| T3.40 | StatsPanel hides retrain button | readiness=0.15 | "Retrain" button disabled or hidden |
| T3.41 | StatsPanel chroma distribution | Mock distribution data | Bar chart renders with correct labels and values |
| T3.42 | AddVideosModal upload mode | Select "Upload Videos" | File drop zone visible, hashtags hidden |
| T3.43 | AddVideosModal scrape mode | Select "Scrape from Instagram" | File drop zone hidden, hashtags field visible |
| T3.44 | AddVideosModal submits upload | Upload mode → drop file → Add Videos | POST videos called, modal closes, job polling starts |
| T3.45 | AddVideosModal submits scrape | Scrape mode → tags → Add Videos | POST crawl called, modal closes, job polling starts |
| T3.46 | AddVideosModal ESC closes | Press ESC | Modal closes, no API call |
| T3.47 | Tab switch preserves state | Click Upload tab → click Videos tab | Video grid shows cached data, no refetch |
| T3.48 | EDIT DEFINITION button | Click → opens EditTrickModal | Pre-filled with current trick data |
| T3.49 | Breadcrumb shows trick path | Selected trick = "handspring" | "Tricks / handspring" visible |
| T3.50 | Job progress bar shows real-time updates | Job running → poll 3 times | Progress % updates, status text changes |

### 3.3 Use Cases Covered

| UC | Description | Component |
|---|---|---|
| UC-03 | View class detail + pipeline state | DetailComponent |
| UC-04 | View class stats | StatsPanel |
| UC-10 | Upload videos | UploadZone, AddVideosModal |
| UC-12 | Upload error | UploadZone (error state) |
| UC-20 | Launch crawl | CrawlForm, AddVideosModal |
| UC-21 | List crawls | Crawl history table |
| UC-22 | List posts for QC | Crawl tab (future QC integration) |
| UC-30 | Cut sources into clips | Bulk Crop AI |
| UC-31 | List videos | VideoGrid |
| UC-33 | Accept clip | VideoEditorModal PROMOTE |
| UC-34 | Discard clip | Bulk Delete |
| UC-40 | Process clips | Bulk Process |
| UC-41 | Process idempotency | Bulk Process (calls existing endpoint) |
| UC-42 | Process error (no data) | Bulk Process (error state) |
| UC-70 | Poll job | WorkflowJobCard |

### 3.4 Flow to Test: Upload Videos → Process → PROMOTE

1. Navigate to Tricks page. Select trick "handspring" (status=draft) from list
2. Right panel loads → breadcrumb "Tricks > handspring", DRAFT badge, EDIT DEFINITION button
3. Click Upload tab → drag 2 .mp4 files onto drop zone
4. Files appear in list with names and sizes
5. Click "UPLOAD & PROCESS" → POST /api/video/classes/{id}/videos (multipart)
6. Per-file progress bar shows → 50% → 100% per file
7. Job polling starts → progress bar shows "Processing videos..." 0→100%
8. On complete: Videos tab auto-selected, 2 new video cards appear with "processed" badges
9. Select both videos via checkboxes → bulk bar slides up: "2 Selected" + Delete/Process
10. Click "Process" → confirmation: "Process 2 videos? This will extract pose data and generate embeddings."
11. Confirm → POST /api/training/classes/{id}/process `{stride: 5}` → job_id
12. Job polling → progress: "Extracting pose data..." 0→50% → "Generating embeddings..." 50→100%
13. Done → toast "2 videos processed successfully", video badges update to blue "processed"
14. Click Stats tab → `GET /api/training/classes/{id}/stats` → readiness check
15. If `readiness=true` (windows_embedded >= min_windows): PROMOTE button enables
16. Click PROMOTE → navigates to Training Studio with class pre-selected for fine-tune

---

## Phase 4: Tricks Page — Video Editor

### 4.1 Feature Description

Implement the VideoEditorModal (`49010cf4`) with client-side video trimming, cropping, and shifting. Includes the trim panel (START/END inputs), crop & shift panel (X OFFSET, Y OFFSET, SCALE, Center Trick button), preview toggle (Show Original Before/After), and Accept/Discard actions. The editor creates temporal previews client-side; changes are persisted only when Accept is called via `POST /api/video/clips/{id}/accept {label?, cutter_config?}`.

**Deliverables**:
- `VideoEditorModal`: Full-screen modal overlay with video player + edit controls
- Trim controls: START time input (mm:ss), END time input (mm:ss), +1f/-1f frame step buttons
- Crop & Shift controls: X OFFSET slider (0-100%), Y OFFSET slider (0-100%), SCALE slider (1.0-2.0x)
- Center Trick button: calls `POST /api/video/classes/{id}/center-trick` (planned endpoint, mock for now)
- CROP_AREA visual overlay on video showing the result frame
- Preview toggle: "Show Original" checkbox (split view before/after)
- Video controls: forward_10, play_circle, replay_10; 00:12 / 00:45 time display
- Footer: Reset to Original (undo all edits), Discard (POST discard), Save Changes (temporal preview only)
- Accept/PROMOTE: Sends `POST /api/video/clips/{id}/accept {label?, cutter_config}` to persist
- Transform tab / Metadata tab sidebar
- Label dropdown under Metadata: trick name + "Unknown" option
- Undo/redo for edit operations (history stack, max 20 ops)

**Client-side editing approach**:
- Video is loaded via blob URL from `GET /api/video/clips/{id}/video`
- Trim/crop/shift adjustments applied using CSS transforms and `<video>` currentTime controls
- Temporal preview = in-memory representation; no file written
- On Accept: cutter_config (trim_start, trim_end, crop_x, crop_y, scale) sent with accept request
- Backend applies cutter_config and persists the final version

### 4.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T4.1 | VideoEditorModal loads video | Open modal with clip_id='8f92a1' | Video element with correct blob URL, plays on click |
| T4.2 | VideoEditorModal shows CROP_AREA overlay | Modal open | Crop frame visual overlay visible on video |
| T4.3 | Trim START input sets start time | Enter "00:05" in START | Video seeks to 5s, trim_start = 5 |
| T4.4 | Trim END input sets end time | Enter "00:30" in END | trim_end = 30 |
| T4.5 | Trim START cannot exceed END | Set START to 00:40 with END at 00:30 | Validation error or auto-correct |
| T4.6 | -1f button steps back 1 frame | Click -1f | currentTime decreases by ~1/fps seconds |
| T4.7 | +1f button steps forward 1 frame | Click +1f | currentTime increases by ~1/fps seconds |
| T4.8 | X OFFSET slider adjusts crop_x | Drag slider to 25% | crop_x = 25, CROP_AREA shifts horizontally |
| T4.9 | Y OFFSET slider adjusts crop_y | Drag slider to -10% | crop_y = -10, CROP_AREA shifts vertically |
| T4.10 | SCALE slider adjusts scale | Drag to 1.2x | scale = 1.2, CROP_AREA enlarges proportionally |
| T4.11 | Center Trick button calls endpoint | Click Center Trick | POST /api/video/classes/{id}/center-trick called (or mock) |
| T4.12 | Center Trick shows progress overlay | Click Center Trick | "Analyzing pose data... (3s)" overlay shown |
| T4.13 | Center Trick success updates values | Center Trick completes | X/Y OFFSET and SCALE updated to centered values |
| T4.14 | Show Original toggle ON | Check "Show Original" | Split view: left=original, right=edited |
| T4.15 | Show Original toggle OFF | Uncheck toggle | Only edited view shown |
| T4.16 | Play button plays video | Click play_arrow | Video plays from current position |
| T4.17 | Replay 10 button | Click replay_10 | Seeks 10 seconds backward |
| T4.18 | Forward 10 button | Click forward_10 | Seeks 10 seconds forward |
| T4.19 | Skip previous/next buttons | Click skip_previous / skip_next | Seeks to previous/next frame boundary |
| T4.20 | Metadata tab | Click Metadata tab | Label dropdown visible, PROMOTE/Discard buttons |
| T4.21 | Label dropdown shows trick name | Render with trick label | Dropdown pre-selected to trick name |
| T4.22 | Label dropdown includes "Unknown" | Open dropdown | "Unknown" option at bottom |
| T4.23 | PROMOTE button (Accept) | Click PROMOTE | POST accept called with label + cutter_config |
| T4.24 | PROMOTE persists cutter_config | Set trim, crop, scale → PROMOTE | Accept body includes `cutter_config: {trim_start, trim_end, crop_x, crop_y, scale}` |
| T4.25 | Discard button | Click Discard | POST discard called, modal closes, video removed from grid |
| T4.26 | Reset to Original | Click Reset to Original | All edit values reset to defaults, preview updates |
| T4.27 | Save Changes creates temporal preview | Click Save Changes | Modal closes, video marked "edited" in grid, cutter_config stored locally |
| T4.28 | Save Changes does NOT call accept | Click Save Changes | No POST accept called; only client-side state updated |
| T4.29 | ESC closes modal | Press ESC | Modal closes without saving |
| T4.30 | Close button closes modal | Click close X | Modal closes, unsaved changes discarded |
| T4.31 | Undo restores previous edit | Trim → Undo (Ctrl+Z) | Trim values restored to previous state |
| T4.32 | Redo re-applies undone edit | Undo → Redo (Ctrl+Y) | Trim values restored to edited state |
| T4.33 | Undo stack limited to 20 | Perform 25 edits → undo 25 times | After 20 undos, returns to original state |
| T4.34 | Video metadata display | Render with metadata | UID, resolution ("1080x1920"), clip label shown |
| T4.35 | Time display updates during play | Play video → wait 2s | Time display shows "00:02 / 00:45" |

### 4.3 Use Cases Covered

| UC | Description | Component |
|---|---|---|
| UC-32 | Play clip | VideoEditorModal player |
| UC-33 | Accept clip | PROMOTE button |
| UC-34 | Discard clip | Discard button |
| UC-30 | Cut sources (Crop AI re-cut) | Center Trick (future endpoint) |

### 4.4 Flow to Test: Edit → Save → Accept Video

1. From Tricks page, click edit icon on a video ("UID: 8f92a1")
2. VideoEditorModal opens → video loads (GET /api/video/clips/8f92a1/video)
3. CROP_AREA overlay visible. Time display shows "00:00 / 00:45"
4. **Trim**: Enter START = "00:05", END = "00:40". Preview updates to cropped range
5. **Crop**: Drag X OFFSET to 25%, Y OFFSET to -5%, SCALE to 1.2x
6. CROP_AREA shifts accordingly
7. **Preview**: Check "Show Original" → split view shows original left, edited right. Uncheck
8. Toggle to Metadata tab → label dropdown shows "handspring"
9. **Save Changes** → modal closes. Video card shows "edited" indicator
10. Re-open editor → previous edits still applied (temporal state)
11. **Center Trick**: Click Center Trick → progress overlay "Analyzing pose data... (3s)"
12. Values update automatically → X OFFSET = 15%, Y OFFSET = -3% (optimized by AI)
13. **Accept**: Click PROMOTE → POST /api/video/clips/8f92a1/accept
14. Body includes: `{label: "handspring", cutter_config: {trim_start: 5, trim_end: 40, crop_x: 15, crop_y: -3, scale: 1.2}}`
15. Toast "Clip promoted". Navigate to Tricks page → video shows "processed" badge with skeleton windows in `skeleton_data`
16. **Discard flow**: Open another video → make edits → click Discard
17. POST discard called. Modal closes. Video removed from grid

---

## Phase 5: Training Studio

### 5.1 Feature Description

Implement the Training Studio page (`295a0d71`): execution mode selection (Train from Scratch / Fine-tune Existing), target classes selector with per-class progress bars, training options (augmentation, re-embed, stride), job summary, and the START TRAINING flow.

**Deliverables**:
- `features/training/training.service.ts`: Methods wrapping `POST /api/training/classes/{id}/retrain`, `GET /api/training/models`, `GET /api/training/models/active`
- `features/training/models.ts`: TrainingConfig, ClassRow, JobSummary types
- `features/training/store/training-store.ts`: SignalStore with mode, selectedClasses, options, summary state
- `ExecutionModeCard`: Train from Scratch (MODEL NAME input) / Fine-tune Existing (Base Model dropdown from `GET /api/training/models?status=done`) — visual card selection
- `TargetClassesSelector`: Checkbox list of eligible classes from `GET /api/training/classes?promotion_candidates=true`. Per-class progress bar (X / N videos). Status icons: insufficient=error red, ready=check_circle green, pending=remove_circle grey. "2/3 Selected" counter. Select All/Deselect All
- `TrainingOptions`: Data Augmentation toggle (default true), Re-embed Features toggle (default true), Stride Size input (number, default 1)
- `JobSummary`: Cards (Total Videos, Total Classes, Est. Duration). ClassImbalanceWarning banner (when max/min > 10:1). DatasetBreakdown table (CLASS NAME, VIDEOS, STATUS)
- `START TRAINING` button: Disabled if <2 classes selected or 0 training videos. Confirmation dialog. Calls `POST /api/training/classes/{first_class_id}/retrain {classes[], mode, augment, reembed, stride, base_model?}` → 202 {job_id, run_id}. Polls training job.
- `SAVE CONFIGURATION`: Saves current config to backend (`POST /api/training/config` — planned). Restores on page load from `GET /api/training/config` or localStorage fallback.
- Training in progress: When a training job is active, show progress bar with "Training epoch X/50" and loss/accuracy updates

### 5.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T5.1 | TrainingService.retrain call | `service.retrain('handspring_id', { classes: ['handspring','shouldermount'], mode: 'full' })` | POST /api/training/classes/handspring_id/retrain with body |
| T5.2 | TrainingService.getModels for fine-tune dropdown | `service.getModels({ status: 'done' })` | GET /api/training/models?status=done |
| T5.3 | TrainingService.getActiveModel | `service.getActiveModel()` | GET /api/training/models/active |
| T5.4 | ExecutionModeCard: select Train from Scratch | Click "TRAIN FROM SCRATCH" card | Blue border, MODEL NAME input visible, base model dropdown hidden |
| T5.5 | ExecutionModeCard: select Fine-tune Existing | Click "FINE-TUNE EXISTING" card | Blue border, base model dropdown visible with loaded models |
| T5.6 | ExecutionModeCard: model name input | Enter "pole_classifier_v2" in MODEL NAME | mode='full', model_name='pole_classifier_v2' |
| T5.7 | ExecutionModeCard: base model dropdown | Select #R-0842 from dropdown | mode='fine-tune', base_model='R-0842' |
| T5.8 | ExecutionModeCard: only one mode active | Select Train → then Fine-tune | Train deselected, Fine-tune selected |
| T5.9 | TargetClassesSelector loads classes | Mock GET classes → 3 classes | 3 ClassRow components rendered |
| T5.10 | ClassRow: insufficient state | Render with training_videos=50, min_required=200 | Red progress bar, error icon, "50 / 200" label |
| T5.11 | ClassRow: ready state | Render with training_videos=210, min_required=200 | Green progress bar, check_circle icon, "210 / 200" |
| T5.12 | ClassRow: pending state | Render with training_videos=5, min_required=200 | Grey progress bar, remove_circle icon, "5 / 200" |
| T5.13 | ClassRow checkbox toggles selection | Click checkbox | Row highlighted, "2/3 Selected" counter updates |
| T5.14 | Select All button | Click "Select All" | All checkboxes checked, counter "3/3 Selected" |
| T5.15 | Deselect All button | Click "Deselect All" | All deselected, counter "0/3 Selected" |
| T5.16 | Search filters classes | Type "hand" in search | Only "handspring" row visible |
| T5.17 | TrainingOptions: Data Augmentation toggle | Click toggle OFF | augment = false |
| T5.18 | TrainingOptions: Re-embed Features toggle | Click toggle OFF | reembed = false |
| T5.19 | TrainingOptions: Stride input | Enter "2" | stride = 2 |
| T5.20 | START TRAINING disabled with 0 classes | Deselect all classes | Button disabled, tooltip "Add classes to training set" |
| T5.21 | START TRAINING disabled with 1 class | Select only 1 class | Button disabled, "At least 2 classes needed" |
| T5.22 | START TRAINING enabled with 2 classes | Select 2 classes | Button enabled |
| T5.23 | START TRAINING confirmation dialog | Click START TRAINING | "Start training with 2 classes and 260 videos? Est. duration: ~1.5h." |
| T5.24 | START TRAINING triggers retrain | Confirm dialog | POST retrain called, job_id + run_id returned, polling starts |
| T5.25 | START TRAINING progress shown | Job running | "Training epoch 8/50" with 15% progress |
| T5.26 | START TRAINING complete | Job done | Toast "Training complete. Review results in Model Registry." |
| T5.27 | START TRAINING error | Job failed | Toast with error, retry button |
| T5.28 | START TRAINING with fine-tune | Select fine-tune + base model + 2 classes → START | POST includes mode='fine-tune', base_model='R-0842' |
| T5.29 | SAVE CONFIGURATION saves config | Click SAVE CONFIGURATION | POST /api/training/config with current config |
| T5.30 | SAVE CONFIGURATION loads on page visit | Navigate to Training page | GET /api/training/config → form pre-filled with saved config |
| T5.31 | JobSummary cards compute correctly | Select handspring(50) + iron_x(210) | Total Videos=260, Total Classes=2, Est. Duration calculated |
| T5.32 | ClassImbalanceWarning visible | handspring=50, shouldermount=5 | Yellow banner "Class imbalance: handspring has 50 videos while shouldermount has 5" |
| T5.33 | ClassImbalanceWarning hidden | Classes balanced (210 vs 200) | No banner shown |
| T5.34 | DatasetBreakdown table reflects selection | Select 2 classes | Table shows 2 rows with correct status icons |
| T5.35 | Training page empty: no eligible classes | Mock GET classes → [] | "No classes eligible for training" empty state |
| T5.36 | Config persistence without backend | API call fails | Fallback to localStorage, toast "Config saved locally" |

### 5.3 Use Cases Covered

| UC | Description | Component |
|---|---|---|
| UC-02 | List classes (promotion candidates) | TargetClassesSelector |
| UC-04 | View class stats (per class readiness) | ClassRow progress bars |
| UC-60 | Retrain full | START TRAINING with mode='full' |
| UC-61 | Retrain fine-tune | START TRAINING with mode='fine-tune' |
| UC-63 | Retrain error | START TRAINING error state |
| UC-70 | Poll job | Training progress bar |

### 5.4 Flow to Test: Train from Scratch

1. Navigate to `/training`. Training Studio page loads
2. **Mode**: Click "TRAIN FROM SCRATCH" card → blue border, MODEL NAME input appears
3. Enter MODEL NAME: "pole_lstm_v3"
4. **Classes**: TargetClassesSelector loads 3 eligible classes via `GET /api/training/classes?promotion_candidates=true`
5. Classes shown: handspring (50/200, insufficient-red), iron_x (210/200, ready-green), shouldermount (5/200, pending-grey)
6. Check handspring + iron_x → "2/3 Selected". START TRAINING enabled
7. **Options**: Data Augmentation ON, Re-embed ON, Stride = 1 (defaults)
8. **Job Summary**: Total Videos = 260, Classes = 2, Est. Duration = ~1.5h
9. ClassImbalanceWarning: "Class 'handspring' has 50 videos while 'iron_x' has 210"
10. DatasetBreakdown: 2 rows — handspring (Insufficient), iron_x (Ready)
11. Click "START TRAINING" → confirmation: "Start training new model with 2 classes and 260 videos?"
12. Confirm → POST /api/training/classes/handspring_id/retrain `{classes: ["handspring","iron_x","transition"], mode: "full", augment: true, reembed: true, stride: 1}`
13. Response: `202 {job_id: "TRN-441", run_id: "R-0894"}`
14. Progress bar appears: "Training epoch 1/50" at 2% → updates every 3s
15. After ~5 poll cycles: "Training epoch 14/50" at 28% with loss=0.415
16. Eventually: done → toast "Training complete. Review results in Model Registry."
17. Link/toast navigates to Model Registry to review run #R-0894

---

## Phase 6: Model Registry

### 6.1 Feature Description

Implement the Model Registry page (`1ec2a262`, `ca33c63a`): active model banner, execution log table, candidate evaluation comparison matrix, and all row actions (view details, activate, approve, reject, archive, delete, download, cancel training).

**Deliverables**:
- `features/model-registry/model-registry.service.ts`: Methods for GET models, GET active, GET run details, POST activate/approve/reject/archive, DELETE run, GET download
- `features/model-registry/models.ts`: ModelRun, ModelRunRow, RunMetrics, ModelComparison, MetricDelta types
- `features/model-registry/store/model-store.ts`: SignalStore with runs[], activeModel, selectedComparison, loading, error
- `ActiveModelBanner`: Green "LIVE" label, "ACTIVE MODEL: #R-0842", Precision/Recall/F1 Score metrics. "Change Active Model" button → model selection dialog → POST activate
- `ExecutionLogTable`: Filters (mode, status), Sort. Run row table with columns: Run ID (+ LATEST/DEPLOYED badges), Mode (Fine-tune/Retrain_Full icon), Classes (chip list), Status (colored chip), Accuracy (with trend arrow), Loss (with trend arrow), Created (relative time), Actions (visibility/delete/approve/download/stop_circle/archive)
- `RunRow` actions by status: completed→visibility+delete+download; completed(awaiting_approval)→visibility+delete+download+approve; running→visibility+stop_circle; failed→visibility+delete; archived→visibility+delete
- Running row: Blue "RUNNING - EPOCH 14/50" chip with progress %, polling `GET /api/training/jobs/{job_id}` for real-time metrics
- `CandidateEvaluation` (`ca33c63a`): Side-by-side panels: BASELINE (ACTIVE) vs CANDIDATE (EVALUATING). Metrics: Val Accuracy, Val Loss, Inference Time. Delta arrows (green up=improvement, red down=regression). Verdict line (green/yellow/red). "Approve & Activate" button
- View run details: Click visibility → slide-in panel with full metrics (accuracy, precision, recall, F1, confusion matrix), class list with per-class accuracy, training params, model path, duration
- Delete confirmation: "Delete run #R-0892? This cannot be undone."
- Archive confirmation: "Archive #R-0841? It will be hidden from active list."
- Approve confirmation: "Approve and activate #R-0892? It will replace #R-0842 as the active model."
- Download: Triggers file download of .keras model file

### 6.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T6.1 | ModelRegistryService.getModels | `service.getModels()` | GET /api/training/models |
| T6.2 | ModelRegistryService.getModels with filters | `service.getModels({ mode: 'fine-tune', status: 'done' })` | GET with query params |
| T6.3 | ModelRegistryService.getActive | `service.getActive()` | GET /api/training/models/active |
| T6.4 | ModelRegistryService.getRun | `service.getRun('R-0892')` | GET /api/training/models/R-0892 |
| T6.5 | ModelRegistryService.activate | `service.activate('R-0892')` | POST /api/training/models/R-0892/activate |
| T6.6 | ModelRegistryService.approve | `service.approve('R-0892')` | POST /api/training/models/R-0892/approve |
| T6.7 | ModelRegistryService.reject | `service.reject('R-0892')` | POST /api/training/models/R-0892/reject |
| T6.8 | ModelRegistryService.archive | `service.archive('R-0841')` | POST /api/training/models/R-0841/archive |
| T6.9 | ModelRegistryService.deleteRun | `service.deleteRun('R-0841')` | DELETE /api/training/models/R-0841 → 204 |
| T6.10 | ModelRegistryService.download | `service.download('R-0892')` | GET /api/training/models/R-0892/download → blob response |
| T6.11 | ActiveModelBanner shows active model | Mock GET active → #R-0842 with precision=94.2, recall=91.8, f1=0.93 | Banner shows correct values, green "LIVE" label |
| T6.12 | ActiveModelBanner no active model | Mock GET active → 404 | "No active model. Activate one from the table." |
| T6.13 | ActiveModelBanner Change Active Model | Click button → select #R-0892 → confirm | POST activate called, banner updates |
| T6.14 | ExecutionLogTable loads runs | Mock GET models → 5 runs | Table with 5 rows, correct columns |
| T6.15 | ExecutionLogTable sorts by default | Load runs | Sorted by Created descending (newest first) |
| T6.16 | ExecutionLogTable filter by mode | Click filter → select "Fine-tune" | Only fine-tune runs shown |
| T6.17 | ExecutionLogTable filter by status | Click filter → select "Completed" | Only completed runs shown |
| T6.18 | RunRow: completed status chip | Render with status='completed' | Green "COMPLETED" chip |
| T6.19 | RunRow: running status chip | Render with status='running', epoch=14, total=50 | Blue "RUNNING - EPOCH 14/50" chip with 28% |
| T6.20 | RunRow: failed status chip | Render with status='failed' | Red "FAILED" chip |
| T6.21 | RunRow: archived status chip | Render with status='archived' | Grey "ARCHIVED" chip |
| T6.22 | RunRow: accuracy with up arrow | Render accuracy=95.5, previous=94.2 | Green up-arrow with "95.5%" |
| T6.23 | RunRow: accuracy with down arrow | Render accuracy=90.0, previous=94.2 | Red down-arrow with "90.0%" |
| T6.24 | RunRow: loss with down arrow (improvement) | Render loss=0.142, previous=0.180 | Green down-arrow "0.142" (lower loss is better) |
| T6.25 | RunRow: LATEST badge | Most recent run | Blue "LATEST" badge on first row |
| T6.26 | RunRow: DEPLOYED badge | Active model run | Green "DEPLOYED" badge |
| T6.27 | RunRow: mode icon fine-tune | Render mode='fine-tune' | tune icon shown |
| T6.28 | RunRow: mode icon retrain_full | Render mode='retrain_full' | autorenew icon shown |
| T6.29 | RunRow: classes as chips | Render classes=['#handspring','#shouldermount'] | Two chip elements with text |
| T6.30 | RunRow: created relative time | Render created='2h ago' | "2h ago" text |
| T6.31 | RunRow: visibility action | Click visibility icon | Slide-in panel with full run details |
| T6.32 | RunRow: visibility loads details | Click visibility | GET /api/training/models/{run_id} called |
| T6.33 | RunRow: approve action (awaiting_approval) | Status='awaiting_approval' | Check/approve button visible, click triggers POST approve |
| T6.34 | RunRow: approve action hidden (completed, not awaiting) | Status='completed', already active | Approve button hidden |
| T6.35 | RunRow: stop action (running) | Status='running' | stop_circle button visible, click → POST /api/training/jobs/{id}/cancel |
| T6.36 | RunRow: stop action hidden (completed) | Status='completed' | stop_circle hidden |
| T6.37 | RunRow: archive action | Status='completed' (non-active) | archive button visible, click → POST archive |
| T6.38 | RunRow: archive action hidden (active) | Active model | archive button hidden |
| T6.39 | RunRow: delete action | Any non-active status | delete button visible, confirmation dialog, DELETE run |
| T6.40 | RunRow: download action | completed or active | download button visible, triggers file download |
| T6.41 | RunRow: running row polls for updates | Running row rendered | Polls GET /api/training/jobs/{job_id} every 3s, metrics update |
| T6.42 | CandidateEvaluation: baseline panel | Active model #R-0842 exists | Left panel shows baseline metrics: Val Accuracy 94.2%, Val Loss 0.180, Inference Time 42ms |
| T6.43 | CandidateEvaluation: candidate panel | Select #R-0892 as candidate | Right panel shows candidate metrics: 95.5%, 0.142, 45ms |
| T6.44 | CandidateEvaluation: accuracy delta | Candidate acc=95.5, baseline=94.2 | Delta = +1.3% with green up-arrow |
| T6.45 | CandidateEvaluation: loss delta | Candidate loss=0.142, baseline=0.180 | Delta = -0.038 with green down-arrow |
| T6.46 | CandidateEvaluation: inference delta warning | Candidate inference=45ms, baseline=42ms | Delta = +3ms with red up-arrow (slower is worse) |
| T6.47 | CandidateEvaluation: green verdict | All metrics improved | "passes all strict evaluation gates" in green |
| T6.48 | CandidateEvaluation: yellow verdict | Mixed results | "Mixed results" in yellow with specific metrics highlighted |
| T6.49 | CandidateEvaluation: red verdict | Candidate worse | Warning in red, "Approve & Activate" still enabled |
| T6.50 | CandidateEvaluation: only completed runs selectable | Try to select running run | Tooltip "Only completed runs can be compared" |
| T6.51 | Approve & Activate button | Click button | Confirmation dialog → POST approve → 200 |
| T6.52 | Approve success flow | Approve completes | ActiveModelBanner updates to new model, previous active archived, toast shown |
| T6.53 | ModelStore.loadRuns | Call store method | store.runs() populated, store.loading() toggles |
| T6.54 | ModelStore error state | Mock API 500 | store.error() populated with error message |
| T6.55 | View details slide-in panel | Click visibility on row | Panel slides from right with full metrics (precision, recall, F1, confusion matrix), classes, params, path, duration |
| T6.56 | View details close | Click close button | Panel slides out |

### 6.3 Use Cases Covered

| UC | Description | Component |
|---|---|---|
| UC-50 | List runs | ExecutionLogTable |
| UC-51 | View active model | ActiveModelBanner |
| UC-52 | View run detail | View details panel |
| UC-53 | Activate run | Change Active Model button |
| UC-54 | Reject run | RunRow reject action |
| UC-62 | Approve run | Approve & Activate button |

### 6.4 Flow to Test: Compare & Approve Model

1. Navigate to `/model-registry`. ExecutionLogTable loads with 5 runs
2. ActiveModelBanner shows: "ACTIVE MODEL: #R-0842" with Precision 94.2%, Recall 91.8%, F1 0.93
3. Table shows: #R-0892 (LATEST, Fine-tune, COMPLETED, 95.5% ↑, 0.142 ↓, 2h ago)
4. #R-0891 is running: "RUNNING - EPOCH 14/50" with polling updates every 3s
5. CandidateEvaluation: BASELINE panel shows #R-0842 metrics
6. Click on #R-0892 row → CANDIDATE panel loads: Val Accuracy 95.5%, Val Loss 0.142, Inference Time 45ms
7. Deltas: Accuracy +1.3% (green ↑), Loss -0.038 (green ↓), Inference +3ms (red ↑ with warning)
8. Verdict: "Run #R-0892 passes all strict evaluation gates. Performance delta is overwhelmingly positive with acceptable inference trade-off." (green)
9. Click "Approve & Activate" → confirmation: "Approve and activate #R-0892?"
10. Confirm → POST /api/training/models/R-0892/approve → 200
11. ActiveModelBanner updates: "ACTIVE MODEL: #R-0892" with new metrics
12. #R-0842 row now shows ARCHIVED status, no longer has DEPLOYED badge
13. #R-0892 now has DEPLOYED badge
14. Associated class → promoted (visible on Tricks page)

---

## Phase 7: System Jobs

### 7.1 Feature Description

Implement the System Jobs page (`e10b1829`): active job cards with real-time progress, collapsible completed jobs history, cancel/retry actions, and filtering by slice and status.

**Deliverables**:
- `features/system-jobs/system-jobs.service.ts`: Methods for cancel job (`POST /{slice}/jobs/{id}/cancel` — planned), retry (re-trigger original operation)
- `features/system-jobs/models.ts`: JobInfo, JobHistoryRow types
- `features/system-jobs/store/jobs-store.ts`: SignalStore with activeJobs[], historyJobs[], filters
- `JobsFilterBar`: Slice filter (All|Crawler|Training|Video), Status filter (All|Running|Completed|Failed), Auto-refresh toggle (ON by default)
- `ActiveJobsSection`: Job card grid (2 columns). Each card: Job ID (#CRW-892), Kind (crawl with download_for_offline icon), Entity (trick name), Progress bar (65%), Status text ("Downloading videos..."), Started time ("5 min ago"), sync-running indicator, Cancel button
- `JobCard`: Polls `GET /{slice}/jobs/{job_id}` every 3s. Progress bar updates smoothly. On done: moves to history with green check. On failed: moves to history with red X.
- `RecentJobsHistory` (collapsible): Table with Job ID, Kind, Entity, Started, Duration, Status, Action. Expandable row for error details. Retry button on failed jobs.
- Cancel flow: Click Cancel → confirmation: "Cancel this job? Progress will be lost." → POST cancel → job moves to history as "cancelled"
- Retry flow: Click Retry on failed job → re-triggers original operation with same params → new job card appears
- Auto-refresh: toggle controls timer; OFF = static display

### 7.2 Unit Testing Plan

| # | Test | Steps | Expected |
|---|---|---|---|
| T7.1 | SystemJobsService.cancelJob | `service.cancelJob('crawler', 'CRW-892')` | POST /api/crawler/jobs/CRW-892/cancel |
| T7.2 | JobCard renders active job | Render with status='running', progress=0.65, kind='crawl' | Progress bar 65%, "Downloading videos...", Cancel button |
| T7.3 | JobCard shows kind icon | kind='cut' | content_cut icon shown |
| T7.4 | JobCard different kind icons | kind='process', kind='retrain', kind='upload' | Correct icon per kind (memory, model_training, cloud_upload) |
| T7.5 | JobCard progress bar fills | progress=0.65 | Bar width 65%, "65%" label |
| T7.6 | JobCard progress at 0% | progress=0 | Empty bar, 0% label |
| T7.7 | JobCard progress at 100% | progress=1 | Full bar, 100%, "Complete" status |
| T7.8 | JobCard status text updates | status_text='Training epoch 8/50' | Text visible below progress bar |
| T7.9 | JobCard started time relative | started_at='5 min ago' | "Started: 5 min ago" shown |
| T7.10 | JobCard Cancel button click | Click Cancel | Confirmation dialog opens |
| T7.11 | JobCard Cancel confirm | Confirm cancel | POST cancel called, card greyed out |
| T7.12 | JobCard Cancel cancel (keep running) | Click Cancel → click "KEEP RUNNING" | Dialog closes, job unaffected |
| T7.13 | JobCard polling updates progress | Job running → mock progress 0.3 → 0.65 → 1.0 | Progress bar updates smoothly through emissions |
| T7.14 | JobCard completes → moves to history | Job done | Card removed from active, added to history with green check |
| T7.15 | JobCard fails → moves to history | Job failed with error | Card in history with red X, error message, retry button |
| T7.16 | JobHistoryRow shows done status | status='done' | Green "Done" check, duration shown |
| T7.17 | JobHistoryRow shows failed status | status='failed', error="OOM on GPU_0" | Red "Failed" chip, "OOM on GPU_0" error text, retry button |
| T7.18 | JobHistoryRow shows cancelled status | status='cancelled' | Grey "Cancelled" chip |
| T7.19 | JobHistoryRow Retry button | Click Retry | Re-triggers original operation, new job card in active section |
| T7.20 | JobHistoryRow expand for details | Click expand on row | Full error message and result JSON shown |
| T7.21 | JobsFilterBar Slice filter | Select "Crawler" | Only crawler jobs in active + history sections |
| T7.22 | JobsFilterBar Status filter | Select "Failed" | Only failed jobs shown |
| T7.23 | JobsFilterBar Auto-refresh OFF | Toggle off | Polling stops, progress freezes |
| T7.24 | JobsFilterBar Auto-refresh ON | Toggle on | Polling resumes at 3s interval |
| T7.25 | ActiveJobsSection "Active Jobs (2)" count | 2 active jobs | Header shows "(2)" |
| T7.26 | ActiveJobsSection empty state | 0 active jobs | "No active jobs. System is idle." with check_circle |
| T7.27 | RecentJobsHistory collapsible | Click expand_more | History table expands/collapses |
| T7.28 | JobsStore tracks active jobs | Add job via polling | store.activeJobs() contains job |
| T7.29 | JobsStore removes completed jobs | Job done | Job moves to store.historyJobs(), removed from active |
| T7.30 | JobsStore filters by slice | Set filter to 'training' | Both active and history filtered |
| T7.31 | Cleanup on component destroy | Navigate away while poll active | All polling subscriptions cancelled |
| T7.32 | Stale job 404 during polling | Mock 404 response | Job removed from active list |

### 7.3 Use Cases Covered

| UC | Description | Component |
|---|---|---|
| UC-70 | Poll job | JobCard |
| UC-71 | Job not found | JobCard (404 → removed) |

### 7.4 Flow to Test: Monitor → Cancel → Retry Job

1. From Tricks page, trigger a crawl job → POST /api/crawler/classes/{id}/crawl → 202 {job_id: "CRW-892"}
2. Navigate to `/jobs`. System Jobs page loads
3. ActiveJobsSection shows 1 card: "#CRW-892 crawler crawl: backflip 0% Downloading videos..."
4. Wait 3s → polling updates: 15% → 35% → 65% → status text changes
5. Click Cancel on the job card → confirmation: "Cancel this job? Progress will be lost."
6. Click "CANCEL JOB" → POST /api/crawler/jobs/CRW-892/cancel
7. Job card moves to RecentJobsHistory: "#CRW-892 crawler backflip 2 min ago Cancelled"
8. **Retry flow**: Find failed job #CUT-112 in history: "cut shouldermount 4h ago Failed — OOM on GPU_0"
9. Click "Retry" → re-triggers POST /api/video/classes/{id}/cut with same params
10. New job card #CUT-115 appears in Active section with fresh progress
11. Filter bar: Select "Crawler" slice → only crawler jobs in both sections
12. Select "Training" → empty if no training jobs running
13. Toggle Auto-refresh OFF → progress bars stop updating
14. Toggle ON → resumes

---

## Phase 8: Integration, E2E & Polish

### 8.1 Feature Description

Cross-page integration, end-to-end testing with Playwright, accessibility audit, performance optimization, error state polish, and final QA.

**Deliverables**:
- E2E test suite (Playwright) covering Workflow A, Workflow B, Workflow C, Model Registry operations, System Jobs monitoring
- Cross-page navigation: Trick Detail "Review" → `/qc-review/:classId`, Training → Model Registry redirect after training completes
- Accessibility audit: WCAG 2.1 AA compliance (keyboard nav, screen readers, focus management, color contrast)
- Performance: bundle analysis, code splitting validation, virtual scroll for large lists, lazy image loading
- Error state polish: Every component handles loading/empty/error states consistently
- Global error handling: API unreachable banner, loading/empty/error states pattern audit
- Toast notification queue: max 3 visible, "and N more" summary
- Animation budget: only progress bars, bulk bar slide-in, skeleton shimmer

### 8.2 E2E Test Scenarios (Playwright)

> **Authoritative spec:** `docs/app/pole_fe/e2e-test-plan.md` defines E2E-1..E2E-20 with
> Given/When/Then + endpoint + DB assertion, and marks the stubbed heavy steps (crawl/cut/train via
> `E2E_FAKES=1`). Classes are **stateless** — the table below is a legacy summary; "status
> transitions" are derived by the FE from entities, not stored. Impl lives in `app/pole_fe/e2e/`,
> run via `pixi run fe-e2e`.

| # | Scenario | Steps | Expected |
|---|---|---|---|
| E2E-1 | Workflow B: Crawl to Promoted | Full 13-step flow from trick creation to model approval (Phase 2+3+5+6) | Derived stage advances (entities, not a stored status); ends with an active run |
| E2E-2 | Workflow A: Upload to Chroma Only | Create trick → upload 2 .mp4 → verify (mock) → check stats | Class chroma_only, chroma distribution displayed |
| E2E-3 | Create → Edit → Delete Trick | NewTrickModal → EditTrickModal → confirm delete | Trick created (201), edited (200), deleted (204), removed from list |
| E2E-4 | Video upload and bulk actions | Upload 3 videos → select 2 → Process → PROMOTE | Videos appear in grid, processed, PROMOTE navigates to Training Studio |
| E2E-5 | Video Editor: trim and accept | Open editor → trim to 5s-40s → crop → Center Trick → Accept | Accept body includes correct cutter_config, video badge updates |
| E2E-6 | Training from scratch | Select mode=full, 2 classes → START → wait for done | Job completes, navigate to Model Registry |
| E2E-7 | Training fine-tune | Select mode=fine-tune, base_model from dropdown, 1 new class → START | POST includes mode='fine-tune', base_model, job starts |
| E2E-8 | Model Registry: compare and approve | Load registry → compare 2 runs → approve candidate | Active model changes, previous archived, toast confirmation |
| E2E-9 | Model Registry: activate | Change active model to another completed run | POST activate, banner updates |
| E2E-10 | Model Registry: archive + delete | Archive old run → delete it | Status changes to archived, then deleted (204) |
| E2E-11 | System Jobs: monitor crawl | Trigger crawl → navigate to Jobs → watch progress | Progress updates, done → moves to history |
| E2E-12 | System Jobs: cancel | Active job → cancel | Job moves to history as "cancelled" |
| E2E-13 | System Jobs: retry | Failed job → retry | New job appears in active, re-runs |
| E2E-14 | System Jobs: filter | Filter by slice/status | Only matching jobs shown |
| E2E-15 | Error: API unreachable | Mock API down → load Tricks page | "Cannot connect to server. Retrying..." banner |
| E2E-16 | Error: 409 duplicate trick | Create trick with existing name | Inline error "This trick name already exists" |
| E2E-17 | Error: 422 invalid hashtag | Create trick with hashtag "gym" (no #) | Inline validation error |
| E2E-18 | Error: 422 .exe upload | Upload .exe file | "Only .mp4 files accepted" error |
| E2E-19 | Responsive: tablet layout | Viewport 768px | Sidebar collapses, single-column video grid |
| E2E-20 | Responsive: mobile layout | Viewport 375px | Bottom nav, stacked cards |

### 8.3 Use Cases Covered

All 21 use cases (UC-01 through UC-71) covered across all 8 phases.

### 8.4 QA Checklist

- [ ] All 28 API endpoints have corresponding service methods
- [ ] All service methods have error handling (404, 409, 422, 500)
- [ ] Every component has loading, empty, error, and success states
- [ ] Every form validates on blur and submit
- [ ] Every destructive action has confirmation dialog
- [ ] Job polling cleans up on component destroy (no memory leaks)
- [ ] Keyboard navigation works on all pages
- [ ] Screen reader announces job status changes (aria-live)
- [ ] Color contrast passes WCAG AA (≥4.5:1 for text)
- [ ] Bundle size <200KB initial, <150KB lazy chunks
- [ ] All 20 E2E tests pass
- [ ] Cross-browser: Chrome, Firefox, Edge functional
- [ ] No console errors on any page
- [ ] System status bar polls /health and displays correctly
- [ ] Dark theme consistent across all pages

---

## Appendix A: Cumulative Unit Test Count

| Phase | Test Count |
|---|---|
| Phase 1: Foundation | 35 |
| Phase 2: Tricks CRUD | 40 |
| Phase 3: Video Management | 50 |
| Phase 4: Video Editor | 35 |
| Phase 5: Training Studio | 36 |
| Phase 6: Model Registry | 56 |
| Phase 7: System Jobs | 32 |
| **Total Unit Tests** | **284** |
| Phase 8: E2E Tests (Playwright) | 20 |
| **Grand Total** | **304** |

## Appendix B: Data Flow Diagram

```
User Action → Component → Service → ApiClient → HTTP Request
                                                    ↓
                                               Backend API (FastAPI)
                                                    ↓
User sees ← Component ← Store ← Service ← ApiClient ← HTTP Response

For async jobs:
User Action → Component → POST /{slice}/.../{id}/action → 202 {job_id}
                     ↓
              JobPollingService → timer(0, 2000ms)
                     ↓
              GET /{slice}/jobs/{job_id} → pending/running/done/failed
                     ↓
              Store updates → Component re-renders
```

---

## Appendix C: FE Data Models (DTOs) — Per Page & Service

These TypeScript interfaces map 1:1 to backend request/response schemas (see `docs/app/pola_api/slices.md` v2.0).

### C.1 Shared / Core

```typescript
// --- Job System ---
interface Job {
  _id: string;
  kind: 'crawl' | 'process' | 'retrain' | 'upload' | 'cut';
  entity_id: string | null;
  slice: 'crawler' | 'training' | 'video';
  status: 'pending' | 'running' | 'done' | 'failed';
  progress: number;        // 0.0–1.0
  result_json: unknown | null;
  error: string | null;
  created_at: string;      // ISO 8601
  finished_at: string | null;
}

// --- Status Machine ---
type ClassStatus =
  | 'draft' | 'uploading' | 'awaiting_upload_verification'
  | 'crawling' | 'awaiting_qc' | 'cutting' | 'reviewing'
  | 'processing' | 'chroma_only' | 'retraining'
  | 'awaiting_approval' | 'promoted' | 'failed';

type PipelineState =
  | 'upload' | 'upload_verification' | 'crawl' | 'qc'
  | 'cut' | 'clip_review' | 'process' | 'retrain'
  | 'approval' | null;

// --- Common ---
interface ApiError {
  detail: string;
}
```

### C.2 Tricks Page — `TricksService`

```typescript
// POST /api/training/classes  → 201
interface CreateTrickRequest {
  name: string;                        // ^[a-z0-9_]+$
  hashtags: string[];                  // cada uno ^#[^\s#]+$
  min_videos?: number;                 // default 5, >= 0
  min_windows?: number;                // default 200, >= 0
  cutter_config?: Record<string, unknown>;
}

// GET /api/training/classes  → 200
// GET /api/training/classes/{id}  → 200
interface TrickClass {
  _id: string;
  name: string;
  hashtags: string[];
  min_videos: number;
  min_windows: number;
  cutter_config: Record<string, unknown> | null;
  status: ClassStatus;
  promotion: boolean;        // true = candidate for fine-tune
  pipeline_state: PipelineState;
  created_at: string;
  updated_at: string;
}

// PATCH /api/training/classes/{id}  → 200
interface PatchTrickRequest {
  name?: string;
  hashtags?: string[];
  min_videos?: number;
  min_windows?: number;
  promotion?: boolean;       // PROMOTE button sets this to true
  cutter_config?: Record<string, unknown>;
}

// GET /api/training/classes/{id}/stats  → 200
interface TrickStats {
  class_id: string;
  label: string;
  samples_info: {
    windows_total: number;
    windows_embedded: number;
    windows_pending: number;
    windows_trained: number;
  };
  chroma_distribution: Record<string, number>;
  readiness: boolean;    // true when windows_embedded >= min_windows
}

// POST /api/training/classes/{id}/process  → 202
interface ProcessRequest {
  stride: number;          // default 5, >= 1
  model_id?: string;       // modelo embedding alternativo
}

// POST /api/training/classes/{id}/videos  → 201 (NEW)
interface RegisterVideoRequest {
  local_path: string;      // debe existir en disco
  can_process?: boolean;   // default true
  kind?: 'video' | 'clip'; // default 'video'
  parent_id?: string;
  source?: 'manual' | 'upload' | 'cut';
}

// GET /api/training/classes/{id}/videos  → 200 (NEW)
interface VideoRecord {
  _id: string;
  class_id: string;
  local_path: string;
  kind: 'video' | 'clip';
  parent_id: string | null;
  source: 'crawler' | 'upload' | 'manual' | 'cut';
  can_process: boolean;
  processed: boolean;
  embedding_model: string | null;
  created_at: string;
  updated_at: string;
}

// PATCH /api/training/videos/{id}  → 200 (NEW)
interface PatchVideoRequest {
  can_process: boolean;
}

// POST /api/training/classes/{id}/retrain  → 202
interface RetrainRequest {
  classes: string[];          // non-empty, each non-empty
  mode: 'full' | 'fine-tune'; // default 'full'
  reembed?: boolean;          // default true
  base_model?: string;        // run_id, required for fine-tune
  use_augmentation?: boolean; // default false
  use_class_weight?: boolean; // default true
}

interface RetrainResponse {
  job_id: string;
  run_id: string;             // YYYYMMDD_HHMMSS[-N]
}
```

### C.3 Training Studio — `TrainingService`

```typescript
// Uses TrickClass[] from GET /api/training/classes?promotion_candidates=true
// Uses ModelRun[] from GET /api/training/models?status=done (for base model dropdown)
// Calls RetrainRequest from above

interface TrainingConfig {
  mode: 'full' | 'fine-tune';
  model_name?: string;        // for full mode
  base_model?: string;        // run_id for fine-tune
  selected_classes: string[]; // class names
  augment: boolean;
  reembed: boolean;
  stride: number;
}

interface ClassTrainingRow {
  name: string;
  training_videos: number;    // videos with processed=true
  min_required: number;       // class min_windows
  selected: boolean;
  readiness: boolean;
}

interface JobSummary {
  total_videos: number;
  total_classes: number;
  estimated_duration: string; // "~1.5h"
  imbalance_warning?: {
    dominant_class: string;
    dominant_count: number;
    minority_class: string;
    minority_count: number;
  };
}
```

### C.4 Model Registry — `ModelRegistryService`

```typescript
// GET /api/training/models  → 200
// GET /api/training/models/active  → 200
// GET /api/training/models/{run_id}  → 200
interface ModelRun {
  _id: string;
  run_id: string;              // YYYYMMDD_HHMMSS[-N]
  mode: 'full' | 'fine-tune';
  classes: string[];
  class_id: string;
  base_model: string | null;
  status: 'running' | 'done' | 'failed' | 'active' | 'rejected';
  active: boolean;
  metrics: {
    val_accuracy: number;
    val_loss: number;
    [key: string]: number;
  } | null;
  model_path: string | null;    // .keras
  encoder_path: string | null;  // .pkl
  metadata_path: string | null; // metadata.json
  window_count: number;
  error: string | null;
  created_at: string;
  updated_at: string;
}

interface ModelRunRow extends ModelRun {
  badges: string[];             // ['LATEST'] | ['DEPLOYED']
  accuracy_delta?: number;      // vs previous run
  loss_delta?: number;
}

interface ModelComparison {
  baseline: ModelRun;
  candidate: ModelRun;
  deltas: ModelMetricDelta[];
  verdict: string;
  verdict_color: 'green' | 'yellow' | 'red';
}

interface ModelMetricDelta {
  metric: string;
  baseline_value: number;
  candidate_value: number;
  delta: number;
  direction: 'up' | 'down';   // up=increase, down=decrease
  improved: boolean;           // for accuracy: up is good; for loss: down is good
}
```

### C.5 Crawler (used by Tricks Page)

```typescript
// POST /api/crawler/classes/{id}/crawl  → 202
interface CrawlRequest {
  tags: string[];        // required, non-empty, each non-empty, no spaces
  limit?: number;        // default 10, >= 1
  min_wait?: number;     // default 5, >= 0
  max_wait?: number;     // default 10, >= min_wait
}

// GET /api/crawler/classes/{id}/crawls  → 200
interface Crawl {
  _id: string;
  class_id: string;
  tags: string[];
  limit: number;
  min_wait: number;
  max_wait: number;
  status: 'pending' | 'running' | 'done' | 'failed';
  downloaded_count: number;
  error: string | null;
  created_at: string;
  finished_at: string | null;
}

// GET /api/crawler/classes/{id}/posts  → 200
interface Post {
  _id: string;
  class_id: string;
  local_path: string;
  kind: 'video';
  source: 'crawler';
  can_process: boolean;
  processed: boolean;
  qc_status: 'pending' | 'accepted' | 'rejected';
  username: string;
  timestamp: string;
  caption: string | null;
  url: string;
  tag: string;
  created_at: string;
  updated_at: string;
}

// POST /api/crawler/posts/{id}/qc  → 200
interface QcRequest {
  status: 'accepted' | 'rejected';
}
```

### C.6 Video (used by Tricks Page + Video Editor)

```typescript
// POST /api/video/classes/{id}/cut  → 202
interface CutRequest {
  sources: CutSource[];       // required, non-empty
  cutter_override?: Record<string, unknown>;
  model_id?: string;
}

interface CutSource {
  kind: 'post' | 'upload' | 'video' | 'path';
  ref: string;                // post_id | upload_id | video_id | absolute_path
}

// GET /api/video/classes/{id}/clips  → 200
interface Clip {
  _id: string;
  class_id: string;
  local_path: string;
  source_kind: 'post' | 'upload' | 'video' | 'path';
  source_ref: string | null;
  parent_id: string | null;
  status: 'pending' | 'accepted' | 'discarded';
  label: string | null;
  accepted_at: string | null;
  created_at: string;
  updated_at: string;
}

// POST /api/video/clips/{id}/accept  → 200
interface AcceptClipRequest {
  label?: string;            // if null, uses class name
}

// GET /api/video/classes/{id}/uploads  → 200
interface VideoUpload {
  _id: string;
  class_id: string;
  video_id: string;
  filename: string;
  local_path: string;
  size: number;              // bytes
  status: 'pending' | 'processing' | 'verified' | 'failed';
  created_at: string;
  updated_at: string;
}

// POST /api/video/classes/{id}/uploads/{uid}/verify  → 200
interface VerifyRequest {
  accepted: boolean;
}
```

### C.7 System Jobs — `JobsService` (shared)

```typescript
// GET /{slice}/jobs/{id}  → 200
// Reuses Job interface from C.1

interface JobInfo extends Job {
  entity_display: string;    // trick name or "Run #R-XXXX"
  status_text: string;       // "Downloading videos..." | "Training epoch 8/50"
  started_ago: string;       // "5 min ago" (computed)
}

interface JobHistoryRow extends JobInfo {
  duration: string;          // "58m" | "2m" (computed)
  action_label?: string;     // "Retry"
}
```

### C.8 Video Editor State (Client-Side Only)

```typescript
interface VideoEditorState {
  clip_id: string;
  label: string | null;
  trim_start: number;        // seconds
  trim_end: number;          // seconds
  crop_x_offset: number;     // 0–100%
  crop_y_offset: number;     // 0–100%
  scale: number;             // 1.0–2.0x
  show_original: boolean;    // preview toggle
  transform_stack: CutterConfig[];  // undo history (max 20)
  transform_index: number;          // current position in stack
}

interface CutterConfig {
  trim_start?: number;
  trim_end?: number;
  crop_x?: number;
  crop_y?: number;
  scale?: number;
}
```

### C.9 Endpoint Summary (33 total)

| # | Method | Path | FE Service | Page |
|---|--------|------|-----------|------|
| 1 | POST | `/api/training/classes` | TricksService.create | Tricks |
| 2 | GET | `/api/training/classes` | TricksService.list | Tricks, Training |
| 3 | GET | `/api/training/classes/{id}` | TricksService.get | Tricks |
| 4 | GET | `/api/training/classes/{id}/stats` | TricksService.getStats | Tricks |
| 5 | PATCH | `/api/training/classes/{id}` | TricksService.patch | Tricks |
| 6 | DELETE | `/api/training/classes/{id}` | TricksService.delete | Tricks |
| 7 | POST | `/api/training/classes/{id}/process` | TricksService.process | Tricks |
| 8 | POST | `/api/training/classes/{id}/videos` | TricksService.registerVideo | Tricks |
| 9 | GET | `/api/training/classes/{id}/videos` | TricksService.listVideos | Tricks |
| 10 | PATCH | `/api/training/videos/{id}` | TricksService.patchVideo | Tricks |
| 11 | POST | `/api/training/classes/{id}/retrain` | TrainingService.retrain | Training |
| 12 | GET | `/api/training/models` | ModelRegistryService.list | Model Registry, Training |
| 13 | GET | `/api/training/models/active` | ModelRegistryService.getActive | Model Registry |
| 14 | GET | `/api/training/models/{run_id}` | ModelRegistryService.get | Model Registry |
| 15 | POST | `/api/training/models/{run_id}/activate` | ModelRegistryService.activate | Model Registry |
| 16 | POST | `/api/training/models/{run_id}/approve` | ModelRegistryService.approve | Model Registry |
| 17 | POST | `/api/training/models/{run_id}/reject` | ModelRegistryService.reject | Model Registry |
| 18 | GET | `/api/training/jobs/{id}` | JobPollingService.poll | All |
| 19 | POST | `/api/crawler/classes/{id}/crawl` | CrawlerService.startCrawl | Tricks |
| 20 | GET | `/api/crawler/classes/{id}/crawls` | CrawlerService.listCrawls | Tricks |
| 21 | GET | `/api/crawler/classes/{id}/posts` | CrawlerService.listPosts | Tricks |
| 22 | POST | `/api/crawler/posts/{id}/qc` | CrawlerService.qc | Tricks |
| 23 | GET | `/api/crawler/jobs/{id}` | JobPollingService.poll | All |
| 24 | POST | `/api/video/classes/{id}/videos` | VideoService.upload | Tricks |
| 25 | GET | `/api/video/classes/{id}/uploads` | VideoService.listUploads | Tricks |
| 26 | POST | `/api/video/classes/{id}/uploads/{uid}/verify` | VideoService.verify | Tricks |
| 27 | POST | `/api/video/classes/{id}/cut` | VideoService.startCut | Tricks |
| 28 | GET | `/api/video/classes/{id}/clips` | VideoService.listClips | Tricks |
| 29 | GET | `/api/video/clips/{id}/video` | VideoService.streamClip | Tricks |
| 30 | POST | `/api/video/clips/{id}/accept` | VideoService.acceptClip | Tricks |
| 31 | POST | `/api/video/clips/{id}/discard` | VideoService.discardClip | Tricks |
| 32 | GET | `/api/video/jobs/{id}` | JobPollingService.poll | All |
| 33 | GET | `/health` | SystemStatusService.check | All |

---

*Document version: 3.1 | Code-accurate DTOs | 2026-08-05*
