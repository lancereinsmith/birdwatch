"""BirdNET inference: mel spectrogram and TFLite model."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import librosa
import numpy as np

try:
    import tflite_runtime.interpreter as tflite  # type: ignore[import-untyped]
except ImportError:
    tflite = None

# Match BirdNET training (48 kHz, 3 s window, 96 mels; see plan-full.md §2.1.1)
SAMPLE_RATE = 48_000
N_FFT = 2048
HOP_LENGTH = 278
N_MELS = 96
FMAX = 15_000.0
WINDOW_S = 3.0
INPUT_SAMPLES = int(SAMPLE_RATE * WINDOW_S)


def preprocess_audio(buffer: np.ndarray) -> np.ndarray:
    """
    Convert 3 s float32 mono (48 kHz) to mel spectrogram.

    Uses librosa with BirdNET parameters: n_fft=2048, hop_length=278,
    n_mels=96, fmax=15000. Output shape suitable for BirdNET TFLite input.
    """
    if buffer.size < INPUT_SAMPLES:
        pad = np.zeros(INPUT_SAMPLES - buffer.size, dtype=buffer.dtype)
        buffer = np.concatenate([buffer, pad])
    elif buffer.size > INPUT_SAMPLES:
        buffer = buffer[:INPUT_SAMPLES].copy()
    # Normalize to roughly [-1, 1]
    peak = np.abs(buffer).max()
    if peak > 1e-8:
        buffer = buffer / peak
    mel = librosa.feature.melspectrogram(
        y=buffer,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        fmax=FMAX,
    )
    # Log scale; ensure shape (1, n_mels, time)
    log_mel = np.log(mel + 1e-8).astype(np.float32)
    return log_mel[np.newaxis, :, :]


def _load_interpreter(model_path: str | Path) -> Any:
    """Load TFLite interpreter; requires tflite_runtime on Pi."""
    if tflite is None:
        raise RuntimeError(
            "tflite_runtime not installed (install on Raspberry Pi: pip install tflite-runtime)"
        )
    return tflite.Interpreter(model_path=str(model_path))


def _load_labels(labels_path: str | Path) -> list[str]:
    """Load label list (one scientific name per line)."""
    with open(labels_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


class BirdNETAnalyzer:
    """
    Run BirdNET inference on 3 s audio buffers.

    Expects BirdNET TFLite model and labels.txt in model_dir (or
    BIRDNET_MODEL_DIR). Returns list of (species_index, confidence) above
    threshold.
    """

    def __init__(
        self,
        model_dir: str | Path | None = None,
        confidence_threshold: float = 0.7,
    ) -> None:
        model_dir = model_dir or os.environ.get("BIRDNET_MODEL_DIR", "")
        if not model_dir:
            raise ValueError("model_dir or BIRDNET_MODEL_DIR must be set")
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite"
        self.labels_path = self.model_dir / "labels.txt"
        if not self.model_path.is_file():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        if not self.labels_path.is_file():
            raise FileNotFoundError(f"Labels not found: {self.labels_path}")
        self.confidence_threshold = confidence_threshold
        self._interpreter = _load_interpreter(self.model_path)
        self._labels = _load_labels(self.labels_path)
        self._interpreter.allocate_tensors()
        in_details = self._interpreter.get_input_details()[0]
        self._input_index = in_details["index"]
        self._input_shape = in_details["shape"]

    def run(self, buffer: np.ndarray) -> list[tuple[int, float]]:
        """
        Run inference on 3 s float32 buffer. Returns list of
        (species_index, confidence) above threshold, sorted by confidence desc.
        """
        inp = preprocess_audio(buffer)
        if inp.shape != tuple(self._input_shape):
            # Resize if model expects different (e.g. batch or time steps)
            inp = _resize_to_input(inp, self._input_shape)
        self._interpreter.set_tensor(self._input_index, inp)
        self._interpreter.invoke()
        out_details = self._interpreter.get_output_details()[0]
        logits = self._interpreter.get_tensor(out_details["index"]).squeeze()
        if logits.ndim > 1:
            logits = logits.reshape(-1)
        # Sigmoid
        probs = 1.0 / (1.0 + np.exp(-logits))
        above = [
            (i, float(probs[i]))
            for i in np.argsort(probs)[::-1]
            if probs[i] >= self.confidence_threshold
        ]
        return above[:10]  # Top 10

    def species_name(self, index: int) -> str:
        """Return scientific name for species index."""
        if 0 <= index < len(self._labels):
            return self._labels[index]
        return f"unknown_{index}"


def _resize_to_input(arr: np.ndarray, target_shape: tuple[int, ...]) -> np.ndarray:
    """Broadcast or trim to target shape."""
    t = list(target_shape)
    if arr.shape == tuple(t):
        return arr
    # Flatten and pad or trim
    flat = arr.flatten()
    size = int(np.prod(t))
    if flat.size >= size:
        return flat[:size].reshape(t)
    out = np.zeros(t, dtype=arr.dtype)
    out.flat[: flat.size] = flat
    return out
