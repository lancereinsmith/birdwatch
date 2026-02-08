# Embedded system (Raspberry Pi)

The **Stage 2** node runs the Birdwatch Python package on a Raspberry Pi (or
compatible Linux board): it records audio, runs BirdNET inference, and
publishes detections to AWS IoT Core. When the cloud is unavailable,
detections are cached locally and sent when connectivity returns.

## Hardware

### Recommended: Raspberry Pi Zero 2 W

- Quad-core ARM, 512 MB RAM, Wi‑Fi.
- Runs full Python stack (librosa, tflite_runtime).
- Power: ~0.7 W idle, ~1.3 W under inference.

### Audio input

- **Microphone:** e.g. Primo EM272 or “Clippy” style; low self-noise.
- **Interface:** Pi has no built-in analog mic input; use a USB audio
  adapter (e.g. UGREEN, Sound Blaster Play! 3). Avoid very cheap dongles
  (noise can confuse the model).

### Optional: solar and battery

For 24/7 outdoor use, the plan suggests a 25–35 W solar panel, 12 V 12 Ah
LiFePO4 battery, MPPT controller, and 5 V buck for the Pi. See the full
[Full plan](reference/plan-full.md) for energy calculations.

## Software setup

### 1. OS and system packages

On **Raspberry Pi OS** (Bullseye or Bookworm), from the repo root:

```bash
./scripts/setup.sh
```

This installs `python3-pip`, `python3-venv`, `libatlas-base-dev`,
`libportaudio2`, and `portaudio19-dev`, then creates a venv and installs
numpy, librosa, sounddevice, awsiotsdk. On ARM it also installs
`tflite-runtime` if available.

If you copy the repo to the Pi, run the same script there (or install the
same packages and `pip install` the birdwatch package).

### 2. BirdNET model and labels

The analyzer expects the **BirdNET TFLite model** and a **labels file**.

1. Get the model and labels (e.g. from
   [BirdNET-Analyzer](https://github.com/birdnet-team/BirdNET-Analyzer-Sierra)
   or [Zenodo](https://zenodo.org/records/15050749)).
2. Place in a directory, for example:
   - `BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite`
   - `labels.txt` (one scientific name per line)
3. Set the environment variable:
   - `BIRDNET_MODEL_DIR=/path/to/that/directory`

### 3. AWS IoT (for publishing detections)

Create an IoT Thing, certificate, and policy so the Pi can publish to
`birdnet/detections`. See [Cloud: IoT setup](cloud.md#iot-setup-for-the-pi)
and `cloud/scripts/iot-setup.md`.

Then set:

- `AWS_IOT_ENDPOINT` — e.g. `xxxxxxxx-ats.iot.region.amazonaws.com`
- `AWS_IOT_CLIENT_ID` — e.g. thing name `birdnet-pi-01`
- `AWS_IOT_CERT_PATH` — path to the device certificate
- `AWS_IOT_KEY_PATH` — path to the private key
- `AWS_IOT_CA_PATH` (optional) — path to Amazon Root CA 1

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BIRDNET_MODEL_DIR` | Yes | Directory containing the TFLite model and `labels.txt`. |
| `BIRDNET_DEVICE_ID` | No | Device id in Detection payloads (default `pi-01`). |
| `BIRDNET_CONFIDENCE` | No | Minimum confidence (default `0.7`). |
| `BIRDNET_OFFLINE_CACHE` | No | Path for SQLite cache (default `offline_cache.db`). |
| `AWS_IOT_*` | Yes for MQTT | Endpoint, client id, cert/key (and optionally CA) paths. |

Noise gate (RMS floor/ceiling) is currently in code; can be made configurable
later.

## Pipeline and modules

1. **recorder** (`birdwatch.recorder`)
   - `RingBuffer`: 48 kHz mono float32, 3 s (144,000 samples).
   - `run_recorder()`: captures via PortAudio (sounddevice), fills buffer,
     calls `on_buffer_ready` with a 3 s slice when the noise gate allows.
2. **analyzer** (`birdwatch.analyzer`)
   - `preprocess_audio()`: normalizes and builds mel spectrogram (librosa:
     n_fft=2048, hop=278, n_mels=96, fmax=15 kHz).
   - `BirdNETAnalyzer`: loads TFLite model and labels, runs inference,
     returns list of (species_index, confidence) above threshold.
3. **mqtt_client** (`birdwatch.mqtt_client`)
   - `DetectionPayload`: dataclass matching the cloud Detection model.
   - `MQTTClient`: connects to AWS IoT Core with mTLS, publishes to
     `birdnet/detections`; on failure appends to SQLite cache.
   - Offline cache is flushed periodically by a watchdog thread when the
     network is available.

The **Pi entry point** (`birdwatch.pi.main`) wires recorder → analyzer →
MQTT: for each 3 s buffer it runs inference and publishes each detection
above the confidence threshold.

## Running

From the repo root (with venv active and `BIRDNET_MODEL_DIR` set):

```bash
uv run birdwatch
```

Or explicitly:

```bash
BIRDNET_MODEL_DIR=/path/to/model uv run python -m birdwatch.pi.main
```

If AWS IoT env vars are not set, the pipeline still runs but detections only
go to the local offline cache until you configure IoT and restart.

## Troubleshooting

- **“tflite_runtime not installed”** — On the Pi, install it with
  `pip install tflite-runtime` (wheels are platform-specific; use the venv
  from `setup.sh`).
- **No sound device** — Ensure a USB sound card or mic is connected and
  that `libportaudio2` is installed; list devices with Python
  `sounddevice.query_devices()`.
- **MQTT connect failed** — Check endpoint, cert/key paths, and IoT policy
  (publish to `birdnet/detections`, connect with the chosen client id).
  Detections will still be cached and sent when the connection works.
- **High CPU or OOM** — Pi Zero 2 W has 512 MB RAM; using zram or reducing
  overlap (e.g. analyze every 3 s only) can help.
