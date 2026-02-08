# Quickstart

Get Birdwatch running in a few steps.

## Prerequisites

- **Python ≥3.12** — Use [uv](https://docs.uv.dev/) for installs.
- **Node ≥18** — For the Amplify backend (`cloud/`).
- **Flutter SDK** — For the mobile app (`app/`).

## 1. Install

From the repo root:

```bash
uv sync
uv sync --group dev --group docs
```

## 2. Run something

### Option A: Pi pipeline (record → analyze → publish)

1. Obtain the BirdNET TFLite model and labels; put them in a directory.
2. Set `BIRDNET_MODEL_DIR` to that directory.
3. (Optional) Set AWS IoT env vars if you want to publish to the cloud.
4. Run:

```bash
uv run birdwatch
```

See [Embedded (Pi)](embedded.md) and [Model setup](model-setup.md) for details.

### Option B: Backend (Amplify sandbox)

From the repo root:

```bash
cd cloud
npx ampx sandbox
```

Then configure the app with the generated Amplify outputs. See [Cloud](cloud.md).

### Option C: Mobile app

From the repo root:

```bash
cd app
flutter pub get
flutter run
```

See [Mobile](mobile.md) for backend config and permissions.

## Next steps

- [User guide](user-guide.md) — How the pieces fit and typical workflows.
- [Embedded (Pi)](embedded.md) — Full Pi setup, env vars, and offline cache.
- [Cloud](cloud.md) — Detection schema, IoT Rule, and Lambda.
- [Mobile](mobile.md) — App structure, inference, and Amplify.
