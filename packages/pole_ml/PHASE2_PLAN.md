---
name: implement-phase-2-data-prep
description: Plan for implementing Phase 2 (Data Preparation) of the Pole AI Motion Analysis System.
metadata:
  type: project
---

# Implementation Plan: Phase 2 - Data Preparation

## Context
Phase 1 extracts skeleton landmarks and `move_name` (labels) from videos and stores them in MongoDB. Phase 2 transforms these frame-level skeletons into temporal "windows" ($W=30, S=5$). The processed window vectors will be stored in **ChromaDB** for similarity search, while all associated metadata (excluding the landmarks themselves) will be persisted in **PostgreSQL**.

## Objectives
1. Implement a sliding window algorithm to create 30-frame sequences.
2. Apply labeling strategies (Majority Vote and Central Frame) using existing frame-to-label mapping.
3. Implement a dual-storage pipeline:
    - **ChromaDB**: Store high-dimensional vectors representing the windows.
    - **PostgreSQL**: Store metadata (video ID, timestamps, labels, etc.) linked to the ChromaDB embeddings.

## Proposed Approach

### 1. New Modules
#### `ml/window_processor.py`
The core engine for segmentation.
- **Input**: Skeleton data streams from MongoDB.
- **Logic**:
    - Iterate through frames with step $D=5$.
    - Construct a 30-frame window $[i, i+29]$.
    - Aggregate landmarks into a flattened vector (the "embedding" input).
- **Labeling**:
    - **Majority Vote**: Determine window label from the mode of `move_name` in the window.
    - **Central Frame**: Use `move_name` from frame $i+14$.

#### `ml/database_manager.py` (New)
Handles the dual-storage orchestration.
- **PostgreSQL Manager**: Creates/updates tables for metadata (e.g., `window_metadata` table with columns: `id`, `video_id`, `start_frame`, `end_frame`, `label`).
- **ChromaDB Manager**: Handles insertion of the window vectors into ChromaDB, using the PostgreSQL primary key as a reference.

### 2. The Pipeline: `ml/data_pipeline.py`
The main execution flow:
1.  **Extraction**: Fetch skeleton sequences from MongoDB.
2.  **Segmentation**: Run `window_processor` to generate windows and labels.
3.  **Vectorization**: Flatten the 30-frame landmarks into a single vector.
4.  **Persistence**:
    - Write metadata to PostgreSQL.
    - Insert vectors into ChromaDB with associated metadata IDs.

### 3. Verification Plan
- [ ] **Unit Test**: `window_processor` correctly generates windows and handles edges (start/end of video).
- [ ] **Integration Test**: Complete run from MongoDB extraction to ChromaDB insertion.