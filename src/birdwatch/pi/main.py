"""
Main loop for embedded node: record 3 s chunks, run BirdNET, publish to AWS IoT.

Environment:
- BIRDNET_MODEL_DIR: directory containing TFLite model and labels.txt
- AWS_IOT_ENDPOINT, AWS_IOT_CLIENT_ID, cert/key paths for MQTT
- Optional: BIRDNET_OFFLINE_CACHE path for SQLite cache
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from birdwatch.analyzer import BirdNETAnalyzer
from birdwatch.mqtt_client import DetectionPayload, MQTTClient
from birdwatch.recorder import run_recorder


def _run_pipeline(
    device_id: str,
    model_dir: str | Path,
    mqtt: MQTTClient,
    confidence_threshold: float = 0.7,
    noise_floor: float = 1e-4,
    noise_ceiling: float = 1.0,
) -> None:
    analyzer = BirdNETAnalyzer(
        model_dir=model_dir,
        confidence_threshold=confidence_threshold,
    )

    def on_buffer_ready(buffer: object) -> None:
        import numpy as np

        buf = np.asarray(buffer, dtype=np.float32)
        results = analyzer.run(buf)
        ts = datetime.now(tz=UTC).isoformat()
        for idx, conf in results:
            name = analyzer.species_name(idx)
            # species_code: often 4-letter code; use first part of scientific name if needed
            code = name.replace(" ", "_")[:10].lower()
            payload = DetectionPayload(
                device_id=device_id,
                species_code=code,
                scientific_name=name,
                common_name=name,  # Enrichment can fill later
                confidence=conf,
                timestamp=ts,
                lat=None,
                lon=None,
                audio_url=None,
                image_url=None,
            )
            mqtt.publish(payload)

    mqtt.start_watchdog()
    run_recorder(
        on_buffer_ready=on_buffer_ready,
        noise_floor=noise_floor,
        noise_ceiling=noise_ceiling,
    )


def main_pi() -> int:
    """Entry point for Pi: parse env and run pipeline."""
    model_dir = os.environ.get("BIRDNET_MODEL_DIR")
    if not model_dir or not Path(model_dir).is_dir():
        print(
            "Set BIRDNET_MODEL_DIR to directory containing BirdNET TFLite model and labels.txt"
        )
        return 1
    device_id = os.environ.get("BIRDNET_DEVICE_ID", "pi-01")
    endpoint = os.environ.get("AWS_IOT_ENDPOINT")
    client_id = os.environ.get("AWS_IOT_CLIENT_ID", device_id)
    cert = os.environ.get("AWS_IOT_CERT_PATH")
    key = os.environ.get("AWS_IOT_KEY_PATH")
    if not endpoint or not cert or not key:
        print("Set AWS_IOT_ENDPOINT, AWS_IOT_CERT_PATH, AWS_IOT_KEY_PATH for MQTT")
        return 1
    mqtt = MQTTClient(
        endpoint=endpoint,
        client_id=client_id,
        cert_path=cert,
        key_path=key,
        ca_path=os.environ.get("AWS_IOT_CA_PATH"),
    )
    try:
        mqtt.connect()
    except Exception as e:
        print(f"MQTT connect failed (will use offline cache): {e}")
    _run_pipeline(
        device_id=device_id,
        model_dir=model_dir,
        mqtt=mqtt,
        confidence_threshold=float(os.environ.get("BIRDNET_CONFIDENCE", "0.7")),
    )
    return 0
