# Birdwatch

Birdwatch is a **bioacoustic bird identification** system in two stages:

1. **Mobile app** (iOS/Android) — Listen on the microphone and identify bird
   calls and songs in real time.
2. **Embedded node** (Raspberry Pi) — Passive acoustic monitoring (PAM);
   uploads detections to the cloud so the app can show them.

The system is built around **BirdNET** (TensorFlow Lite) from the Cornell Lab
of Ornithology, with **AWS Amplify Gen 2** for sync and **eBird** /
**iNaturalist** / **Wikipedia** for enrichment.

## Repo layout

| Path | Purpose |
|------|--------|
| `src/birdwatch/` | Python package for the Raspberry Pi: record → analyze → publish. |
| `cloud/` | AWS Amplify Gen 2 backend: Auth, Data (AppSync/DynamoDB), Storage (S3), IoT Lambda. |
| `app/` | Flutter mobile app (Stage 1): live listen + sync with cloud. |
| `docs/` | This documentation (MkDocs). |
| `scripts/` | Setup scripts (e.g. Pi `setup.sh`). |

## Prerequisites

- **Python ≥3.12** — Use [uv](https://docs.uv.dev/) for installs and runs.
- **Node ≥18** — For Amplify backend (`cloud/`).
- **Flutter SDK** — For the mobile app (`app/`).

## Quick start (development)

From the repo root:

```bash
uv sync
uv sync --group dev --group docs
```

Then:

- **Lint & format:** `uv run ruff check src tests && uv run ruff format src tests`
- **Type check:** `uv run ty check`
- **Tests:** `uv run pytest`
- **Docs (local):** `uv run mkdocs serve` → open <http://127.0.0.1:8000>

## Documentation map

- **[Plan](plan.md)** — Architecture summary, data flow, and roadmap.
- **[Embedded (Pi)](embedded.md)** — Hardware, setup, env vars, and running
  the Pi pipeline.
- **[Cloud](cloud.md)** — Amplify backend, Detection schema, IoT setup, and
  Lambda.
- **[Mobile](mobile.md)** — Flutter app structure, audio/inference, and
  Amplify integration.
- **[Model setup](model-setup.md)** — BirdNET TFLite model and labels
  (obtain, place, verify).
- **[Hardware](hardware.md)** — BOM and assembly notes for the Pi node.
- **[Operational](operational.md)** — eBird API key, privacy/legal notes.
- **[API](api/birdwatch.md)** — Python API (mkdocstrings).

## Where to start

- **Run the Pi pipeline locally (no hardware):** Install deps, obtain the
  BirdNET TFLite model and labels, set `BIRDNET_MODEL_DIR`; run
  `uv run birdwatch` (see [Embedded](embedded.md)).
- **Deploy the backend:** From `cloud/`, run `npx ampx sandbox` and follow
  [Cloud](cloud.md) and `cloud/scripts/iot-setup.md`.
- **Run the app:** From `app/`, run `flutter pub get && flutter run` (see
  [Mobile](mobile.md)).

Progress and remaining work are tracked in [TODO](reference/todo.md).
