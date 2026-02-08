# End-to-end tests (run on Raspberry Pi)

These tests require a real Pi with microphone, BirdNET model, and (optionally)
AWS IoT credentials. They are **not** run in CI.

## Setup on the Pi

1. Complete [Embedded setup](../../docs/embedded.md): OS, `setup.sh`, model,
   env vars.
2. Optionally set AWS IoT env vars for MQTT (or tests will use offline cache).

## Run e2e tests

From the repo root on the Pi:

```bash
uv sync --group dev
uv run pytest tests/e2e/ -v
```

To run only e2e tests by marker (from anywhere):

```bash
uv run pytest -m pi -v
```

By default, CI excludes `-m pi` so these tests are skipped in GitHub Actions.
