# `pole_fe` — UI/UX Design Specification

> **Pole API Workflow Manager** — 4-page web application for ML pipeline management.
> Based on Stitch designs from project `projects/9998128497502972100`.
> Document version: Initial Design (pre-iteration)

---

## 1. Design System

### 1.1 Tokens
- Dark mode: surface #131313, surface-container #202020, on-surface #e5e2e1
- Primary: #aac7ff, primary-container: #3e90ff, on-primary: #003064
- Secondary: #47e266, secondary-container: #09bf49
- Error: #ffb4ab, error-container: #93000a
- Outline: #8b91a0, outline-variant: #414754
- Typography: Inter (headline + body), JetBrains Mono (labels/data)
- Border radius: 4px
- Icons: Material Icons (filled style, 24px)

### 1.2 Layout Shell (shared across all pages)
- **Sidebar (200px fixed left)**: Logo "NEURAL_FLOW V0.8.2-ALPHA" at top, nav items (Tricks, Training, Model Registry, System Jobs) with Material icons + active state highlight, "NEW PIPELINE" FAB button, Docs/Settings pinned at bottom.
- **Top Bar (full width, 56px)**: Search input (global search), cluster selector dropdown ("Cluster_01 v3_Production"), notification bell with badge, DNS icon, account avatar circle.
- **Main Content Area**: Flex-1, scrollable, page content rendered via router-outlet.
- **System Status Bar (fixed bottom, 32px)**: Left: "SYSTEM_STATUS: NOMINAL // ALL_SYSTEMS_GO" in JetBrains Mono. Right: "GPU_0: 92%", "CPU: 14%", "CHROMA: CONNECTED" with green dot.

### 1.3 Shared UI Components (Atoms)
- **Badge/Chip**: Status indicator pills. Colors: promoted=green, chroma_only=blue, draft=grey, failed=red, processing=yellow, running=blue pulse.
- **Button**: Primary (filled primary-container), Secondary (outlined), Danger (error, for delete/reject), Ghost (text-only). Sizes: sm (28px), md (36px), lg (44px). Icon + text or icon-only variants.
- **Card**: surface-container background, 4px radius, outline-variant border, 16px padding.
- **Dialog/Modal**: Centered overlay (surface-bright backdrop), surface-container background, title + content + actions footer, close X button, trap focus, ESC to close.
- **Progress Bar**: Linear bar with outline-variant track and primary fill. Shows fraction label (e.g., "3,402 / 5,000"). Height 6px, radius 3px.
- **Stepper (Pipeline)**: Horizontal step indicators. Each step has icon circle (check for completed, spinner for active, empty for pending). Connecting lines between steps. Labels below.
- **Data Table**: surface-container header row, alternating surface/surface-container-low rows. Columns with sort arrows. Status chips in cells. Row hover highlight.
- **Video Player**: Custom player with play/pause, timeline scrubber, time display (current/total), speed control (0.5x/1x/2x), fullscreen toggle. Metadata overlay showing confidence score.
- **Drag & Drop Zone**: Dashed border (outline-variant), "Drag & drop .mp4 files here or click to browse" text, file icon, file validation feedback.
- **Empty State**: Centered illustration, title "No tricks yet", subtitle "Create your first trick to get started", action button.
- **Toast/Notification**: Top-right temporary notification. Types: success (green), error (red), info (blue), warning (yellow). Auto-dismiss after 5s.

---

## 6. Global Modals & Popups

### 6.1 Confirmation Dialog (reusable)
- Title: Action description
- Body: Detailed explanation + consequences
- Actions: Confirm button (context-colored) + Cancel button
- Used for: delete trick, delete video, activate model, approve model, start training, cancel job

### 6.2 Create/Edit Trick Modal
- Title: "Create New Trick" or "Edit Trick: {name}"
- Form fields (see Flow 1)
- Actions: Create/Save + Cancel

### 6.3 Video Player Modal
- Full-screen overlay with video at center
- Player controls: play/pause, timeline, volume, speed, fullscreen, picture-in-picture
- Metadata panel (toggle-able): frame number, confidence, track ID, object detections
- Action buttons: Accept (green), Reject (red), Edit (opens editor)
- Keyboard shortcuts: Space=play, ←→=seek, Esc=close

### 6.4 Video Editor Modal (see section 2.4)

