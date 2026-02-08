#!/usr/bin/env bash
# Setup Raspberry Pi OS for Birdwatch embedded node (Phase 2).
# Run from repo root or copy to Pi and run there.

set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
  python3-pip \
  python3-venv \
  libatlas-base-dev \
  libportaudio2 \
  portaudio19-dev

echo "Creating venv and installing Python deps..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy librosa sounddevice awsiotsdk

# On Pi ARM, install TFLite runtime (optional on other platforms)
if uname -m | grep -qE 'aarch64|armv7l'; then
  pip install tflite-runtime
fi

echo "Done. Activate with: source .venv/bin/activate"
echo "Set BIRDNET_MODEL_DIR and AWS IoT env vars, then run: python -m birdwatch.pi.main"
