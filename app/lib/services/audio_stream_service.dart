/// Real-time audio capture: 48 kHz mono PCM for BirdNET.
///
/// iOS: configure AVAudioSession in "measurement" mode to disable AGC.
/// Android: RECORD_AUDIO permission; sample rate 48000, channel 1.
library;

import 'dart:async';

/// Configuration for BirdNET-compatible capture.
class AudioStreamConfig {
  static const int sampleRate = 48000;
  static const int channels = 1;
  static const int bufferSeconds = 3;
  static const int bufferSamples = sampleRate * bufferSeconds;
}

/// Service that captures audio and emits 3-second float32 buffers.
class AudioStreamService {
  /// Start capture; [onBufferReady] is called with 3 s of samples (chronological).
  /// Call [stop] to release the recorder.
  Future<void> start(void Function(List<double> buffer) onBufferReady) async {
    // TODO: use record package (or flutter_sound)
    // - Format: PCM 16-bit → convert to float32 -1..1
    // - Stream into ring buffer; every 3 s call onBufferReady(ring.read())
    // - iOS: set session category for measurement mode
    throw UnimplementedError('Audio capture not yet implemented');
  }

  Future<void> stop() async {}
}
