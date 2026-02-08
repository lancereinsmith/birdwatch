"""Tests for MQTT client (payload, offline cache)."""

import json
from dataclasses import asdict
from pathlib import Path

from birdwatch.mqtt_client import (
    DetectionPayload,
    _append_cache,
    _delete_cached,
    _init_db,
    _load_cache,
)


def test_detection_payload_roundtrip() -> None:
    p = DetectionPayload(
        device_id="pi-01",
        species_code="turmig",
        scientific_name="Turdus migratorius",
        common_name="American Robin",
        confidence=0.85,
        timestamp="2026-02-08T12:00:00Z",
        lat=37.0,
        lon=-122.0,
        audio_url=None,
        image_url=None,
    )
    d = asdict(p)
    assert d["device_id"] == "pi-01"
    assert d["species_code"] == "turmig"
    assert d["confidence"] == 0.85
    p2 = DetectionPayload(**d)
    assert p2.device_id == p.device_id and p2.confidence == p.confidence


def test_offline_cache(tmp_path: Path) -> None:
    cache = tmp_path / "test_cache.db"
    _init_db(cache)
    p = DetectionPayload(
        device_id="pi-01",
        species_code="code",
        scientific_name="Sci",
        common_name="Common",
        confidence=0.9,
        timestamp="2026-02-08T12:00:00Z",
        lat=None,
        lon=None,
        audio_url=None,
        image_url=None,
    )
    _append_cache(cache, p)
    rows = _load_cache(cache)
    assert len(rows) == 1
    payload_json, created_at = rows[0]
    loaded = json.loads(payload_json)
    assert loaded["device_id"] == "pi-01"
    _delete_cached(cache, [created_at])
    assert len(_load_cache(cache)) == 0
