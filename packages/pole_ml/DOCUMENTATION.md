# Pole AI - Skeleton Data Processing System

## Project Overview

This system processes video data to extract human skeleton poses using MediaPipe Pose and stores the results in MongoDB for further analysis and machine learning training. The system is designed for pole dance motion recognition, with special considerations for handling occlusions and ensuring robust performance.

## System Architecture Flow Diagram

```
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
│   Video Input   │───▶│  SkeletonExtractor  │───▶│ ProcessingPipeline   │
│                 │    │                     │    │                      │
│  OpenCV Video   │    │  MediaPipe Pose     │    │  Sliding Window      │
│  Frames         │    │  Detection          │    │  Processing          │
└─────────────────┘    └─────────────────────┘    │                      │
                                        │    │  Biomechanical       │
                                        │    │  Feature Extraction  │
                                        │    │                      │
                                        │    │  LSTM Embedding      │
                                        │    │  Conversion           │
                                        │    │                      │
                                        └───────────────────────┘
                                                       │
                                                       ▼
                                          ┌──────────────────────┐
                                          │   SkeletonStorage    │
                                          │                      │
                                          │ MongoDB Storage      │
                                          │                      │
                                          └──────────────────────┘
```

## Component Flow Diagram

```
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
│   Video Input   │───▶│  SkeletonExtractor  │───▶│ WindowRepository     │
│                 │    │                     │    │                      │
│  OpenCV Video   │    │  MediaPipe Pose     │    │  MongoDB Access      │
│  Frames         │    │  Detection          │    │                      │
└─────────────────┘    └─────────────────────┘    └──────────────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────────┐
                           │ ProcessingPipeline          │
                           │                             │
                           │  Sliding Window             │
                           │  Processing                 │
                           │  Feature Extraction         │
                           │  Embedding Conversion       │
                           └─────────────────────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────────┐
                           │ SkeletonRepository          │
                           │                             │
                           │ ChromaDB Storage            │
                           │                             │
                           └─────────────────────────────┘
```

## Architecture

The system follows a modular architecture with three main components:

1. **SkeletonExtractor**: Handles pose detection from video frames
2. **ProcessingPipeline**: Manages the sliding window processing of skeleton data  
3. **SkeletonStorage**: Handles storage and retrieval of processed data in MongoDB

### Component Interactions

```
[Video Input] → [SkeletonExtractor] → [ProcessingPipeline] → [SkeletonStorage]
     ↓              ↓              ↓              ↓
  MediaPipe    Sliding Window   Data Formatting   MongoDB
   Pose         Processing       & Normalization
```

## Data Structure

### Raw Video Data Flow
1. **Frame-level data**: Each frame contains:
   - `frame`: Frame number in video
   - `timestamp`: Time in seconds from video start
   - `landmarks`: 33 pose landmarks with (x, y, z, visibility) coordinates
   - `visibility_count`: Number of visible landmarks

2. **Window-level data**: Processed sliding windows:
   - `window_id`: Unique identifier for the window
   - `window_start`: First frame number in window  
   - `window_end`: Last frame number in window
   - `frames_in_window`: Total frames in window
   - `landmarks`: List of landmark arrays from each frame in window
   - `timestamps`: Time stamps for each frame in window
   - `visibility_count`: Visibility count from first frame
   - `features`: Computed biomechanical features from landmarks
   - `label`: Classification label for the window (if available)
   - `processed_at`: Timestamp when data was processed

### Landmark Structure
Each landmark is a 4-tuple: `(x, y, z, visibility)`
- `x, y, z`: 3D coordinates normalized to the range [0,1] 
- `visibility`: Confidence score between 0 and 1 (0 = not visible, 1 = fully visible)
- Landmarks with visibility below threshold are filtered out and set to `None`

### MongoDB Storage Schema

```json
{
  "video_id": "string",
  "frame": integer,
  "timestamp": float,
  "landmarks": [
    [x, y, z, visibility],  // 33 landmarks
    ...
  ],
  "visibility_count": integer,
  "processed_at": datetime
}
```

## Class Features and Functionalities

### SkeletonExtractor Class
**Features:**
- Pose detection from video frames using MediaPipe Pose
- Landmark extraction with (x, y, z, visibility) coordinates
- Visibility filtering with configurable threshold (default: 0.7)
- Normalization of coordinates relative to hip center
- Support for occlusion handling in pole dance movements

**Functionalities:**
- `extract_pose(frame)`: Extract pose landmarks from a single frame
- `process_video(video_path)`: Process entire video and return skeleton data
- `normalize_coordinates(landmarks)`: Normalize landmark positions
- `filter_visibility(landmarks)`: Filter landmarks based on visibility score

### ProcessingPipeline Class
**Features:**
- Sliding window processing of skeleton data
- Biomechanical feature extraction from pose landmarks
- Integration with LSTM embedding conversion
- Support for configurable stride intervals
- Window-based data organization for sequence analysis

**Functionalities:**
- `process_sliding_window(video_data)`: Process video data in sliding windows
- `extract_biomechanical_features(landmarks)`: Compute motion features from landmarks
- `save_windows_embeddings()`: Convert window data to embeddings and store in repository
- `calculate_stride_interval()`: Calculate optimal frame stride for processing

