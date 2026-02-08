"""AWS IoT MQTT client for publishing detections; offline SQLite cache and flush."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_mqtt() -> tuple[ModuleType | None, Any]:
    try:
        from awscrt import mqtt as mqtt_mod
        from awsiotsdk import mqtt_connection_builder  # type: ignore[import-untyped]

        return mqtt_mod, mqtt_connection_builder
    except ImportError:
        return None, None


mqtt_crt, mqtt_connection_builder = _load_mqtt()

TOPIC = "birdnet/detections"


@dataclass
class DetectionPayload:
    """Payload published to birdnet/detections; matches Amplify Detection schema."""

    device_id: str
    species_code: str
    scientific_name: str
    common_name: str
    confidence: float
    timestamp: str  # ISO8601
    lat: float | None
    lon: float | None
    audio_url: str | None
    image_url: str | None


def _default_cache_path() -> Path:
    return Path(os.environ.get("BIRDNET_OFFLINE_CACHE", "offline_cache.db"))


def _init_db(cache_path: Path) -> None:
    conn = sqlite3.connect(cache_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def _load_cache(cache_path: Path) -> list[tuple[str, float]]:
    """Return list of (payload_json, created_at)."""
    conn = sqlite3.connect(cache_path)
    rows = conn.execute(
        "SELECT payload, created_at FROM detections ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


def _delete_cached(cache_path: Path, created_ats: list[float]) -> None:
    if not created_ats:
        return
    conn = sqlite3.connect(cache_path)
    placeholders = ",".join("?" * len(created_ats))
    conn.execute(
        f"DELETE FROM detections WHERE created_at IN ({placeholders})", created_ats
    )
    conn.commit()
    conn.close()


def _append_cache(cache_path: Path, payload: DetectionPayload) -> None:
    conn = sqlite3.connect(cache_path)
    conn.execute(
        "INSERT INTO detections (payload, created_at) VALUES (?, ?)",
        (json.dumps(asdict(payload)), time.time()),
    )
    conn.commit()
    conn.close()


def _is_connected() -> bool:
    """Simple connectivity check (e.g. try DNS or a lightweight request)."""
    import socket

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False


class MQTTClient:
    """
    Publish Detection payloads to AWS IoT Core (birdnet/detections).
    Uses mTLS (cert/key). Offline cache and watchdog thread to flush when online.
    """

    def __init__(
        self,
        endpoint: str,
        client_id: str,
        cert_path: str | Path,
        key_path: str | Path,
        ca_path: str | Path | None = None,
        cache_path: Path | None = None,
        flush_interval_sec: float = 60.0,
    ) -> None:
        if mqtt_connection_builder is None:
            raise RuntimeError("awsiotsdk not installed")
        self.endpoint = endpoint
        self.client_id = client_id
        self.cert_path = Path(cert_path)
        self.key_path = Path(key_path)
        self.ca_path = Path(ca_path) if ca_path else None
        self.cache_path = cache_path or _default_cache_path()
        self.flush_interval_sec = flush_interval_sec
        self._connection: Any = None
        self._lock = threading.Lock()
        _init_db(self.cache_path)

    def connect(self) -> None:
        """Build and connect MQTT over mTLS."""
        builder = mqtt_connection_builder.mtls_from_path(
            endpoint=self.endpoint,
            cert_filepath=str(self.cert_path),
            pri_key_filepath=str(self.key_path),
            client_id=self.client_id,
        )
        if self.ca_path and self.ca_path.is_file():
            builder.with_certificate_authority(str(self.ca_path))
        self._connection = builder.build()
        self._connection.connect().result(timeout=10)

    def disconnect(self) -> None:
        """Disconnect MQTT."""
        with self._lock:
            if self._connection:
                self._connection.disconnect()
                self._connection = None

    def publish(self, payload: DetectionPayload) -> bool:
        """
        Publish payload to birdnet/detections. If not connected, append to
        offline cache and return False.
        """
        body = json.dumps(asdict(payload))
        with self._lock:
            if self._connection is None:
                _append_cache(self.cache_path, payload)
                return False
        try:
            assert mqtt_crt is not None
            self._connection.publish(
                topic=TOPIC, payload=body, qos=mqtt_crt.QoS.AT_LEAST_ONCE
            ).result(timeout=5)
            return True
        except Exception:
            _append_cache(self.cache_path, payload)
            return False

    def flush_cache(self) -> int:
        """Connect if needed, publish all cached payloads, remove from DB. Return count flushed."""
        with self._lock:
            conn = self._connection
        if conn is None and _is_connected():
            try:
                self.connect()
            except Exception:
                return 0
        rows = _load_cache(self.cache_path)
        if not rows:
            return 0
        flushed = 0
        created_ats: list[float] = []
        for payload_json, created_at in rows:
            try:
                _ = DetectionPayload(**json.loads(payload_json))  # validate shape
                with self._lock:
                    c = self._connection
                if c is None:
                    break
                assert mqtt_crt is not None
                c.publish(
                    topic=TOPIC, payload=payload_json, qos=mqtt_crt.QoS.AT_LEAST_ONCE
                ).result(timeout=5)
                flushed += 1
                created_ats.append(created_at)
            except Exception:
                break
        if created_ats:
            _delete_cached(self.cache_path, created_ats)
        return flushed

    def start_watchdog(self) -> None:
        """Start background thread that periodically flushes cache when online."""

        def run() -> None:
            while True:
                time.sleep(self.flush_interval_sec)
                self.flush_cache()

        t = threading.Thread(target=run, daemon=True)
        t.start()
