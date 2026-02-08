"""Tests for recorder (RingBuffer, noise gate)."""

import numpy as np

from birdwatch.analyzer import N_MELS, preprocess_audio
from birdwatch.recorder import BUFFER_SAMPLES, RingBuffer


def test_ring_buffer_write_read() -> None:
    ring = RingBuffer()
    chunk = np.ones(1000, dtype=np.float32) * 0.5
    ring.write(chunk)
    out = ring.read()
    assert out.shape == (BUFFER_SAMPLES,)
    assert out.dtype == np.float32
    # Only first 1000 filled
    assert np.all(out[:1000] == 0.5)
    assert np.all(out[1000:] == 0.0)


def test_ring_buffer_rms() -> None:
    ring = RingBuffer()
    ring.write(np.ones(BUFFER_SAMPLES, dtype=np.float32) * 0.5)
    assert abs(ring.rms() - 0.5) < 1e-6


def test_preprocess_audio_shape() -> None:
    buf = np.random.randn(BUFFER_SAMPLES).astype(np.float32) * 0.1
    mel = preprocess_audio(buf)
    assert mel.ndim == 3
    assert mel.shape[0] == 1
    assert mel.shape[1] == N_MELS
    assert mel.dtype == np.float32
