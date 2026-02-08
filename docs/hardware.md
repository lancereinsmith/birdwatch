# Hardware (Raspberry Pi node)

Bill of materials and assembly notes for the **Stage 2** embedded node,
based on the full [plan](reference/plan-full.md).

## Core: Raspberry Pi Zero 2 W

- **SoC:** Quad-core ARM Cortex-A53 @ 1 GHz, 512 MB RAM.
- **Power:** ~0.7 W idle, ~1.3 W under inference; 5 V supply.
- **Boot:** Full Linux (Raspberry Pi OS); allow ~20–30 s cold boot.
- **Tip:** Use zram swap to reduce OOM risk under load.

## Audio input

The Pi has no built-in analog mic input. Use an external USB audio path.

### Microphone

- **Primo EM272** electret capsule (e.g. “Clippy” style).
  - Sensitivity about -28 dB, low self-noise (~14 dBA).
  - Can be wired to a 3.5 mm jack or a small USB board.

### USB audio adapter

- **Suggested:** UGREEN USB audio adapter or Sound Blaster Play! 3.
- **Avoid:** Very cheap generic dongles (often noisy; can trigger false
  detections).
- Connect the mic to the adapter’s input; set the Pi to use this device as
  the default recording source.

### Wind and weather

- Use a foam windscreen and/or “dead cat” on the mic to reduce wind noise.
- For outdoor enclosures, place the mic in a downward-facing vent (e.g. PVC
  elbow) so it is protected but still receives sound.

## Enclosure (optional)

- **Rating:** IP65 or IP67 if outdoors.
- **Vent:** Acoustic path for the mic; consider a Gore-Tex breather to
  limit condensation inside the box.
- **Mounting:** Secure the Pi and USB adapter inside; keep the mic
  accessible to the environment.

## Power (24/7 / solar)

For continuous or solar-powered use:

- **Battery:** 12 V 12 Ah LiFePO4 (or similar) for several days of
  autonomy with no sun.
- **Solar:** 25–35 W 12 V panel; winter “peak sun” often 2–3 h in many
  regions.
- **Regulation:** MPPT charge controller preferred; efficiency losses
  (e.g. 85–95%) in mind when sizing.
- **Pi supply:** 5 V from a buck converter (e.g. 12 V → 5.1 V, high
  efficiency) to stay within Pi current limits.

Exact sizing depends on location and duty cycle; see the full plan for
energy calculations.

## Assembly checklist

1. Flash Raspberry Pi OS to SD; enable SSH/Wi‑Fi if headless.
2. Connect USB audio adapter and microphone; verify recording in OS.
3. Run `scripts/setup.sh` (or equivalent) to install Python and

  birdwatch deps.

4. Install BirdNET model and labels; set `BIRDNET_MODEL_DIR` (see

  [model-setup](model-setup.md)).

5. Configure AWS IoT (cert/key, policy); set `AWS_IOT_*` env vars.
6. (Optional) Mount in enclosure; connect solar/battery if used.
7. Run `uv run birdwatch` (or `python -m birdwatch.pi.main`) and confirm

  detections and MQTT/cache behavior.
