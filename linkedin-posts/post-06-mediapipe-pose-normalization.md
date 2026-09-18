# The Normalization Trick Most Pose Pipelines Get Wrong

Same movement, different camera, different body — same vector. Here's how.

Raw pose landmarks are useless for ML: the same trick filmed from different distances produces totally different coordinates.

The fix is two simple transforms:
- Center on the hips (translation invariance)
- Scale by shoulder width (scale invariance)

Plus a visibility filter (drop landmarks below 0.7 confidence).

The result: classifier-ready vectors that don't care where the athlete stood or how far the camera was.

This is the first stage of my AI Sport Agent movement pipeline.

How do you normalize pose data?

**Hashtags:** #ComputerVision #MachineLearning #AI #MediaPipe
