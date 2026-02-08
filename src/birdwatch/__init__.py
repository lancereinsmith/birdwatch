"""Birdwatch: bioacoustic bird ID — embedded (Raspberry Pi) and cloud support."""


def main() -> None:
    """Entry point for birdwatch CLI. Runs Pi pipeline if BIRDNET_MODEL_DIR set."""
    import os
    import sys

    if os.environ.get("BIRDNET_MODEL_DIR"):
        from birdwatch.pi.main import main_pi

        sys.exit(main_pi())
    print("Usage: set BIRDNET_MODEL_DIR (and AWS IoT env) then run birdwatch")
    print("See docs/embedded.md and TODO.md")
    sys.exit(0)
