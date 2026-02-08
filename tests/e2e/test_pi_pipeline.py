"""E2E tests that require a Raspberry Pi (TFLite model, optional IoT)."""

import os

import pytest

pytestmark = pytest.mark.pi


@pytest.mark.skipif(
    not os.environ.get("BIRDNET_MODEL_DIR"),
    reason="BIRDNET_MODEL_DIR not set; run on Pi with model",
)
def test_analyzer_loads_and_runs() -> None:
    """On Pi: BirdNETAnalyzer loads TFLite/labels and runs on a buffer."""
    import numpy as np

    from birdwatch.analyzer import BirdNETAnalyzer
    from birdwatch.recorder import BUFFER_SAMPLES

    model_dir = os.environ["BIRDNET_MODEL_DIR"]
    analyzer = BirdNETAnalyzer(model_dir=model_dir, confidence_threshold=0.5)
    assert analyzer.species_name(0)  # at least one label

    buf = np.zeros(BUFFER_SAMPLES, dtype=np.float32)
    results = analyzer.run(buf)
    assert isinstance(results, list)
    # Silent input yields low confidences; no assertion on length
