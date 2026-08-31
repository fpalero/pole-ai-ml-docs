# Phase 1 Implementation Plan: Skeleton Extraction

## Overview
Implement the skeleton extraction functionality using MediaPipe Pose to extract 33 key points from video frames, normalize coordinates, and perform temporal consistency checks.

## Requirements
- Extract 33 key points from each frame using MediaPipe Pose
- Normalize coordinates to be translation and scale invariant (center on hips/nose, scale by body dimensions)
- Implement temporal consistency checks:
  - Joint angle constraints (elbows shouldn't bend backwards)
  - Body part proximity checks (head shouldn't be below feet)
  - Movement speed limits (body parts shouldn't move faster than physically possible)
- Process videos efficiently with sliding window approach (30 frames with stride=5)
- Store data in MongoDB with proper schema design
- Implement error handling for corrupted frames/videos

## Implementation Details

### 1. Skeleton Extraction Module (`skeleton_extractor.py`)
- Use MediaPipe Pose to detect and extract 33 key points per frame
- Filter keypoints by visibility score > 0.7
- Implement coordinate normalization:
  - Center on hips (keypoints 23 and 24)
  - Scale by shoulder width for translation and scale invariance
  - Normalize z-coordinates to be relative to body dimensions

### 2. Temporal Consistency Checks
- Joint angle constraints: Verify that elbows don't bend backwards
- Body part proximity: Ensure head isn't below feet (in normalized coordinates)
- Movement speed limits: Check that body parts don't move faster than physically possible (max 5.0 normalized distance per frame)

### 3. Sliding Window Processing
- Process videos with 30-frame windows (1 second at 30 FPS)
- Use stride=5 for efficient processing
- Implement pipeline to process consecutive frames

### 4. Data Storage (`storage.py`)
- Store data in MongoDB with proper schema design
- Include video_id, frame number, landmarks, and timestamps
- Implement progress tracking and logging
- Handle corrupted frames/videos gracefully

## File Structure
```
ml/
├── skeleton_extractor.py    # Core skeleton extraction implementation
├── storage.py               # MongoDB storage implementation  
└── processing_pipeline.py   # Processing pipeline with sliding windows
main.py                      # Main entry point
requirements.txt             # Python dependencies
Dockerfile                   # Container configuration
docker-compose.yml           # Docker orchestration
```

## Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `VIDEO_PATH`: Path to input video files  
- `OUTPUT_DIR`: Directory for output data
- `VISIBILITY_THRESHOLD`: Minimum visibility score (default 0.7)
- `STRIDE`: Frame stride for processing (default 5)

## Docker Integration
- Create containerized environment using Python 3.9
- Install required dependencies: OpenCV, MediaPipe, NumPy, PyMongo
- Set up non-root user for security
- Configure proper directory permissions for video/data storage