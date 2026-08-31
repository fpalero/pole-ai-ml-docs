Aquí tienes todo el documento unificado y formateado de manera limpia, consistente y estructurada en Markdown, corrigiendo las secciones de código rotas y los bloques de texto plano del original.
------------------------------
## VideoCutter Configuration Parameters## 📁 Video Section

| Parameter | Value | Description | Impact |
|---|---|---|---|
| video_path | null | Path to the video file to process | Set at runtime via command line |
| output_dir | "output_clips" | Directory where extracted clips will be saved | All clips are saved in this directory |
| target_class | null | Target class to detect (e.g., "handspring") | Set at runtime via command line |
| window_size | 30 | Number of frames per window for classification | At 30 FPS = 1 second of video |
| video_padding | 1 | Seconds added before and after each segment | Provides margin around detected segments |

## window_size (30)

* What it does: Defines how many consecutive frames are grouped together for a single prediction.
* Why 30: At 30 FPS, this equals 1 second of video.
* Trade-offs:
* Larger: More context but less temporal precision.
   * Smaller: Faster but noisier.
* Usage: Accumulates window_size frames in buffer and passes them to classifier.

## video_padding (1)

* What it does: Adds extra seconds to the start and end of each extracted clip.
* Why 1: Provides a 1-second margin before and after the detected segment.
* Benefits: Captures the complete movement even if detection timing is slightly off.
* Usage:

start_clip = max(0, start - padding)duration_clip = min(total, end + padding)


------------------------------
## 📊 Confidence Section

| Parameter | Value | Description | Impact |
|---|---|---|---|
| threshold | 0.95 | Base confidence threshold | Reference threshold for confidence levels |
| threshold_high | 0.99 | High threshold to start detection | Very strict, only accepts nearly perfect predictions |
| threshold_low | 0.90 | Low threshold to maintain detection | More permissive once a segment has started |

## threshold (0.95)

* What it does: Base confidence threshold (used as reference).
* Why 0.95: Very strict, only accepts highly confident predictions.
* Impact: Filters false positives but may miss real detections.

## threshold_high (0.99)

* What it does: Minimum confidence required to start a new segment.
* Why 0.99: Extremely strict for initiation.
* Impact: Only starts a segment when confidence is near perfect.
* Usage:

if avg_confidence >= self.confidence_threshold_high:
    # Start detection
    consecutive_detections += 1


## threshold_low (0.90)

* What it does: Minimum confidence required to maintain an active segment.
* Why 0.90: More permissive once segment has started.
* Impact: Allows segment to continue even if confidence drops slightly.
* Usage:

if avg_confidence >= self.confidence_threshold_low:
    # Maintain detection
    last_detection_time = window_end_time


------------------------------
## ⏱️ Duration Section

| Parameter | Value | Description | Impact |
|---|---|---|---|
| min_segment | 2.0 | Minimum segment duration (seconds) | Discards segments shorter than this |
| max_segment | 4.0 | Maximum segment duration (seconds) | Discards segments longer than this |

## min_segment (2.0)

* What it does: Discards segments shorter than this duration.
* Why 2.0: A typical trick lasts 2-3 seconds.
* Impact: Filters out short false positive segments (noise).
* Usage: Filters segments that don't meet minimum duration.

## max_segment (4.0)

* What it does: Discards segments longer than this duration.
* Why 4.0: A trick rarely lasts more than 4 seconds.
* Impact: Prevents multiple tricks from being merged into one.
* Usage: Filters segments that exceed maximum duration.

------------------------------
## 🎯 Detection Section

| Parameter | Value | Description | Impact |
|---|---|---|---|
| min_consecutive | 10 | Consecutive detections needed to start | At 30 FPS ≈ 0.33 seconds of consistent detection |
| max_gap | 0.15 | Maximum gap between detections (seconds) | 150ms, very strict |

## min_consecutive (10)

* What it does: Minimum number of consecutive detections to start a segment.
* Why 10: At 30 FPS ≈ 0.33 seconds of consistent detection.
* Impact:
* Higher: More robust against false positives.
   * Lower: More sensitive but noisier.
* Usage:

consecutive_detections += 1if consecutive_detections >= self.min_consecutive_detections:
    # Start segment


## max_gap (0.15)

* What it does: Maximum time allowed without detection before closing segment.
* Why 0.15: 150ms, very strict.
* Impact:
* Lower: Shorter, more precise segments.
   * Higher: Longer but less precise segments.
* Usage:

time_since_last = window_end_time - last_detection_timeif time_since_last > self.max_gap_between_detections:
    # Close segment


------------------------------
## 📈 History Section

| Parameter | Value | Description | Impact |
|---|---|---|---|
| window | 15 | Number of predictions for moving average | Smooths confidence fluctuations |

## window (15)

* What it does: Size of the window for calculating moving average of confidence.
* Why 15: Smooths confidence fluctuations without losing sensitivity.
* Impact:
* Larger: Smoother but slower to react.
   * Smaller: More reactive but noisier.
* Usage:

confidence_history.append(pred_conf)if len(confidence_history) > history_window:
    confidence_history.pop(0)avg_confidence = np.mean(confidence_history)


------------------------------
## 🔄 Complete Parameter Flow

1. Frame → SkeletonExtractor → Features (14 features)
2. Accumulate window_size frames in buffer
3. Classifier predicts (class, confidence)
4. Store confidence in history window (15)
5. Calculate avg_confidence (moving average)
6. If target class detected:
   a. If NOT currently detecting:
      - If avg_confidence >= threshold_high (0.99)
      - Increment consecutive_detections
      - If consecutive_detections >= min_consecutive (10)
      - START segment
   b. If ALREADY detecting:
      - If avg_confidence >= threshold_low (0.90)
      - Maintain segment
      - If not, and gap > max_gap (0.15)
      - CLOSE segment
7. Filter by duration: min_segment (2.0) - max_segment (4.0)
8. Apply video_padding (1s before/after)
9. Extract clips with FFmpeg