### WindowRepository Class
**Features:**
- Specialized access to window data from MongoDB
- Efficient querying of window data by video_id
- Error handling with dedicated error logging
- Integration with processing pipeline components

**Functionalities:**
- `get_windows_by_video(video_id)`: Retrieve all windows for a specific video
- `get_all_windows()`: Retrieve all windows in the database
- `save_window(window_data)`: Save a single window to MongoDB
- `get_window(window_id)`: Retrieve a specific window by ID
- `log_processing_error(error_info)`: Log processing errors to dedicated collection

### SkeletonRepository Class
**Features:**
- ChromaDB-based vector storage for skeleton embeddings
- Support for storing and retrieving vector data with metadata
- Integration with prediction and retrieval functionality
- Efficient storage and search capabilities for machine learning training

**Functionalities:**
- `save_vector(vector, metadata)`: Save a vector with associated metadata
- `predict(vector, top_k=5)`: Find similar vectors in the repository
- `get_all_samples()`: Retrieve all stored samples
- `delete_sample(sample_id)`: Delete a specific sample
- `verify_collection()`: Verify collection integrity and consistency
- `save_invalid_vector()`: Handle invalid vector data gracefully

## Data Conversion Process

### 1. Pose Detection
- Input: Video frames from OpenCV
- Output: 33 pose landmarks per frame
- Each landmark includes coordinates and visibility score

### 2. Visibility Filtering  
- Landmarks with visibility < 0.7 are filtered out
- Only windows with ≥10 visible landmarks are processed
- Filtered landmarks are set to `None` for invalid points

### 3. Normalization
- Coordinates are normalized relative to hip center
- Scaling factor based on shoulder width
- All coordinates scaled to [0,1] range

### 4. Sliding Window Processing
- Frames processed at stride interval (default: every 5th frame)
- Windows contain sequential frames for LSTM processing
- Each window stored as separate document with metadata

### 5. Storage
- Data stored in MongoDB with unique identifiers
- Documents indexed by video_id and window_id for efficient querying
- Timestamps and metadata preserved for analysis

## Window Repository

A new `WindowRepository` class has been implemented to handle specialized access to window data from MongoDB. This repository provides methods to retrieve and store window data that is used in the embedding conversion process.

### Methods:
- `get_windows_by_video(video_id)`: Returns all windows associated with a specific video
- `get_all_windows()`: Returns all windows in the database
- `save_window(window_data)`: Saves a single window to the database
- `get_window(window_id)`: Retrieves a specific window by ID

### Error Handling:
When processing windows fails, errors are logged to a separate `processing_errors` collection in MongoDB with:
- `window_id`: The ID of the failed window
- `video_id`: The video associated with the failed window  
- `error_message`: Description of the error that occurred
- `timestamp`: When the error occurred

## Processing Pipeline Integration

The `ProcessingPipeline` class now includes a `save_windows_embeddings` method that:
1. Uses `WindowRepository` to retrieve all windows from MongoDB
2. Processes landmarks and biomechanical features using `SkeletonEmbeddings`
3. Stores resulting vectors in `SkeletonRepository` along with metadata
4. Handles errors gracefully by logging them to the processing_errors collection

## Code Organization

```
packages/pole-train-model/
├── pole_ml/                          # (renamed from src/ml)
│   ├── classifiers/                  # LSTMClassifier, ChromaClassifier, HybridClassifier
│   ├── models/                       # ModelTrainer, ModelPersistence, ModelEvaluator, ModelData, VideoLSTMTrainer
│   ├── processors/                   # skeleton_extractor, processing_pipeline, skeleton_embedding, data_augmentation
│   └── repositories/                 # storage(Mongo), window_repository, video_repository, skeleton_repository(ChromaDB)
├── pole_tools/                       # (renamed from src/tools)
│   ├── process_data.py, train_model.py, process_embeddings.py, evaluate_video.py, video_cutter.py
├── models/                           # MediaPipe model + LSTM checkpoints
├── config/                           # VideoCutter YAML properties
├── docs/                             # Documentation (this file)
└── tests/                            # Unit tests
```

> **Note:** Earlier documentation referenced a flat layout (`ml/skeleton_extractor.py`,
> `ml/storage.py`) and a `src/` layout. The canonical structure is namespaced under
> `pole_ml/processors`, `pole_ml/models`, `pole_ml/classifiers`, and `pole_ml/repositories`,
> with CLI tools under `pole_tools`. See `AGENTS.md` for the current reference layout.

## Database Schema Details

### Collections
- `skeleton_data`: Stores processed skeleton data with window metadata
- `processing_progress`: Tracks processing status and progress
- `processing_errors`: Stores information about failed window processing operations

### Key Fields
- `video_id`: Unique identifier for the source video
- `window_id`: Sequential identifier for sliding windows
- `frame`: Frame number in original video
- `timestamp`: Time in seconds from video start
- `landmarks`: 33x4 array of normalized coordinates and visibility scores
- `visibility_count`: Number of visible landmarks (0-33)
- `processed_at`: Timestamp when data was processed

