# Mobile app (Flutter)

The **Stage 1** app lives under **`app/`**. It lets users listen with the
device microphone, run BirdNET inference on-device, and see detections that
sync from the cloud (including those from Raspberry Pi nodes).

## Features (current and planned)

- **Real-time listen:** Capture 48 kHz mono audio; run inference on 3 s
  chunks; show species and confidence.
- **Sync:** Subscribe to the Amplify DataStore Detection model so detections
  from the Pi (and other sources) appear in the app in real time.
- **Enrichment:** Wikipedia (thumbnails, summary), eBird (recent
  observations by region for spatial validation), iNaturalist (taxonomy,
  images).

## Project structure

```text
app/
├── pubspec.yaml
├── lib/
│   ├── main.dart              # App entry; Amplify config (when deployed)
│   ├── screens/
│   │   └── home_screen.dart   # Placeholder home / detection list
│   └── services/
│       ├── audio_stream_service.dart   # 48 kHz capture, 3 s buffers
│       ├── inference_service.dart      # TFLite in isolate
│       ├── amplify_sync_service.dart   # DataStore.observe(Detection)
│       ├── wikipedia_service.dart      # Page summary API
│       └── ebird_service.dart          # Recent observations by region
└── assets/                   # Add BirdNET .tflite and labels.txt
```

## Prerequisites

- Flutter SDK (stable channel).
- For iOS: Xcode, CocoaPods; configure microphone usage description.
- For Android: minSdk per Flutter; RECORD_AUDIO permission.

## Running the app

From the repo root:

```bash
cd app
flutter pub get
flutter run
```

Select a device or simulator. The app currently shows a placeholder home
screen; wiring to Amplify and inference is in progress (see [TODO](reference/todo.md)).

## Backend configuration

After deploying the Amplify backend (`npx ampx sandbox` from `cloud/`):

1. Copy or generate **Amplify outputs** (e.g. `amplify_outputs.json`) into
   the app (e.g. `app/lib/` or a config path).
2. In `main.dart`, add the Amplify plugins (Auth Cognito, API, DataStore,
   Storage S3) and call `Amplify.configure(amplifyConfig)` with that
   output.
3. Ensure the app has the correct API keys / auth mode so it can read and
   write the Detection model and (if used) storage.

Until that is done, the app runs without cloud sync.

## Audio pipeline

- **Capture:** Use the `record` package (or flutter_sound) to record PCM
  at **48 kHz, mono**. On iOS, set the audio session to a “measurement”
  style so AGC does not distort bird calls.
- **Buffering:** Maintain a ring buffer of 144,000 samples (3 s). Every 3 s
  (or with overlap, e.g. 1 s), pass the slice to the inference pipeline.
- **Spectrogram:** BirdNET expects a mel spectrogram, not raw audio. On
  mobile, compute it in app code (e.g. FFT + mel bins). The plan suggests
  an **isolate** or FFI to a C++ FFT (e.g. KissFFT) to avoid UI jank.
- **Inference:** Load the BirdNET TFLite model from assets; run in a
  **separate isolate** so the UI stays responsive. Input shape and
  preprocessing (n_fft=2048, hop=278, n_mels=96, 0–15 kHz) must match the
  Pi/analyzer.

## Inference and model assets

- Add **BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite** and **labels.txt** to
  `app/assets/` and reference them in `pubspec.yaml` under `flutter:
  assets:`.
- Use **tflite_flutter** to load the model (e.g. `Interpreter.fromAsset`)
  and run inference. Map output indices to species via labels.txt.
- Apply a confidence threshold (e.g. 0.7); optionally filter by location
  using eBird “recent observations” for the user’s region.

## Sync (Amplify DataStore)

- Use **Amplify.DataStore.observe()** on the Detection model type so new
  and updated detections (from the Pi or other clients) stream to the app.
- Build a **DetectionList** (or similar) that updates when the observed
  stream emits; show device id, species, confidence, timestamp, and
  optional thumbnail (Wikipedia) or map.

## Enrichment APIs

- **Wikipedia:** `GET https://en.wikipedia.org/api/rest_v1/page/summary/{title}`
  for thumbnail and extract; use scientific name as title.
- **eBird:** “Recent observations in a region” for spatial validation;
  requires an eBird API key. Use the user’s lat/lon to get a region code
  (e.g. county), then fetch recent species and flag or suppress detections
  not in that list.
- **iNaturalist:** Taxonomy and images; use the taxa API with scientific
  name.

API keys (eBird, etc.) should be configured via environment or a secure
config (not hardcoded).

## Key packages

- **amplify_flutter**, **amplify_auth_cognito**, **amplify_api**,
  **amplify_datastore**, **amplify_storage_s3** — Backend and sync.
- **tflite_flutter** — On-device inference.
- **record** (or **flutter_sound**) — Audio capture.
- **permission_handler** — Mic permissions.
- **fftea** (or FFI to C++ FFT) — Spectrogram in isolate.
- **http** — Wikipedia / eBird / iNaturalist calls.

## Release build and store listing

### Build

- **Android:** `flutter build apk` (debug) or `flutter build appbundle` (Play
  Store). Set version in `pubspec.yaml` (`version: 0.1.0+1` = name+build).
- **iOS:** `flutter build ios`; open Xcode to archive and upload, or use
  Codemagic / Fastlane. Configure signing and provisioning.

### Store listing checklist

- **Icons:** App icon (adaptive on Android; all sizes on iOS).
- **Screenshots:** Phone (and tablet if supported) for each store.
- **Short description / tagline:** One line for listing.
- **Full description:** Features, permissions (e.g. microphone for bird
  ID), and that raw audio is not stored (see [Operational](operational.md)).
- **Privacy policy URL:** Required for Play and App Store if you collect
  data or use sensitive permissions.
- **Categories:** e.g. Nature, Education.
- **Content rating:** Complete the questionnaire (e.g. everyone).
- **Permissions:** Justify microphone in the store listing and in-app.
