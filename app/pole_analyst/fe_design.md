# Pole AI Coach — Video Analysis Chatbot Web App (Light Theme)

## Design Overview

Generate a light-themed desktop web application called **"Pole AI Coach"** — a professional, athletic-feeling tool where a pole athlete uploads a training video and gets improvement feedback through a specialized AI coach. The interface is a clean two-column desktop layout with a slim top bar: a chat panel on the left where the user talks to the video-analysis coach, and a tools panel on the right for uploading videos, browsing their library, and reviewing detailed video analysis in tabs. The visual language is Angular/Material-inspired, accessible, calm, and readable, with generous spacing, a pleasant accent color, and clear tab navigation.

---

## Layout

Generate a desktop web application viewport (roughly 1440×900), light background. Structure it as a full-height two-pane split beneath a slim top bar:

- **Slim top bar (full width, ~56px tall):** white background with a subtle bottom border. Left side shows the product name "Pole AI Coach" with a small athletic glyph or icon, plus a one-line subtitle: "AI video analysis for pole athletes." Right side shows a small circular user avatar and a minimal settings icon.
- **Main content area** below the top bar is split vertically into two columns with a thin divider:
  - **Left pane — Chat:** approximately 40% width. Holds the conversation with the Coach.
  - **Right pane — Tools:** approximately 60% width. Holds the video library/upload and the video detail tabs.
- Ensure both panes scroll independently and keep consistent 16–24px padding and an 8px grid for spacing.

---

## Left Pane — Chat

Generate a chat interface labeled with a header reading **"Coach"**. Below the header, include a subtle subtitle: "Your video-analysis coach — upload a video and ask for feedback."

