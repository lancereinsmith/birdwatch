# Birdwatch implementation TODO

Progress against PLAN.md implementation roadmap.

## Project setup

- [x] pyproject.toml with PEP 735 dependency-groups (dev, docs)
- [x] Ruff lint/format config
- [x] pytest config and test layout
- [x] mkdocs scaffold
- [x] CI (optional): run ruff, ty, pytest — `.github/workflows/ci.yml`; excludes `-m pi` e2e

## Phase 1: Cloud backend (AWS Amplify Gen 2)

- [x] Amplify Gen 2 project layout under `cloud/`
- [x] Detection schema (Amplify data)
- [x] Storage resource (S3 bucket for audio clips)
- [x] Auth resource (email + IAM for Lambda)
- [x] Lambda: IoT → AppSync mutation (iot-handler)
- [x] Script/docs to create IoT Thing and policy for Pi
- [x] Deploy to AWS (manual: `npx ampx sandbox`) — script `cloud/scripts/deploy-sandbox.sh` and docs in cloud.md

## Phase 2: Embedded system (Raspberry Pi)

- [x] setup.sh for Raspberry Pi OS (deps, Python packages)
- [x] recorder.py: RingBuffer, 48 kHz mono, 3 s buffer (sounddevice)
- [x] analyzer.py: load TFLite, librosa mel spectrogram (n_fft=2048, hop=278, n_mels=96), inference
- [x] mqtt_client.py: awsiotsdk mTLS, publish to birdnet/detections
- [x] Offline cache (SQLite) and watchdog flush when online
- [x] Noise threshold (RMS) to skip inference
- [x] Obtain BirdNET TFLite model and labels; document placement (see docs/model-setup.md)
- [x] End-to-end test on real Pi — scaffold in `tests/e2e/`, marker `pi`; run on Pi: `pytest tests/e2e/ -v` or `pytest -m pi`

## Phase 3: Mobile application (Flutter)

- [x] Flutter project under `app/`
- [x] Pubspec: amplify_flutter, tflite_flutter, flutter_sound, permission_handler
- [x] AudioStream service (48 kHz mono, measurement mode on iOS)
- [x] Inference isolate + spectrogram (fftea or placeholder)
- [x] Amplify DataStore observe(Detection)
- [x] WikipediaService, eBirdService stubs
- [x] Full UI (DetectionList, detail screens) — list + detail scaffold; home links to list
- [x] Release build and store listing — docs in mobile.md (build commands, store checklist)

## Documentation

- [x] mkdocs index and structure
- [x] README updated (overview, uv, ruff, ty, pytest, mkdocs)
- [x] API docs (mkdocstrings) for Python — docs/api/birdwatch.md + mkdocstrings plugin
- [x] Hardware BOM and assembly notes — docs/hardware.md

## Operational

- [x] eBird API key and usage docs — docs/operational.md
- [x] Privacy/legal note (no continuous recording) — docs/operational.md
