# Video Cutter Tool Integration Documentation

This document provides a comprehensive overview of how the VideoCutter tool integrates with the rest of the pole-ai project pipeline.

## Overview

The VideoCutter tool serves as an essential component in the pole-ai project's video processing workflow. It bridges the gap between raw video data and the structured skeleton data that feeds into machine learning models, by automatically extracting segments containing specific classes of interest.

## Complete Pipeline Integration

### 1. Input Processing Flow

```
[Raw Video] 
    ↓
[VideoCutter Tool] 
    ↓
[HybridClassifier Predictions]
    ↓
[SkeletonExtractor]
    ↓
[WindowRepository (MongoDB)]
    ↓
[SkeletonEmbeddings]
    ↓
[SkeletonLSTMTrainer]
```

### 2. VideoCutter's Role in the Pipeline

The VideoCutter sits at the beginning of the pipeline, processing raw videos to extract segments of interest:

1. **Initial Processing**: Reads video files using OpenCV
2. **Windowed Analysis**: Processes video in 30-frame windows as expected by the HybridClassifier
3. **Class Detection**: Uses HybridClassifier predictions to identify segments containing target classes
4. **Segment Extraction**: Extracts identified segments using FFmpeg for further processing

### 3. Integration with Key Components

#### HybridClassifier Integration

The VideoCutter leverages the same HybridClassifier instance used throughout the project:

```python
# The same classifier used in the main pipeline
self.classifier = HybridClassifier(**classifier_config) if classifier_config else HybridClassifier()

# Uses the exact same prediction method expected by other components
prediction, confidence, metadata = self.classifier.predict(window)
```

#### SkeletonExtractor Integration

The VideoCutter maintains compatibility with the existing skeleton extraction pipeline:

```python
# Same extractor used for all window processing
self.skeleton_extractor = SkeletonExtractor()

# Extracts features in the same format expected by the classifier
window_features = self._extract_window_features(frames)
```

#### MongoDB Storage Integration

While not directly storing data, the VideoCutter's output feeds into the existing MongoDB workflow:

1. Extracted clips are saved to disk
2. These clips can then be processed through the normal pipeline
3. Windowed data is stored in MongoDB via WindowRepository

### 4. Data Flow Through VideoCutter

```python
def process_video(self, video_path, target_class="handspring", output_dir="output_clips"):
    # 1. Open video with OpenCV
    cap = cv2.VideoCapture(video_path)
    
    # 2. Process in 30-frame windows
    segments = self._detect_target_class_windowed(cap)
    
    # 3. Extract clips using FFmpeg
    self._extract_clips(segments)
    
    # 4. Return list of extracted clip paths
    return extracted_clips
```

### 5. Window Processing Details

The VideoCutter maintains consistency with the project's window processing approach:

- **Window Size**: 30 frames (consistent with classifier expectations)
- **Feature Format**: 14 keypoints per frame (same as other components)
- **Processing Method**: Sliding window approach
- **Temporal Resolution**: Maintains original video timing information

### 6. FFmpeg Integration Details

The tool uses FFmpeg for efficient, lossless video extraction:

```bash
ffmpeg -i input.mp4 -ss startTime -to endTime output_clip.mp4
```

- **Command Structure**: Standard FFmpeg command with start/end time parameters
- **Quality Preservation**: Lossless extraction maintains video quality
- **Error Handling**: Robust error handling for FFmpeg command failures
- **Performance**: Efficient processing of multiple clips

### 7. Confidence Thresholding

The tool implements confidence-based filtering:

```python
# Default threshold of 0.7
if prediction_confidence >= self.confidence_threshold:
    # Include in detected segments
```

This ensures quality control while maintaining detection sensitivity.

## Usage Patterns

### Standard Use Case

```python
from pole_tools.video_cutter import VideoCutter

# Initialize with default settings
cutter = VideoCutter()

# Extract handspring clips from a video
clips = cutter.process_video(
    video_path="sports_video.mp4",
    target_class="handspring",
    output_dir="./handspring_clips"
)
```

### Advanced Configuration

```python
from pole_tools.video_cutter import VideoCutter

# Initialize with custom confidence threshold
cutter = VideoCutter(classifier_config={
    'threshold': 0.8
})

# Process with higher quality requirements
clips = cutter.process_video(
    video_path="sports_video.mp4",
    target_class="handspring",
    output_dir="./handspring_clips",
    confidence_threshold=0.8
)
```

## Benefits of Integration

1. **Consistency**: Uses the same components and data formats as the main pipeline
2. **Efficiency**: Leverages existing classifier and extractor implementations
3. **Scalability**: Can be easily integrated into automated processing workflows
4. **Quality Control**: Maintains the same confidence standards throughout
5. **Maintainability**: Minimal code duplication with shared components

## Testing Integration

The VideoCutter tool includes comprehensive testing that ensures integration with other components:

1. **Unit Tests**: Test individual methods and component interactions
2. **Integration Tests**: Verify end-to-end processing workflow
3. **Compatibility Tests**: Ensure consistent behavior with existing pipeline components

## Future Enhancements

Potential improvements for better integration:

1. **Parallel Processing**: Implement multithreading for faster video processing
2. **Batch Extraction**: Optimize FFmpeg commands for multiple clips
3. **Cloud Integration**: Support cloud-based video processing for large datasets
4. **Real-time Processing**: Enable live video analysis capabilities

This integration ensures that the VideoCutter tool seamlessly fits into the existing pole-ai project architecture while providing valuable functionality for automated video segment extraction.