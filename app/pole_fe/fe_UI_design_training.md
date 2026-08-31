# `pole_fe` — Page 2: Training

> Shared design system: see `fe_UI_design_common.md`

## 3. Page 2: Training Page

### 3.1 Purpose
Configure and trigger model training/retraining. This page does NOT manage videos (that's done on Tricks page). It shows which videos are marked for training across all tricks and handles the training job submission.

### 3.2 Layout

**Header**: Title "TRAINING STUDIO" with subtitle "Configure model architecture and launch training jobs."

**Two-column layout**:
- Left (60%): Training Configuration
- Right (40%): Training Dataset Summary

### 3.3 Training Configuration (Left Panel)

**Mode Selection** (card):
- Radio cards (not just radio buttons - visual cards):
  - "TRAIN FROM SCRATCH" card: Icon model_training, description "Build a completely new LSTM model. All weights initialized randomly. Requires more data and time."
  - "FINE-TUNE EXISTING" card: Icon tune, description "Start from an existing model and adapt it. Faster convergence, less data required."
- When "FINE-TUNE EXISTING" selected: dropdown to select base model from registry

**Class Selection** (card):
- Multi-select list of all tricks that have training_ready videos
- Checkbox per trick, shows: trick name, video count (training_ready / total)
- "Select All" / "Deselect All" toggles
- Minimum: must select at least 2 classes (including "transition" if applicable)
- Warning if only 1 class selected: "At least 2 classes needed for classification"

**Training Options** (card):
- Data Augmentation toggle (boolean, default true)
- Re-embed toggle (boolean, default true) - re-compute embeddings after training
- Stride input (number, optional) - window stride for data processing

**Action bar**:
- "START TRAINING" button (primary, large, icon: play_arrow)
- "SAVE CONFIGURATION" button (outlined) - saves for later
- Both disabled if no classes selected or no videos in training set

### 3.4 Training Dataset Summary (Right Panel)

**Summary cards row**:
- Total Videos in Training Set (number, icon: video_library)
- Total Classes (number, icon: category)
- Estimated Training Time (calculated, icon: schedule)
- Data Balance Warning (if any class has <10 videos)

**Per-class breakdown** (table):
- Class name | Video count | Status (ready/insufficient) | Min threshold met? (check/cross)

**Sample preview** (optional): Thumbnail grid of random training videos

**Warning states**:
- Yellow banner if class imbalance detected: "Class 'handspring' has 50 videos while 'shouldermount' has only 5. Consider adding more data for balanced training."
- Red banner if no videos in training set: "No videos selected for training. Go to Tricks page to add videos to the training set."

### 3.5 Flows on Training Page

**Flow 10: Train New Model from Scratch**
1. Select "TRAIN FROM SCRATCH" mode
2. Select classes for training (checkboxes from available classes)
3. Configure options (augmentation, re-embed, stride)
4. Review dataset summary on right - ensure all classes have sufficient data
5. Click "START TRAINING"
6. Confirmation dialog: "Start training new model with N classes and M videos? This may take several hours."
7. "START" / "CANCEL"
8. Job starts: progress bar with "Training epoch X/Y" label, loss/accuracy updates
9. On complete: toast "Training complete", redirect to Model Registry to review/approve results
10. On error: error message with details, retry button

**Flow 11: Fine-tune Existing Model**
1. Select "FINE-TUNE EXISTING" mode
2. Select base model from dropdown (shows model run ID, date, accuracy)
3. Select additional classes to add
4. Configure options
5. Click "START TRAINING"
6. Confirmation: "Fine-tune model {run_id} with N new classes?"
7. Job starts, progress shown
8. On complete: redirect to Model Registry

**Flow 12: Clear Training Selection**
1. User wants to reset all training selections
2. "CLEAR ALL" button in dataset summary
3. Confirmation: "Remove all videos from training set? Videos will remain but won't be used for this training run."
4. "CLEAR" / "CANCEL"

---

*See also: fe_UI_design_common.md for design system, QA guidelines, and design iterations.*
