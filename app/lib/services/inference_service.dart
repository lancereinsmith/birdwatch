/// On-device BirdNET inference in an isolate to avoid UI jank.
///
/// Pipeline: 3 s float32 buffer → STFT/mel spectrogram (e.g. fftea) → TFLite.
library;

import 'dart:isolate';

/// Result: species index and confidence.
class DetectionResult {
  final int speciesIndex;
  final double confidence;
  const DetectionResult(this.speciesIndex, this.confidence);
}

/// Runs inference in a separate isolate; returns top detections above threshold.
class InferenceService {
  /// Load TFLite model and labels from assets (call once after startup).
  Future<void> loadModel() async {
    // TODO: load assets/BirdNET_*.tflite and labels.txt
    // tflite_flutter: Interpreter.fromAsset('...')
    throw UnimplementedError('TFLite load not yet implemented');
  }

  /// Run inference on [buffer] (3 s, 48k, mono float32).
  /// Returns list of (index, confidence) sorted by confidence.
  Future<List<DetectionResult>> run(List<double> buffer) async {
    // TODO: send buffer to isolate; isolate computes mel + TFLite; return results
    throw UnimplementedError('Inference isolate not yet implemented');
  }

  void dispose() {}
}