## Configuration Parameters

### Visibility Threshold
- Default: 0.7 (landmarks with visibility < 0.7 are filtered out)

### Processing Stride
- Default: 5 (process every 5th frame to reduce computational load)

### Window Size
- Configurable parameter for LSTM input sequences

## Error Handling and Fallback Mechanisms

The system implements robust error handling with fallback mechanisms:

1. **Database Fallback**: If MongoDB is not available or has no data, the training process will automatically use mock training data to ensure completion.
2. **Graceful Degradation**: All components include proper exception handling to prevent crashes during processing.
3. **Logging**: Comprehensive logging throughout the pipeline for debugging and monitoring purposes.
4. **Error Tracking**: Failed window processing operations are logged to a dedicated `processing_errors` collection.

## Model Training Implementation

### LSTM Model Architecture

The pole dance recognition system uses a specialized LSTM model architecture optimized for motion sequence analysis:

#### Model Components
1. **Input Layer**: Accepts windowed sequences of normalized skeleton data (30 frames × 132 features)
2. **LSTM Layers**: Three stacked LSTM layers with CuDNN optimization for GPU acceleration
3. **Dropout Layers**: Regularization to prevent overfitting  
4. **Output Layer**: Classification layer for pole dance movement types

#### Training Process Flow Diagram

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  Windowed Sequences │───▶│ SkeletonEmbeddings   │───▶│  SkeletonRepository │
│  (30 frames × 132)  │    │  Conversion          │    │  Storage            │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
        │                           │                          │
        ▼                           ▼                          ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  Processed Windows  │───▶│  Vector Embeddings   │───▶│  Training Data      │
│  (from MongoDB)     │    │  (33 landmarks × 4)  │    │  for Model          │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
        │                           │                          │
        ▼                           ▼                          ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  Feature Extraction │───▶│  ChromaDB Storage    │───▶│  Model Training     │
│  (Biomechanical)    │    │  (Vectors + Metadata)│    │  Process            │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

#### Training Pipeline Steps
1. **Data Preparation**: Retrieve windowed sequences from MongoDB using `WindowRepository`
2. **Embedding Conversion**: Convert landmark data to vectors using `SkeletonEmbeddings`
3. **Storage**: Store embeddings in `SkeletonRepository` with metadata
4. **Model Training**: Train LSTM model on stored embeddings with appropriate validation techniques

### Embedding Process Flow

```
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   Landmarks     │───▶│  SkeletonEmbeddings │───▶│  Vector Storage  │
│  (33 × 4)       │    │  Conversion         │    │  (ChromaDB)      │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
        │                       │                         │
        ▼                       ▼                         ▼
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Normalized     │───▶│  Feature Extraction │───▶│  Metadata        │
│  Coordinates    │    │  (Biomechanical)    │    │  (video_id,      │
└─────────────────┘    └─────────────────────┘    │   window_id,     │
                                                    │   timestamp)     │
                                                    └──────────────────┘
```

### Training Data Flow

```
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Video Input    │───▶│  SkeletonExtractor  │───▶│  Processing      │
│                 │    │                     │    │  Pipeline        │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
        │                       │                         │
        ▼                       ▼                         ▼
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Frame Data     │───▶│  Window Processing  │───▶│  Window Storage  │
│  (33 landmarks) │    │                     │    │  (MongoDB)       │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
        │                       │                         │
        ▼                       ▼                         ▼
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Window Data    │───▶│  Embedding          │───▶│  Repository      │
│  (30 frames)    │    │  Conversion         │    │  Storage         │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
        │                       │                         │
        ▼                       ▼                         ▼
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Vector Data    │───▶│  ChromaDB Storage   │───▶│  Model Training  │
│  (132 features) │    │                     │    │  Process         │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
```

### Key Training Components

**SkeletonEmbeddings Class**
- Converts landmark data to vector representations
- Implements biomechanical feature extraction from pose landmarks  
- Handles normalization and standardization of features
- Generates embeddings suitable for LSTM model training

**Training Process Integration**
1. **Data Retrieval**: `WindowRepository` retrieves processed windows from MongoDB
2. **Feature Conversion**: `SkeletonEmbeddings` converts landmark data to numerical vectors
3. **Storage**: Vectors stored in `SkeletonRepository` with metadata for training
4. **Model Training**: LSTM model trained on vector embeddings with appropriate labels
5. **Validation**: Cross-validation techniques applied to ensure robust performance

The training pipeline leverages the structured data flow from raw video input through pose extraction, window processing, feature embedding, and finally model training - all integrated seamlessly with the repository storage system for efficient data management.

## New Window Repository Implementation

The new `WindowRepository` class provides specialized access to window data and enables the processing pipeline to:
1. Retrieve windows from MongoDB efficiently
2. Process them through the embedding conversion pipeline
3. Handle errors gracefully without stopping the entire process
4. Maintain clear separation of concerns between data access and processing logic

This implementation replaces some functionality previously handled by `SkeletonStorage` for window data specifically, while maintaining compatibility with existing storage operations.