### 6.5 Notification Toast (reusable)
- Position: top-right, stacked
- Types: success (green, check icon), error (red, error icon), warning (yellow, warning icon), info (blue, info icon)
- Auto-dismiss after 5 seconds (configurable)
- Manual dismiss via X button
- Max 3 visible at once (older auto-dismiss)

---

## 7. Responsive Behavior

| Breakpoint | Width | Sidebar | Video Grid | Trick List | Tables |
|---|---|---|---|---|---|
| Desktop | ≥1440px | Fixed 200px | 3 columns | Left panel visible | Full columns |
| Laptop | ≥1024px | Fixed 200px | 2 columns | Left panel visible | Full columns |
| Tablet | ≥768px | Collapsible (hamburger) | 1 column | Full width, click navigates | Horizontal scroll |
| Mobile | <768px | Bottom nav bar | Full width | Full width cards | Stacked cards |

---

## 8. QA Considerations

### 8.1 Loading States
- Every data fetch: skeleton loader (not spinner, except for small elements)
- Job submissions: button shows spinner, text changes to "Processing..."
- Video uploads: per-file progress bar
- Page transitions: minimal (instant route change, data loads async)

### 8.2 Empty States
- Tricks page (no tricks): Illustration + CTA
- Videos tab (no videos): "Upload videos or scrape from Instagram to get started"
- Model Registry (no models): "No models trained yet. Go to Training to create your first model."
- System Jobs (no jobs): "No active jobs. System is idle."

### 8.3 Error States
- API unreachable: Top banner "Cannot connect to server. Retrying..." with retry button
- 404: "The requested resource was not found." with navigation suggestion
- 409: Inline error below relevant field
- 422: Inline validation errors
- 500: "Something went wrong. Please try again." with retry button
- Job failure: Red card/job with error message and retry option

### 8.4 Edge Cases
- Trick name with special characters: sanitized, alphanumeric + underscore only
- Video upload > max size: reject with clear message before upload starts
- Concurrent operations on same trick: disable buttons during active job
- Browser tab closed during upload/job: warn user with beforeunload event
- Multiple rapid clicks: debounce button clicks, disable after first click
- Zero videos selected for action: disable bulk action buttons, show "Select videos to continue" hint
- All videos already processed: "Process" button hidden, "All videos processed" badge
- Network disconnected during polling: show reconnecting state, preserve last known data

---

## 9. UI Experience Guidelines

### 9.1 Interaction Patterns
- **Progressive disclosure**: Advanced options (cutter config, stride, augmentation) hidden behind "Advanced" toggle
- **Contextual actions**: Bulk action bar appears only when items selected; per-item actions in 3-dot menu
- **Undo where possible**: Toast notification with "Undo" button for reversible actions (e.g., remove from training)
- **Keyboard shortcuts**: Space=play video, ←→=seek, Esc=close modal, Ctrl+Enter=submit form
- **Drag & drop**: Video upload, trick reordering (future)

### 9.2 Visual Hierarchy
- Primary actions: filled buttons (primary-container)
- Secondary actions: outlined buttons
- Destructive actions: error-colored, always with confirmation
- Information: subtle text or tooltips
- Status: colored badges/chips for quick scanning

### 9.3 Feedback
- Every action has visual feedback (button state change, toast, progress)
- Optimistic UI where safe (e.g., remove from training set - update UI immediately, revert on error)
- Processing states clear: "Processing 3 of 10 videos..."

### 9.4 Navigation
- Breadcrumbs for deep navigation (Tricks > handspring > Videos)
- Back button behavior: returns to previous context
- Active nav item highlighted in sidebar
- Tab state preserved when switching between tricks

---

## 10. Design Iterations

> **Note**: Stitch visual generation was attempted for all 3 iterations but the service experienced timeouts (`MCP error -32001` across `edit_screens`, `generate_screen_from_text`, and `generate_variants`). The iterations below reflect the intended design refinement that would be applied visually. The existing Stitch screens (`68496e2e`, `1cc6927fe`, `2f63c54e`, `5fb86ccf`) remain as-is for reference.

---

### Iteration 1 — Gap Analysis & Structural Refinement

**Reviewer**: UX Lead  
**Focus**: Completeness, missing states, information architecture

#### Findings & Changes

