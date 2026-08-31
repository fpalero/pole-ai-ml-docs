# Video Cropping Tool Requirements Document

## 1. Introduction

The purpose of this document is to outline the requirements and design for a video cropping tool that leverages the HybridClassifier from @pole_ml/classifiers/hybrid_classifier.py and utilizes ffmpeg for efficient video processing. This tool aims to automate the extraction of specific segments of interest from videos based on the classifier's predictions.

### Objectives

- Automatically detect and extract video segments corresponding to predefined classes using the HybridClassifier.
- Efficiently process videos using ffmpeg to ensure high performance and minimal resource usage.
- Provide a clear, maintainable implementation that can be easily integrated into existing workflows.

## 2. System Design

### 2.1 Architecture Overview

The system architecture is designed to handle video processing in a modular and efficient manner:

```
[Input Video] -> [HybridClassifier for Predictions] -> [VideoCutter Class] -> [FFmpeg for Cropping] -> [Output Clips]
```

Components:

- HybridClassifier: Responsible for making class predictions on video windows.
- VideoCutter Class: Orchestrates the entire process, from reading videos to invoking ffmpeg commands.
- FFmpeg: Used for actual video cropping based on detected segments.
- SkeletonExtractor: Extracts skeleton features for consistent window processing.

### 2.2 Key Components

- **HybridClassifier**:
  - Processes video data in 30-frame windows as expected by the classifier.
  - Outputs class predictions along with confidence scores.
- **VideoCutter Class**:
  - Manages the workflow, including video reading, prediction processing, and ffmpeg invocation.
  - Handles error checking and resource management (e.g., releasing video captures).
- **SkeletonExtractor**:
  - Extracts skeleton features from frames for consistent windowed processing.
  - Ensures that extracted windows have the expected format (30 frames with 14 keypoints each).

## 3. Implementation Details

### 3.1 HybridClassifier Integration

The VideoCutter class will utilize the HybridClassifier to make predictions on 30-frame windows:

- Method: `predict(window)`
  - Expects a window of shape (30, 14) - 30 frames with 14 keypoints each
  - Returns a tuple containing:
    - `prediction`: The predicted class (e.g., "handspring")
    - `confidence`: Confidence score for the prediction
    - `metadata`: Additional metadata if required

### 3.2 FFmpeg Integration

FFmpeg will be used to extract clips from detected segments:

- Command Structure: `ffmpeg -i input.mp4 -ss startTime -to endTime output_clip.mp4`
- Parameters:
  - `-i`: Input video file path
  - `-ss`: Start time of the segment in HH:MM:SS format
  - `-to`: End time of the segment in HH:MM:SS format
  - Output clip path

### 3.3 Class Design

```python
class VideoCutter:
    def __init__(self, classifier_config=None):
        # Initialize HybridClassifier with optional configuration
        self.classifier = HybridClassifier(**classifier_config) if classifier_config else HybridClassifier()
        # Initialize SkeletonExtractor for window processing
        self.skeleton_extractor = SkeletonExtractor()
        # Other initializations...

    def process_video(self, video_path, target_class="handspring", output_dir="output_clips"):
        """
        Main method to process the video and extract clips.

        Args:
            video_path (str): Path to the input video file.
            target_class (str): Target class to detect and extract.
            output_dir (str): Directory for output clips.

        Returns:
            None
        """
        # Implementation...

    def _setup_ffmpeg(self):
        """
        Ensure ffmpeg is available and properly configured.
        """
        # Check if ffmpeg is installed and in PATH...
        pass

    def _detect_target_class_windowed(self, cap):
        """
        Detect target class segments using the HybridClassifier with windowed processing.

        Args:
            cap (cv2.VideoCapture): OpenCV VideoCapture object.

        Returns:
            list: List of detected segments as tuples (start_time, end_time).
        """
        # Implementation...

    def _extract_window_features(self, frames):
        """
        Extract skeleton features from a window of frames.

        Args:
            frames (list): List of OpenCV frames

        Returns:
            numpy.ndarray or None: Window features as expected by classifier, or None if failed
        """
        # Implementation...

    def _extract_clips(self, segments):
        """
        Extract clips for detected segments using ffmpeg.

        Args:
            segments (list): List of tuples (start_time, end_time).

        Returns:
            None
        """
        # Implementation...
```

