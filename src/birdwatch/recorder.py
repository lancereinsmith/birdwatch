"""Audio recording and ring buffer for 3-second BirdNET analysis windows."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd

if TYPE_CHECKING:
    from collections.abc import Callable

# BirdNET expects 48 kHz mono, 3 s
SAMPLE_RATE = 48_000
CHANNELS = 1
DTYPE = np.float32
SECONDS = 3.0
BUFFER_SAMPLES = int(SAMPLE_RATE * SECONDS)


class RingBuffer:
    """
    Lock-free ring buffer for continuous 48 kHz mono float32 audio.

    Holds exactly BUFFER_SAMPLES (3 s at 48 kHz). New samples overwrite oldest.
    """

    __slots__ = ("_buf", "_idx", "_full")

    def __init__(self) -> None:
        self._buf: np.ndarray = np.zeros(BUFFER_SAMPLES, dtype=DTYPE)
        self._idx = 0
        self._full = False

    def write(self, chunk: np.ndarray) -> None:
        """Append chunk (1D float32); may wrap around."""
        n = chunk.size
        if n >= BUFFER_SAMPLES:
            self._buf[:] = chunk[-BUFFER_SAMPLES:]
            self._idx = 0
            self._full = True
            return
        k = min(n, BUFFER_SAMPLES - self._idx)
        self._buf[self._idx : self._idx + k] = chunk[:k]
        self._idx = (self._idx + k) % BUFFER_SAMPLES
        if n > k:
            self._buf[: n - k] = chunk[k:]
            self._idx = n - k
        if self._idx == 0 or n > k:
            self._full = True

    def read(self) -> np.ndarray:
        """Return a copy of the current 3 s buffer in chronological order."""
        if not self._full:
            return self._buf.copy()
        return np.roll(self._buf, -self._idx)

    def rms(self) -> float:
        """Root-mean-square amplitude of current buffer (noise gate)."""
        view = self.read()
        return float(np.sqrt(np.mean(view * view)))


def _noise_gate_ok(rms: float, floor: float, ceiling: float) -> bool:
    """Return True if rms is between floor and ceiling (inclusive bounds)."""
    return floor <= rms <= ceiling


def run_recorder(
    *,
    on_buffer_ready: Callable[[np.ndarray], None],
    noise_floor: float = 1e-4,
    noise_ceiling: float = 1.0,
    block_duration_ms: int = 100,
) -> None:
    """
    Run blocking recorder: capture 48 kHz mono, maintain ring buffer, call
    on_buffer_ready with 3 s float32 array when ready; skip if RMS outside
    [noise_floor, noise_ceiling].
    """
    ring = RingBuffer()
    block_samples = int(SAMPLE_RATE * block_duration_ms / 1000)

    def callback(
        indata: np.ndarray,
        _frames: int,
        _time: object,
        _status: sd.CallbackFlags,
    ) -> None:
        chunk = indata[:, 0].astype(DTYPE) if indata.ndim > 1 else indata.astype(DTYPE)
        ring.write(chunk)
        rms = ring.rms()
        if _noise_gate_ok(rms, noise_floor, noise_ceiling):
            on_buffer_ready(ring.read())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        blocksize=block_samples,
        callback=callback,
    ):
        while True:
            sd.sleep(int(block_duration_ms))