| # | Finding | Change | Affected Section |
|---|---------|--------|-----------------|
| F1 | **Tricks page lacks "Select trick" empty state** in the right panel when no trick is selected. User opens page and sees empty right side with no guidance. | Add centered illustration in right panel: "Select a trick from the list to manage its videos." Pulsing arrow pointing left toward trick list. | 2.3 Right Panel |
| F2 | **Video grid has no filter/sort**. With 50+ videos per trick, users need to filter by status (processed/unprocessed/training) and sort by date/name. | Add filter dropdown bar above video grid: Status filter (All, Pending Processing, Processed, Training Ready), Sort (Date desc, Date asc, Name). | 2.3 Videos Tab |
| F3 | **Training page has no "training history" section**. Users can't see past training runs from this page — they have to navigate to Model Registry. | Add collapsible "Training History" section at bottom showing last 5 runs (Run ID, date, status, accuracy). "View All" link navigates to Model Registry. | 3.2 Layout |
| F4 | **Model Registry needs a "currently training" indicator** that's more prominent. The in-progress row is easy to miss. | Add a persistent banner at top of Model Registry page when a training job is active: "Training in progress: Run #R-0894 — Epoch 8/50 [progress bar] — View Details". | 4.2 Layout |
| F5 | **System Jobs page missing "slice filter" visibility**. Users want to quickly see which slice has the most activity. | Add colored slice count badges next to filter dropdown: Crawler (2), Training (1), Video (0). Badge colors match slice colors. | 5.2 Layout |
| F6 | **No "global action" FAB or quick-add**. All creation flows start from contextual buttons scattered across pages. | Add a persistent FAB (floating action button) in bottom-right corner, context-aware by current page: on Tricks page = "NEW TRICK", on Model Registry = "NEW TRAINING". Saves clicks. | 1.2 Layout Shell |
| F7 | **Video editor missing "undo/redo"**. Client-side editing without undo is risky — one wrong crop loses original view. | Add undo/redo buttons in video editor toolbar. Maintain edit history stack (max 20 operations). | 2.4 Video Editor |
| F8 | **Create Trick modal flow has no "skip to later" for upload/crawl**. User must choose a data source, but may just want to create the trick definition first. | Add third radio option: "Add videos later (create empty trick)". Default selected. If this is chosen, modal closes after creation and right panel shows "Add videos via Upload or Crawl tabs." | Flow 1 |

#### Iteration 1 Design Decisions

- **Navigation consolidation**: The sidebar now has 4 items matching the 4 pages exactly: Tricks, Training, Model Registry, System Jobs. Removed "Workflows" from original design since workflow = pipeline steps within Trick Detail.
- **Color coding standardization**: Status colors standardized across all pages:
  - Green: promoted, completed, done, active, accepted
  - Blue: chroma_only, processing, training_ready  
  - Yellow/Amber: running, in_progress, pending
  - Red: failed, rejected, error, discarded
  - Grey: draft, archived, queued
- **Tab persistence**: When switching between tricks in the left panel, the active tab (Videos/Crawl/Upload/Stats) persists. E.g., if user is on Stats tab for "handspring" and clicks "shouldermount", Stats tab for shouldermount loads.

---

### Iteration 2 — UX Polish & Responsiveness

**Reviewer**: UI Designer + QA  
**Focus**: Interaction details, responsive behavior, accessibility

#### Findings & Changes

| # | Finding | Change | Affected Section |
|---|---------|--------|-----------------|
| F9 | **Bulk actions bar jumps the layout** when it appears/disappears. Distracting and causes misclicks. | Bulk actions bar is now a fixed-position floating bar at the bottom of the video grid area. Slides up with animation when 1+ videos selected. Doesn't shift grid content. | 2.3 Videos Tab |
| F10 | **Video thumbnails show no file info**. Users can't distinguish between similar-looking clips. | Each video card now shows: filename below thumbnail, duration badge (top-right overlay), file size. On hover: preview plays (3s silent loop). | 2.3 Video Grid |
| F11 | **Drag & drop zone has no file queue management**. Users can't reorder or clear selected files before upload. | Add file queue list below drop zone with drag-to-reorder handles, individual remove buttons, total size counter, "Clear All" button. File validation feedback per file (red border + error text for non-.mp4, oversized). | 2.3 Upload Tab |
| F12 | **Training page class selector lacks visual feedback** on which classes have sufficient data. | Each class row shows: name, video count with color bar (green=sufficient >10, yellow=low 3-10, red=insufficient <3), "Min threshold: 200 windows" with met/unmet icon. Classes with insufficient data are dimmed and have a warning icon — can still be selected but show risk warning. | 3.4 Dataset Summary |
| F13 | **Model comparison matrix is confusing** — delta values unclear whether good or bad. | Redesign: green up-arrow for improvements, red down-arrow for regressions. Add "VERDICT" summary line: "Run B outperforms Run A on all metrics" or "Mixed results — Run A better on accuracy, Run B better on loss." Color the verdict green/red/yellow. | 4.2 Comparison Matrix |
| F14 | **System Jobs page has no "auto-scroll" to active jobs**. On page with many completed jobs, user scrolls to find active ones. | Active jobs always pinned at top. Sticky section header "ACTIVE JOBS (3)" with count. Completed section collapsible, collapsed by default if more than 5 active jobs. | 5.2 Layout |
| F15 | **Keyboard shortcuts not documented**. Power users don't know what shortcuts exist. | Add "?" keyboard shortcut that opens a shortcuts help dialog. Add subtle shortcut hints in tooltips (e.g., "Play video (Space)"). | 9.1 Interaction |
| F16 | **Toast notifications stack can overflow screen**. If 5+ jobs complete simultaneously, toasts fill the viewport. | Limit to 3 visible toasts. Queue additional toasts and show "and 2 more notifications" summary. User can click summary to expand all. | 6.5 Notification Toast |

