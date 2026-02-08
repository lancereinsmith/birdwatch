/// Amplify DataStore: observe Detection model for real-time list updates.
library;

import 'dart:async';

import '../models/detection.dart';

export '../models/detection.dart';

/// Subscribe to Detection changes (from Pi and app).
/// Until Amplify is wired, emits an empty list so the UI can show "No detections".
Stream<List<Detection>> observeDetections() async* {
  // TODO: Amplify.DataStore.observe(Detection.classType), collect list, yield
  yield <Detection>[];
}
