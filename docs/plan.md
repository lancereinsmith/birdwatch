# Plan summary

This page summarizes the Birdwatch architecture and roadmap. The full
technical specification is in the repo as [Full plan](reference/plan-full.md).

## Why BirdNET and mel spectrograms

Bird identification is treated as **image recognition**: audio is converted
to a **mel spectrogram** (time–frequency representation), then a CNN
classifies it.

- **BirdNET** (Cornell) provides a TFLite model trained on ~6k species.
- **Input:** 3 seconds of mono audio at **48 kHz**.
- **Preprocessing:** FFT (n_fft=2048, hop=278), 96 mel bins, 0–15 kHz,
  log scale. Must match training exactly.

## System architecture

**Edge → Cloud → Edge**

- **Stage 1 (Mobile):** Flutter app captures audio, runs TFLite on-device,
  shows results and syncs with the cloud (Amplify DataStore).
- **Stage 2 (Pi):** Raspberry Pi buffers 3 s chunks, runs the same TFLite
  model, publishes detections to AWS IoT Core; a Lambda forwards them to
  AppSync so the app sees them in real time.
- **Cloud:** AWS Amplify Gen 2 — Cognito (auth), DynamoDB + AppSync (Detection
  model), S3 (audio clips), IoT Core + Lambda (ingest from Pi).

## Key technical choices

| Area | Choice | Reason |
|------|--------|--------|
| Model | BirdNET v2.4 TFLite (FP16) | Research-grade, ~6k species, edge-friendly. |
| Mobile | Flutter + tflite_flutter | Cross-platform, control over DSP and inference. |
| Embedded | Raspberry Pi Zero 2 W | Full Python stack (librosa, tflite_runtime), low power. |
| Cloud | AWS Amplify Gen 2 | Native IoT (MQTT → Lambda), serverless, AppSync sync. |
| Enrichment | eBird, iNaturalist, Wikipedia | Spatial validation, taxonomy, thumbnails. |

## Data flow (Pi → app)

1. Pi records 48 kHz mono, keeps a 3 s ring buffer.
2. Optional noise gate (RMS) skips silent or clipped segments.
3. Each 3 s window → mel spectrogram → TFLite → top species above threshold
   (e.g. 0.7).
4. Each detection is published as JSON to MQTT topic `birdnet/detections`.
5. AWS IoT Rule invokes a Lambda with the message payload.
6. Lambda (or future step) writes to AppSync (e.g. `createDetection`).
7. App subscribes to Detection via DataStore; list updates in real time.

## Implementation roadmap

- **Phase 1 — Cloud:** Amplify project, Detection schema, Storage, Auth,
  IoT Lambda, IoT setup docs.
- **Phase 2 — Embedded:** Pi setup script, recorder (ring buffer), analyzer
  (librosa + TFLite), MQTT client with offline cache.
- **Phase 3 — Mobile:** Flutter app, audio capture, inference (isolate),
  DataStore observe, enrichment APIs (Wikipedia, eBird).

Current status: see [TODO](reference/todo.md).