#### Iteration 2 Design Decisions

- **Tablet/mobile strategy**: Instead of trying to fit the two-panel Tricks layout on tablet, use a master-detail pattern: full-width trick list, clicking a trick navigates to a full-width video management view. Back button returns to list. Simplifies responsive implementation significantly.
- **Video player controls**: Changed from custom-built to standardized browser controls with overlay. Decision: custom controls add 3+ weeks of dev time. Use native `<video>` with `controls` attribute, add custom overlay for confidence/ID metadata only.
- **Date/time formatting**: All timestamps use relative time ("2h ago", "3d ago") with absolute timestamp on hover tooltip. Matches Stitch design patterns.
- **Loading skeleton granularity**: Page-level skeleton for initial load. Component-level skeleton for tab switches within Tricks page. No skeleton for rapid operations (accept/reject clip).

---

### Iteration 3 — Edge Cases, Performance & Final Polish

**Reviewer**: Lead Developer + QA Lead  
**Focus**: Error recovery, performance at scale, final details

#### Findings & Changes

| # | Finding | Change | Affected Section |
|---|---------|--------|-----------------|
| F17 | **No "resumable upload" for large files**. If connection drops during a 500MB upload, user must restart from 0. | Add chunked upload with resumability: split files >50MB into 5MB chunks, track completed chunks, resume from last successful chunk. Show "Resuming upload..." state. | 2.3 Upload Tab, Flow 2 |
| F18 | **Video grid pagination missing**. With 200+ videos per trick, loading all at once freezes the UI. | Implement virtual scrolling for video grid (render only visible rows). Load thumbnails lazily (Intersection Observer). "Load more" button at bottom or infinite scroll. | 2.3 Videos Tab |
| F19 | **Crawl form allows launching multiple concurrent crawls** for same trick. This creates duplicate data and wastes Instagram quota. | Disable "EXECUTE CRAWL" button if there's already a running/failed crawl job for this trick. Show banner: "A crawl job is already in progress. View status in System Jobs." | 2.3 Crawl Tab |
| F20 | **Training page doesn't prevent training with zero augmentable data**. User can click "START TRAINING" with 0 videos in training set. | "START TRAINING" button disabled when total training videos = 0. Shows tooltip: "Add videos to training set from the Tricks page." Minimum 2 classes also enforced with inline validation. | 3.3 Training Configuration |
| F21 | **Model Registry comparison doesn't handle incomplete runs**. Comparing a completed run with a failed run shows NaN/empty values. | Only allow comparing runs with status "done" or "active". Failed/running/rejected runs are not selectable for comparison. Show tooltip: "Only completed runs can be compared." | 4.2 Comparison Matrix |
| F22 | **No "bulk delete" for System Jobs history**. Old completed jobs accumulate with no cleanup. | Add "Clear History" button with date range filter (last 24h, last 7 days, all). Confirmation dialog with count: "Delete 142 completed job records? This cannot be undone." | 5.2 Completed Jobs |
| F23 | **Video editor "Center Trick" auto-analysis is unclear**. What does it analyze? How long does it take? | Add progress overlay during analysis: "Analyzing pose data... Detecting center of movement... (3s)". Show visual overlay of detected motion path during analysis. Result preview shows before/after split view. | 2.4 Video Editor |
| F24 | **Training readiness gauge has no "why" explanation**. Users see "42%" but don't know what's needed to reach 100%. | Click on gauge opens detail panel: "Required: 10,000 total windows. Current: 4,281. Missing: 5,719 from any accepted clips. Estimated clips needed: ~20 more clips." Actionable guidance. | 2.3 Stats Tab |

