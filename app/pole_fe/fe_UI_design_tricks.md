# `pole_fe` — Page 1: Tricks

> Shared design system: see `fe_UI_design_common.md`

## 2. Page 1: Tricks Page

### 2.1 Layout
Split view: Left panel = trick list (40%), Right panel = video list + actions (60%). On mobile/tablet: full-width trick list, click navigates to video detail.

### 2.2 Left Panel: Trick List

**Header row**: Title "TRICK_REGISTRY" with subtitle "Manage AI pose extraction classes and training pipelines." + "NEW TRICK" button (primary, icon: add_box).

**Filter bar**: Pill toggles: ALL | PROMOTED | CHROMA_ONLY | DRAFT. Toggle switch: "Promo Candidates only". Search input for filtering by name.

**Trick cards** (one per trick):
- TRK-ID (e.g., "TRK-001") + name (e.g., "handspring") as title row
- Hashtag chips below title (#gymnastics, #acrobatics)
- Status badge (top-right): PROMOTED, CHROMA_ONLY, DRAFT, FAILED
- Mini pipeline stepper (4 steps: INGEST → EXTRACT → TRAIN → PROMO)
- Action buttons row: edit (icon), delete (icon, danger), VIEW_DETAIL (chevron_right)
- Clicking the card or VIEW_DETAIL opens the right panel with that trick's videos
- Selected card has primary-container border highlight

**Empty state**: When no tricks exist, show empty state with "Create your first trick" CTA.

**Loading state**: 3 skeleton cards with shimmer animation.

### 2.3 Right Panel: Video Management (shown when a trick is selected)

**Header**: Breadcrumb "Tricks > {trick_name}", status badge, "EDIT DEFINITION" button.

**Tabs**:
1. **Videos** (default): Grid of non-clip videos for this trick (only `clip=false` videos)
2. **Clips**: Grid of clip videos (a video is a clip if `clip=true` or it is a crop child `kind='clip'`)
3. **Stats**: Dataset metrics (total samples, embedded/pending/trained windows, training readiness %, minimum threshold, chroma distribution)

**Videos Tab - Video Grid**:
- Thumbnail card per video (16:9 preview, edit button overlay)
- Status badge on each thumbnail (NEW / PROCESSED / READY)
- Checkbox for multi-select
- Status filter pills with per-filter counts (ALL, NEW, PROCESSED, ...)
- Bulk actions bar (appears when 1+ selected; content depends on whether the selected are clips):

**Bulk actions bar** (floating, bottom-center; appears when ≥1 video selected):
- Selection count ("N Videos Selected" or "N Clips Selected")
- If the selected items **are clips**:
  - **Clip** (toggle → unclip / move to video)
  - **Process** → opens Process Config modal (stride)
  - **Embed** → opens Embed Config modal (model)
  - **Training** (toggle ADD/REMOVE selected_for_training) → runs as a job
  - **Delete** (danger) → batch delete job
- If the selected items **are videos** (non-clips):
  - **Delete** (danger) → batch delete job
  - **Crop AI** → runs the AI cutter as a `cut` job on the selected videos
  - **Clip** (toggle → mark as clip)

> All bulk actions run as **background jobs** monitored in System Jobs and report a per-item
> Completed/Skipped/Failed summary. Only clips can be **processed, embedded, or added to training**
> (enforced server-side); non-clip videos are always `selected_for_training=false`.

**Config modals**:

1. **Process Config Modal** — title "Process Videos", single field "Slides (stride)" (number input, min 1, max 30, default 5), footer: "CANCEL" + "START PROCESSING". On confirm → `POST /api/training/classes/{id}/process` `{video_ids, stride}` (job). Requires clips.

2. **Embed Config Modal** — title "Create Embeddings", single field "Model" (select of generated LSTM runs). On confirm → `POST /api/training/classes/{id}/embed` `{video_ids, model_id}` (job). If no run selected, BE falls back to the configured `embedding_model_path`. Requires clips.

**Crawl Tab**:
- Form fields: Target Tags, Sample Limit, Min/Max Wait, "EXECUTE CRAWL" button → starts a crawl job
- Crawl history table below form (date, tags, limit, status, downloaded count)

**Upload Tab**:
- Drag & drop zone (accepts .mp4 only, max 10 files at once)
- Selected files list with name, size, remove button
- "UPLOAD & PROCESS" button
- Upload history below (filename, upload date, status)

**Stats Tab**:
- Total Samples card, Cleaned Samples card
- Training Readiness gauge (circular, %)
- Minimum Threshold bar
- Chroma Distribution bar chart
- "Retrain" button (if readiness is sufficient)

### 2.4 Video Editor Overlay (Client-side)

Opened from video action "Edit". Full-screen modal with:
- **Video player area (left 60%)**: Shows video. Timeline with start/end trim handles (draggable). Frame scrubber.
- **Edit controls (right 40%)**:
  - **Trim**: Start time input (mm:ss), End time input (mm:ss), "Apply Trim" button
  - **Crop/Shift**: X offset slider, Y offset slider, "Center Trick" auto-button (analyzes movement and centers), visual box overlay on video showing crop area, "Apply Crop" button
  - **Preview area**: Shows before/after comparison
- **Footer**: "Save Changes" (primary), "Discard Changes" (outlined), "Reset to Original" (ghost)
- Changes are applied client-side and sent as cutter_config when processing

### 2.5 Flows on Tricks Page

**Flow 1: Create New Trick**
1. User clicks "NEW TRICK" button
2. Modal opens titled "Create New Trick"
3. Form fields:
   - Trick Name (text input, required, validated for uniqueness)
   - Hashtags (tag input, required, must start with #, min 1)
   - Data Source toggle: "Upload Videos" | "Scrape from Instagram" (radio buttons)
   - Min Videos threshold (number, optional, default 5)
   - Min Windows threshold (number, optional, default 200)
   - Cutter Config (collapsible advanced section): FPS, Resolution Width, Resolution Height
4. "CREATE TRICK" button (primary) / "CANCEL" (ghost)
5. Creation runs as a **job** (`POST /api/training/classes/jobs` → `202 {job_id}`) tracked in System Jobs; trick appears in the list when the job completes
6. Validation errors (empty/reserved/duplicate name) are shown inline (immediate 4xx)

**Flow 2: Upload Videos to Existing Trick**
1. Select trick from left panel
2. Switch to Upload tab
3. Drag files onto drop zone or click to browse
4. Files appear in list with name, size, remove button
5. Click "UPLOAD & PROCESS"
6. Progress bar shows per-file upload progress
7. Job polling starts: progress bar shows processing status
8. On complete: videos appear in Videos tab, toast "Videos processed successfully"
9. On error: toast with error message, retry button

**Flow 3: Scrape Videos from Instagram**
1. Select trick from left panel
2. Switch to Crawl tab
3. Form pre-filled with trick's hashtags. Adjust tags/limit/waits.
4. Click "EXECUTE CRAWL"
5. Job starts: progress bar with label "Crawling Instagram..."
6. On complete: class status updates to awaiting_qc, notification "Crawl complete: N videos downloaded"
7. Navigate to QC Review (could be inline or separate route)

**Flow 4: Process Videos**
1. In Clips tab, select one or more clips via checkboxes
2. Bulk actions bar appears: click "Process"
3. Process Config modal opens with Slides (stride) input (default 5); must be an integer between 1 and 30
4. Click "START PROCESSING" → `POST /api/training/classes/{id}/process` `{video_ids, stride}` (job)
5. Job runs in System Jobs; on complete videos refresh
6. Non-clip videos are rejected (only clips can be processed)

**Flow 4b: Embed Videos**
1. In Clips tab, select clips via checkboxes
2. Bulk actions bar: click "Embed"
3. Embed Config modal opens with Model select (generated LSTM runs; value = run `model_path`)
4. Click "PROCESS" → `POST /api/training/classes/{id}/embed` `{video_ids, model_id}` (job)
5. Job runs in System Jobs; on complete video `embedding_models` updated

**Flow 5: Add/Remove videos for Training**
1. In Clips tab, select clips via checkboxes
2. Bulk actions bar: click "Training" (toggle)
3. If all selected are already selected-for-training → removes the flag; otherwise adds it
4. Runs as a job `POST /api/training/classes/{id}/promote` `{video_ids, selected}` (System Jobs)
5. Only clips can be added to training; non-clips and unprocessed clips are blocked

**Flow 5b: Toggle Clip flag**
1. Select videos or clips via checkboxes
2. Bulk actions bar: click "Clip" (toggle)
3. If any selected is not a clip → marks them as clips (`POST /api/training/classes/{id}/clip` `{video_ids, clip:true}`) → they move to the Clips tab
4. If all selected are clips → unclips them (`clip:false`, kind→video, clears `selected_for_training`) → they move to the Videos tab
5. Runs as a job (System Jobs); clips can be processed/embedded/trained, videos cannot

**Flow 6: Edit Video**
1. Click the edit button on a video/clip card
2. Video Editor overlay opens (manual per-video adjustment)
3. "Save Changes" / "Discard"

**Flow 7: Delete Video(s)**
1. Select one or more videos/clips via checkboxes
2. Bulk actions bar: click "Delete"
3. Confirmation dialog: "Delete N videos? This cannot be undone."
4. On confirm → `POST /api/video/videos/delete` `{video_ids}` (batch job, System Jobs)
5. Videos that still have child clips are skipped and reported; already-deleted files are irreversible

**Flow 8: Delete Trick**
1. Click delete icon on trick card
2. Confirmation dialog: "Delete this trick? ..."
3. On confirm → cascade-delete runs as a `delete_class` job (System Jobs); the list reloads when it completes

**Flow 9: Edit Trick Definition**
1. Click edit icon on trick card OR "EDIT DEFINITION" in right panel header
2. Modal opens with current values pre-filled (name, hashtags, thresholds, cutter_config)
3. Edit fields, "SAVE CHANGES" / "CANCEL"
4. On success: toast "Trick updated", list refreshes

---

*See also: fe_UI_design_common.md for design system, QA guidelines, and design iterations.*
