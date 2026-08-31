# `pole_fe` — Page 4: System Jobs

> Shared design system: see `fe_UI_design_common.md`

## 5. Page 4: System Jobs

### 5.1 Purpose
Monitor all background tasks (crawling, cutting, processing, training, uploading) across all slices in real-time.

### 5.2 Layout

**Header**: Title "SYSTEM JOBS" with subtitle "Monitor all background processing tasks in real-time."

**Filter bar**: Slice filter pills (All | Crawler | Training | Video).

**Active Jobs Section** (if any running/pending):
- Job cards in a grid (2 columns) showing:
  - Job ID (truncated)
  - Slice badge (crawler=orange, training=blue, video=purple)
  - Entity (trick name or model run ID)
  - Progress bar with percentage
  - Status text ("Running" / "Queued")
  - **Stop** button (danger) — cancels the running job and rolls back the work done

**History Section** (collapsible, always open when non-empty):
- Sorted by **Date** (most recent first)
- Table with columns: Job, Kind, Entity, Status, **Date** (`dd-mm-yyyy HH:MM:ss.mmm`), Description
- Description shows the per-item result summary: `Completed N, Skipped N, Failed N — skipped <id>: <reason>; failed <id>: <reason>; …` and for create jobs `created <name>`
- Status: Done (green), Stopped (outline), Failed (red) — stopped shows the rollback message

**Empty State**: "No active jobs. System is idle." with check_circle icon.

### 5.3 Flows on System Jobs

**Flow 18: Monitor Active Job**
1. Job card appears in Active section when any background task starts
2. Progress bar updates in real-time (polling)
3. When done: card moves to History with Done status + per-item description

**Flow 19: Stop (Cancel) Job**
1. Click "Stop" on a running/pending job card
2. Confirmation: "Stop this job and revert the work already done?"
3. On confirm: `POST /api/{slice}/jobs/{id}/cancel` sets a cooperative cancellation flag
4. The worker stops between items and **rolls back** its side effects (windows, embeddings, training/clip flags, created class/clips, downloads/uploads)
5. Card moves to History with **Stopped** status + description of what was reverted
6. Note: physical files already deleted by a delete job are not restored (reported as irreversible)

**Flow 20: Job completion / failure / stop notifications**
- Done / failed / stopped jobs raise a notification (bell badge + panel).

**Flow 21: View Job History**
1. History table sorted by date (most recent first)
2. Date column shows `dd-mm-yyyy HH:MM:ss.mmm`
3. Description column shows the per-item Completed/Skipped/Failed summary with reasons

---

*See also: fe_UI_design_common.md for design system, QA guidelines, and design iterations.*
