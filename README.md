# Birdwatch

Bioacoustic bird identification in two stages: a **mobile app** (iOS/Android) for real-time listening and an **embedded node** (Raspberry Pi) that uploads detections to the cloud. Built around BirdNET (TFLite) and AWS Amplify Gen 2.

## Repo layout

- **`src/birdwatch/`** — Python package for the Raspberry Pi (record → analyze → MQTT).
- **`cloud/`** — AWS Amplify Gen 2 backend (Auth, Data, Storage, Lambda for IoT).
- **`app/`** — Flutter mobile app (Stage 1).

## Requirements

- Python ≥3.12 (use [uv](https://docs.uv.dev/) for installs).
- Node ≥18 for Amplify (`cloud/`).
- Flutter SDK for `app/`.

## Quick start

```bash
uv sync
uv sync --group dev --group docs
```

- **Lint/format:** `uv run ruff check src tests && uv run ruff format src tests`
- **Type check:** `uv run ty check`
- **Tests:** `uv run pytest`
- **Docs:** `uv run mkdocs serve`

## Embedded (Raspberry Pi)

1. Copy repo to the Pi and run `./scripts/setup.sh`.
2. Put BirdNET TFLite model and `labels.txt` in a directory; set `BIRDNET_MODEL_DIR`.
3. Set AWS IoT env vars (endpoint, client id, cert/key paths).
4. Run: `uv run birdwatch` or `python -m birdwatch.pi.main`.

See [docs/embedded.md](docs/embedded.md) and [TODO.md](TODO.md).

## Cloud

From `cloud/`: run `npx ampx sandbox` to deploy. Configure IoT (Thing, policy, rule) per [cloud/scripts/iot-setup.md](cloud/scripts/iot-setup.md).

## Mobile app

From `app/`: `flutter pub get && flutter run`. Configure Amplify with generated outputs after sandbox.

## Documentation

See the [project documentation](https://lancereinsmith.github.io/birdwatch/) for full docs and API reference.