#### Iteration 3 Design Decisions

- **Offline mode acknowledgment**: No offline mode will be built (this is an internal tool, always-on network expected). However, the app handles disconnection gracefully with a reconnecting banner and preserved last-known state.
- **State URL sync**: Trick ID synced to URL query param (`/tricks?selected=trk-001`). Allows deep-linking and browser back/forward to work correctly with the two-panel layout.
- **Dark mode only**: No light mode toggle. Stitch design system is dark-only. Simplifies CSS token architecture.
- **Animation budget**: Minimal animations — only for feedback-critical interactions: progress bars (smooth), skeleton loading (shimmer), bulk bar slide-in (300ms ease-out). No page transitions or decorative animations.
- **Video processing indicator on thumbnails**: When a video is currently being processed by a background job, its thumbnail shows a pulsing blue border + "Processing..." label. Updates automatically when job completes via polling.

#### Final Component Count

| Page | Unique Components | Shared UI Components Used |
|---|---|---|
| Tricks | 9 (Dashboard, TrickCard, NewTrickDialog, VideoGrid, VideoCard, CrawlForm, UploadZone, MetricsPanel, VideoEditor) | Badge, Button, Card, Dialog, ProgressBar, Stepper, Table, DragDropZone, EmptyState, Toast, Chip, Icon, Input, Select |
| Training | 4 (TrainingConfig, DatasetSummary, ClassSelector, TrainingHistory) | Badge, Button, Card, Dialog, ProgressBar, Table, EmptyState, Toast, Chip |
| Model Registry | 4 (RunTable, ComparisonMatrix, RetrainDialog, ApproveDialog) | Badge, Button, Card, Dialog, Table, ProgressBar, Toast, Chip |
| System Jobs | 2 (JobCard, JobHistoryTable) | Badge, Button, Card, ProgressBar, Table, EmptyState, Toast, Chip |

**Total unique components**: 19  
**Total shared UI components**: 13  
**Total modals/dialogs**: 7 (NewTrickDialog, EditTrickDialog, ConfirmationDialog, VideoPlayerModal, VideoEditorModal, RetrainDialog, ApproveDialog)

---

## 11. Appendix: All Dialog/Modal Specifications

### 11.1 Confirmation Dialog
- **Props**: title (string), message (string), confirmLabel (string), confirmStyle ('primary'|'danger'), cancelLabel (string, default "Cancel"), onConfirm (callback), onCancel (callback)
- **Used by**: Flow 4 (Process Videos), Flow 7 (Delete Video), Flow 8 (Delete Trick), Flow 11 (Start Training), Flow 14 (Activate Model), Flow 15 (Approve Model), Flow 16 (Reject Model), Flow 19 (Cancel Job)

### 11.2 Create/Edit Trick Modal
- **Props**: mode ('create'|'edit'), trickData? (TrickClass, for edit), onSave (callback), onCancel (callback)
- **Width**: 480px
- **Height**: auto (max 80vh, scrollable)
- **Tabs**: None — single form

### 11.3 Video Player Modal
- **Props**: videoUrl (string), clipMetadata? (Clip), onAccept (callback), onReject (callback), onEdit (callback)
- **Width**: 90vw, max 1200px
- **Height**: 80vh

### 11.4 Video Editor Modal
- **Props**: videoUrl (string), currentConfig? (CutterConfig), onSave (callback), onCancel (callback)
- **Width**: 95vw, max 1400px
- **Height**: 85vh

### 11.5 Retrain Dialog
- **Props**: availableClasses (TrickClass[]), onStart (callback), onCancel (callback)
- **Width**: 560px

### 11.6 Approve Dialog
- **Props**: run (ModelRun), comparisonRun? (ModelRun), onApprove (callback), onCancel (callback)
- **Width**: 640px

### 11.7 Keyboard Shortcuts Dialog
- **Trigger**: "?" key
- **Content**: Table of shortcuts (Space=play/pause video, Left/Right=seek video, Esc=close modal, Ctrl+Enter=submit form)
- **Width**: 400px

---

*Document version: 3.0 | Iteration 3 (final) | 2026-08-05*