### 3.4 Skeleton Extraction Integration

The VideoCutter tool integrates with the skeleton extraction pipeline by:

1. Using the same `SkeletonExtractor` instance that's used throughout the project
2. Ensuring consistent window formats (30 frames, 14 keypoints) 
3. Processing windows in a way that matches the expectations of downstream components
4. Maintaining compatibility with the existing MongoDB storage structure
5. Supporting both classifier-based detection and direct skeleton feature extraction for validation

### 3.5 Confidence Thresholding

The tool implements confidence thresholding to improve extraction quality:

1. Each window prediction includes a confidence score
2. Clips are only extracted if confidence exceeds the threshold (default: 0.7)
3. Users can customize the threshold based on their specific requirements
4. Lower thresholds may result in more clips but potentially lower quality
5. Higher thresholds ensure better quality but may miss some valid segments

### 3.6 Error Handling and Logging

Comprehensive error handling is implemented:

1. Video file validation and existence checks
2. FFmpeg command execution monitoring
3. Classifier prediction error recovery
4. Resource cleanup (video capture release, temporary files)
5. Detailed logging of processing steps and potential issues
6. Graceful degradation when individual components fail

## 4. Testing Strategy

### 4.1 Unit Tests

- **HybridClassifier Integration**:
  - Test prediction accuracy and confidence scores on windowed data
- **VideoCutter Methods**:
  - Test `_setup_ffmpeg` for proper ffmpeg availability checks
  - Test `_detect_target_class_windowed` for correct segment detection using windows
  - Test `_extract_window_features` for accurate skeleton feature extraction
  - Test `_extract_clips` for accurate clip extraction

### 4.2 Integration Tests

- Ensure that the entire workflow (video reading, window processing, prediction, ffmpeg extraction) functions as expected
- Verify that clips are correctly extracted and saved to the specified output directory

### 4.3 Manual Validation

- Manually inspect extracted clips to ensure they align with the detected segments
- Validate that no unintended or erroneous clips are produced

## 5. Optimization and Future Enhancements

### 5.1 Potential Improvements

- **Parallel Processing**: Implement multithreading or multiprocessing for faster video processing
- **Batch Processing**: Optimize ffmpeg commands to handle multiple clips in a single invocation
- **Error Handling**: Enhance error logging and recovery mechanisms

### 5.2 Scalability Considerations

- **Support Multiple Formats**: Extend the tool to handle different video formats and resolutions
- **Cloud Integration**: Explore options for cloud-based processing to handle large-scale video analysis

## 6. Conclusion

This document outlines the requirements and design for a robust video cropping tool that integrates the HybridClassifier with ffmpeg for efficient segment extraction. By following these guidelines, we aim to develop a reliable and scalable solution that meets the project's objectives.

## 7. Usage Examples

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

### Advanced Usage with Custom Configuration

```python
from pole_tools.video_cutter import VideoCutter

# Create cutter with custom classifier configuration
cutter = VideoCutter(classifier_config={
    'model_path': '/path/to/custom/model',
    'threshold': 0.8
})

# Process video with custom parameters
clips = cutter.process_video(
    video_path="input_video.mp4",
    target_class="handspring",
    output_dir="./extracted_clips",
    confidence_threshold=0.8  # Custom confidence threshold
)
```

## 8. Integration Points

The VideoCutter tool integrates seamlessly with:

1. **HybridClassifier**: Uses the same classifier instance for consistent predictions
2. **SkeletonExtractor**: Maintains compatibility with windowed processing expectations
3. **OpenCV**: Leverages existing video reading capabilities
4. **FFmpeg**: Utilizes efficient video extraction capabilities
5. **MongoDB Storage**: Works with the existing data storage infrastructure

## 9. Performance Considerations

- The tool processes videos in 30-frame windows as expected by the HybridClassifier
- FFmpeg is used for efficient, lossless video cropping
- Confidence thresholding helps reduce false positives
- Error handling ensures robust processing even with problematic videos