- **States indicator:** Next to the header (near the coach's name), render a small status chip that communicates the coach's current state. Show it with a dot and a label, for example: **Idle** (gray dot), **Thinking** (amber dot, optionally with three animated dots), **Working / Analyzing** (blue dot with a small spinner), **Completed** (green check), or **Error** (red dot). Make the chip visually distinct and always visible near the top of the chat.
- **Message list:** A scrollable conversation area with alternating bubbles:
  - **User messages:** right-aligned, filled with a soft accent-tinted background, rounded corners, readable dark text.
  - **Assistant messages:** left-aligned, white cards with a light border and subtle shadow, prefixed with a small coach avatar/icon. Assistant messages are rendered in a structured, easy-to-scan way (headings, bullet lists, and inline "chips" for metrics such as phase durations, critical frame, and max z-score).
  - Include a sample conversation showing the user asking "Can you analyze my video 'invert_practice.mp4'?" and the coach replying with a structured improvement summary.
- **Composer input:** At the bottom of the left pane, a rounded text input with placeholder text like "Ask about your video…" and a circular **send** button with an arrow icon. Optionally include a small paperclip/attach icon inside the input to indicate video attachment capability.

---

## Right Pane — Video Library (default mode)

Generate the default state of the right pane as a **video library / upload tool**, titled **"My Videos"**:

- **Upload control:** A prominent dashed-border drop zone spanning the top of the pane, with a centered cloud-upload icon, the text "Drag & drop a video here, or **Upload video**," and a solid accent-colored "Upload video" button. Mention supported formats (e.g., "MP4, MOV — up to 200 MB").
- **Search bar:** Below the upload zone, a rounded search input with a magnifier icon and placeholder "Search videos…".
- **Video list/grid:** Render a responsive grid of video cards (2 columns). Each card shows:
  - A **video thumbnail** with a play-button overlay.
  - The **filename** (bold, truncated with ellipsis).
  - The **upload date** (small, muted gray text).
  - A clear **status badge**: a green pill labeled "Analyzed" or a neutral gray pill labeled "Not analyzed."
  - A contextual action button: **"Analyze"** (accent-outlined) for videos that are not analyzed, or **"Open analysis"** (solid accent) for videos that are analyzed.
- Show a mix of analyzed and not-analyzed cards in the sample to demonstrate both states clearly.

---

## Right Pane — Video Detail Tabs

Generate the video-detail mode, shown after the user clicks an analyzed video. Render a **tab bar** near the top of the right pane with four clearly separated tabs: **Summary, Histogram, Pose, Plan**, with the active tab visually highlighted (accent underline or filled pill) and inactive tabs in muted text.

- **Summary tab (active by default):** A header showing the video name and trick type (e.g., "Invert — Advanced"). Below it, a row of **metric cards** displaying: **Phase durations** (e.g., "Entry 0.4s · Hold 1.2s · Exit 0.6s"), **Critical frame/phase/metric** (highlighted value), and **Max z-score** (with a small trend indicator). Include a short paragraph summarizing the overall assessment.

> **Backend contract — Summary tab (Phase 12).** The Summary tab is fed by the read-only
> endpoint `GET /api/tools/histograms/summary/{video_id}` (no recompute; returns the stored
> per-video summary verbatim; `404` when the histogram or the summary is absent — "run
> histograms/analysis first"). Response shape:
>
> ```json
> {
>   "video_id": "…", "trick_label": "…",
>   "z_mean": { "<metric>": 0.42, "…": "…" },
>   "scores": { "<metric>": 81.0, "…": "…" },
>   "detections": [
>     { "index": 152, "phase": "execution", "metric": "vertical_speed",
>       "z_score": 2.3, "frame": 58, "frame_image_path": "/abs/…/frame_58.jpg" }
>   ],
>   "critical_frame": 58, "critical_phase": "execution", "critical_metric": "vertical_speed"
> }
> ```
>
> **Contract notes for the FE:**
> - Phase names are **lowercase**: `init` / `execution` / `exit` (the old
>   `ENTRANCE`/`EXECUTION`/`EXIT` naming from the removed `analyze` endpoint is gone; the
>   Summary tab maps them to the Entry/Hold/Exit labels).
> - `scores` are per-metric 0-100 (100 = cohort mean); `z_mean` is **signed** and retained for
>   directional feedback; `detections` list every point with `|z| > 1`, each with an absolute
>   `frame` and an **optional** `frame_image_path` (may be absent if frame extraction failed).
> - `critical_frame`/`critical_phase`/`critical_metric` are optional (present only when
>   detections exist).
> - No-summary state: a `404` with `{"detail": "summary not available for '<video_id>'; run
>   histograms/analysis first"}` means the video has not been analyzed yet — the tab renders a
>   "not analyzed yet" state with a CTA to run `histograms/analysis`.
- **Histogram tab:** A clean bar/area **histogram chart** titled "Trick-Metric Distribution," with labeled axes, a highlighted marker on the current video's metric value, and a legend. The chart is crisp, light, and accessible with visible axis labels.
- **Pose tab:** Show an **annotated frame** from the user's video — a still image of the athlete mid-trick with a **skeleton overlay** (connected joint points and bones drawn over the body) and **correction hints** (small arrows, callouts, or colored markers pointing to areas to adjust, with short labels like "Straighten back" or "Raise hip").
- **Plan tab:** Render an **improvement plan** as an ordered list of advice steps (e.g., "1. Increase hold time by 0.3s…"), plus a separate "Detected errors" card listing specific issues with severity indicators (warning/error icons and short descriptions).

---

## Visual Style

Generate the interface with a **light theme** and a professional, athletic, accessible feel:

- **Color palette:** A clean white/off-white background (#FFFFFF / #FAFBFC), dark slate text (#1F2937), a calm **accent color** (e.g., a deep teal or indigo-blue) used consistently for primary buttons, active tabs, and links, with a soft tinted version of the accent for backgrounds of selected items and user bubbles. Use semantic colors sparingly: green for "Analyzed"/success, amber for "Thinking"/warning, red for errors.
- **Typography:** Use a clean, readable sans-serif (Material-style) with clear hierarchy — bold section headers, medium-weight labels, and regular body text. Maintain comfortable line spacing.
- **Components:** Rounded corners (8–12px), subtle borders and shadows, clear focus states, and consistent spacing on an 8px grid.
- **Tabs and navigation:** Clear tab navigation with visible active/inactive states and smooth, understandable transitions between the library and detail modes.
- **Accessibility:** Ensure strong color contrast, visible labels on all icons, and clear hover/focus affordances.

---

## States & Empty States

Generate the following states to make the flow coherent:

- **No video selected (empty right panel):** Show a friendly empty state in the right pane — a centered illustration or icon (e.g., a film/video glyph), the message "No video selected," and a hint: "Upload a video or pick one from your library to get started." Include a subtle "Upload video" button.
- **Analysis in progress:** Show a loading state synced to the coach's **Working/Analyzing** state — a card in the library with a spinner overlay and the label "Analyzing…", while the chat status chip shows "Working/Analyzing" with a spinner. Optionally show skeleton placeholders where metric cards will appear.
- **Error state:** Show a red-tinted card or banner in the chat and/or detail pane when analysis fails, with a clear error message and a "Retry" action.

Ensure all screens are consistent, fully wired visually, and produce one coherent, self-contained desktop app design.
