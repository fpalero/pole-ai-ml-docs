# Video Cutter Tool Documentation

## Overview

The Video Cutter tool is designed to automatically extract segments from videos that contain specific classes detected by the HybridClassifier. It processes videos in 30-frame windows, uses the classifier to identify interesting segments, and then extracts those segments using ffmpeg.

## Key Features

- **Windowed Processing**: Processes videos in 30-frame windows as expected by the HybridClassifier
- **Class Detection**: Automatically detects segments containing specified target classes  
- **Efficient Extraction**: Uses ffmpeg for fast, lossless video extraction
- **Confidence Thresholding**: Only extracts segments with confidence above a threshold
- **Skeleton Feature Extraction**: Integrates with SkeletonExtractor for consistent window processing

## Architecture

```
[Input Video] 
    ↓
[OpenCV VideoCapture]
    ↓
[30-frame Window Processing]
    ↓
[HybridClassifier Prediction]
    ↓
[FFmpeg Clip Extraction]
    ↓
[Output Clips]
```

## Integration with Existing Components

The Video Cutter tool integrates seamlessly with:

1. **HybridClassifier**: Uses the classifier to make predictions on 30-frame windows
2. **SkeletonExtractor**: Extracts skeleton features for consistent window processing  
3. **OpenCV**: Handles video reading and basic frame operations
4. **FFmpeg**: Performs efficient video cropping and extraction

## Usage Examples

### Basic Usage

```python
from pole_tools.video_cutter import VideoCutter

# Create cutter instance
cutter = VideoCutter()

# Process video and extract clips
clips = cutter.process_video(
    video_path="input_video.mp4",
    target_class="handspring",  # Class to detect
    output_dir="./extracted_clips"  # Output directory
)

print(f"Extracted {len(clips)} clips")
```

### Advanced Usage

```python
from pole_tools.video_cutter import VideoCutter

# Create cutter instance with custom configuration
cutter = VideoCutter(classifier_config={
    'model_path': './models/best_model.pth',
    'confidence_threshold': 0.8
})

# Process video with specific settings
clips = cutter.process_video(
    video_path="input_video.mp4",
    target_class="handspring",
    output_dir="./extracted_clips",
    confidence_threshold=0.85,
    min_clip_duration=2.0  # Minimum clip duration in seconds
)
```

## Methods

### `__init__(self, classifier_config=None)`

Initialize the VideoCutter with optional classifier configuration.

**Parameters:**
- `classifier_config` (dict): Configuration parameters for the HybridClassifier

### `process_video(self, video_path, target_class="handspring", output_dir="output_clips")`

Main method to process a video and extract clips containing the target class.

**Parameters:**
- `video_path` (str): Path to the input video file
- `target_class` (str): Target class to detect and extract (default: "handspring")
- `output_dir` (str): Directory for output clips (default: "output_clips")

**Returns:**
- List of paths to extracted clip files

### `_detect_target_class_windowed(self, cap)`

Detect target class segments using windowed processing with the HybridClassifier.

**Parameters:**
- `cap` (cv2.VideoCapture): OpenCV VideoCapture object

**Returns:**
- List of detected segments as tuples (start_time, end_time)

### `_extract_window_features(self, frames)`

Extract skeleton features from a window of frames.

**Parameters:**
- `frames` (list): List of OpenCV frames

**Returns:**
- numpy.ndarray or None: Window features as expected by classifier, or None if failed

## Requirements

- OpenCV (`cv2`)
- FFmpeg (for video extraction)
- HybridClassifier from `pole_ml/classifiers/hybrid_classifier.py`
- SkeletonExtractor from `pole_ml/processors/skeleton_extractor.py`

## Error Handling

The tool includes comprehensive error handling for:
- Missing input files
- FFmpeg not being available
- Classifier prediction failures  
- Video processing errors
- File system issues

## Performance Considerations

- Processes videos in 30-frame windows to match classifier expectations
- Uses efficient OpenCV video reading
- Leverages ffmpeg for fast, lossless extraction
- Supports parallel processing of multiple videos (future enhancement)

## Future Enhancements

1. **Parallel Processing**: Implement multithreading for faster video processing
2. **Batch Processing**: Optimize ffmpeg commands to handle multiple clips in a single invocation
3. **Cloud Integration**: Support cloud-based processing for large-scale video analysis
4. **Multiple Class Detection**: Extract clips for multiple target classes simultaneously
5. **Configurable Thresholds**: Allow users to set custom confidence thresholds