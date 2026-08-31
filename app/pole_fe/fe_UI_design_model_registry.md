# `pole_fe` — Page 3: Model Registry

> Shared design system: see `fe_UI_design_common.md`

## 4. Page 3: Model Registry

### 4.1 Purpose
View all trained models, their statistics, training status, and select which model is active for production use.

### 4.2 Layout

**Header**: Title "MODEL REGISTRY" with tabs: MANAGE | TRAIN | EVALUATE | DEPLOY

**Active Model Banner** (if exists):
- Card at top with blue accent border
- "ACTIVE MODEL: {run_id}" with model details
- "CHANGE ACTIVE MODEL" button

**Main Content: Execution Log Table**

Table columns:
- **Run ID**: Format #R-XXXX, badges: "LATEST" (blue), "DEPLOYED" (green)
- **Mode**: "Fine-tune" or "Retrain_Full" with icon
- **Classes**: Chips showing included classes
- **Status**: Colored chips - COMPLETED (green), RUNNING (blue with spinner), FAILED (red), ARCHIVED (grey)
- **Accuracy**: Percentage with trend arrow (up green, down red) compared to previous run
- **Loss**: Value with trend arrow
- **Created**: Relative time ("2h ago", "3d ago")
- **Actions**: View Details (eye icon), Activate (if completed, not active), Approve (if awaiting_approval), Reject, Archive

**Training in Progress Row** (if active training job):
- Highlighted row with blue background
- Shows epoch progress: "EPOCH 14/50" with spinner
- Loss/accuracy update in real-time (polling)

**Comparison Matrix** (bottom section):
- Select 2 runs to compare
- Side-by-side panels: Run A vs Run B
- Metrics compared: Val Accuracy (+1.3% ▲ or -0.5% ▼), Val Loss, Confusion Matrix Delta
- Highlight: "Run #R-0892 passes all strict evaluation gates. Performance delta is positive."
- "APPROVE & ACTIVATE" button (primary, large)

### 4.3 Flows on Model Registry

**Flow 13: View Run Details**
1. Click "View Details" on a run row
2. Detail panel opens (slide-in from right or expand row):
   - Full metrics (accuracy, precision, recall, F1, confusion matrix)
   - Classes included with per-class accuracy
   - Training parameters used
   - Model file path
   - Created date, training duration
3. "CLOSE" button

**Flow 14: Activate Model**
1. Click "Activate" on a completed run
2. Confirmation dialog: "Set {run_id} as the active model? This will be used for video cutting and all inference services."
3. "ACTIVATE" / "CANCEL"
4. On confirm: model becomes active, badge updates, toast confirmation
5. Previous active model becomes "archived" (or deactivated)

**Flow 15: Approve Model (after retraining)**
1. Run with status "awaiting_approval" appears in table
2. User reviews metrics (View Details)
3. User compares with active model (Comparison Matrix)
4. If satisfied: click "APPROVE & ACTIVATE"
5. Confirmation dialog: "Approve and activate this model? It will replace the current active model."
6. "APPROVE" / "CANCEL"
7. On confirm: model becomes active, previous active archived, associated class promoted

**Flow 16: Reject Model**
1. Click "Reject" on awaiting_approval run
2. Confirmation: "Reject this training run? The model will be discarded."
3. "REJECT" / "CANCEL"
4. On confirm: run status → rejected, class returns to chroma_only

**Flow 17: Archive Old Model**
1. Click "Archive" on an old completed model
2. Confirmation: "Archive {run_id}? It will remain stored but won't appear in the active list."
3. "ARCHIVE" / "CANCEL"

---

*See also: fe_UI_design_common.md for design system, QA guidelines, and design iterations.*
