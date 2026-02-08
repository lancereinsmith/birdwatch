# User guide

This guide walks through using Birdwatch: the embedded Pi node, the cloud
backend, and the mobile app.

## What Birdwatch does

- **Mobile app** — Record from the device microphone, run BirdNET
  on-device, and see identifications in real time. Detections from Pi
  nodes also sync into the app.
- **Embedded node (Pi)** — Continuously records 3 s chunks, runs the same
  BirdNET model, and publishes detections to the cloud so they appear in
  the app.
- **Cloud** — AWS Amplify Gen 2 provides auth, a Detection data model with
  real-time sync (AppSync), storage for audio clips, and an IoT path so
  the Pi can publish detections.

## Running the Pi node

1. **Hardware** — Raspberry Pi Zero 2 W (or compatible), USB sound card,
   and a suitable microphone. See [Hardware](hardware.md).
2. **Software** — On the Pi, run `./scripts/setup.sh` from the repo root
   to install system packages and Python deps (including `tflite-runtime`
   on ARM).
3. **Model** — Obtain the BirdNET TFLite model and labels; put them in a
   directory and set `BIRDNET_MODEL_DIR`. See [Model setup](model-setup.md).
4. **AWS IoT** (optional) — To publish detections to the cloud, create an
   IoT Thing, certificate, and policy; set `AWS_IOT_*` env vars. See
   [Cloud: IoT setup](cloud.md#iot-setup-for-the-pi).
5. **Run** — From the repo root: `uv run birdwatch`. Detections are
   published to MQTT when connected, or cached locally until the network
   is available.

Full details: [Embedded (Pi)](embedded.md).

## Deploying the backend

1. **Prerequisites** — Node ≥18, AWS CLI (or Amplify/SSO) configured.
2. **Deploy** — From repo root: `cd cloud && npx ampx sandbox`. This
   deploys Auth, Data (Detection model), Storage, and the IoT Lambda.
3. **Outputs** — Use the generated Amplify outputs (e.g.
   `amplify_outputs.json`) in the Flutter app so it can connect to
   AppSync and DataStore.
4. **IoT** — Create an IoT Rule that forwards `birdnet/detections` to the
   Lambda so Pi detections are written to the backend. See
   [Cloud](cloud.md) and `cloud/scripts/iot-setup.md`.

## Running the mobile app

1. **Prerequisites** — Flutter SDK; for iOS, Xcode and mic usage
   description; for Android, RECORD_AUDIO permission.
2. **Run** — From repo root: `cd app && flutter pub get && flutter run`.
3. **Backend** — After deploying the sandbox, copy Amplify outputs into
   the app and configure Amplify in `main.dart`. Until then, the app runs
   without cloud sync.
4. **Model** — Add the BirdNET TFLite model and labels to `app/assets/`
   for on-device inference. See [Model setup](model-setup.md) and
   [Mobile](mobile.md).

## Typical workflows

- **Pi only** — Set `BIRDNET_MODEL_DIR`, run `uv run birdwatch`. Detections
  are cached locally if AWS IoT is not configured.
- **App only** — Run the app with or without Amplify; use the mic for
  real-time ID when the model is in assets.
- **Pi + cloud** — Deploy the backend, set up IoT (Thing, policy, Rule),
  configure the Pi with certs and env vars. Pi detections flow to
  AppSync and appear in the app.
- **Development** — Use `uv run mkdocs serve` for docs, `uv run pytest`
  for tests, and `uv run ruff check src tests && uv run ruff format src
  tests` for lint/format.

## More reference

- [Model setup](model-setup.md) — Obtaining and placing the BirdNET model.
- [Hardware](hardware.md) — BOM and assembly for the Pi node.
- [Operational](operational.md) — eBird API key, privacy/legal notes.
- [API](api/birdwatch.md) — Python API reference.
