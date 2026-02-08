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

## Get started

- **[Quickstart](quickstart.md)** — Install and run the Pi pipeline,
  backend, or app in a few steps.
- **[User guide](user-guide.md)** — How the Pi, cloud, and app fit
  together and typical workflows.

## Documentation map

- **[Embedded (Pi)](embedded.md)** — Hardware, setup, env vars, and
  running the Pi pipeline.
- **[Cloud](cloud.md)** — Amplify backend, Detection schema, IoT setup,
  and Lambda.
- **[Mobile](mobile.md)** — Flutter app structure, audio/inference, and
  Amplify integration.
- **[Model setup](model-setup.md)** — BirdNET TFLite model and labels
  (obtain, place, verify).
- **[Hardware](hardware.md)** — BOM and assembly notes for the Pi node.
- **[Operational](operational.md)** — eBird API key, privacy/legal notes.
- **[API](api/birdwatch.md)** — Python API (mkdocstrings).
- **[Plan](plan.md)** — Architecture summary, data flow, and roadmap.

## Development

From the repo root: `uv sync --group dev --group docs`. Then lint/format
(`uv run ruff check src tests && uv run ruff format src tests`), type check
(`uv run ty check`), tests (`uv run pytest`), and local docs
(`uv run mkdocs serve` → <http://127.0.0.1:8000>).