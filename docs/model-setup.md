# BirdNET model and labels

The analyzer (Pi and mobile app) needs the **BirdNET TFLite model** and a
**labels file** that maps output indices to species scientific names.

## Obtaining the model and labels

1. **BirdNET-Analyzer (GitHub)**
   - Repo: [birdnet-team/BirdNET-Analyzer-Sierra](https://github.com/birdnet-team/BirdNET-Analyzer-Sierra)
   - Check the repo for scripts or links to download the TFLite export and
     the species list used at inference time.

2. **Zenodo**
   - BirdNET model v2.4 is published on Zenodo; search for “BirdNET” and
     the version (e.g. 2.4). Example record:
     [Zenodo BirdNET](https://zenodo.org/records/15050749)
   - Download the FP16 TFLite model and the labels file (or species list)
     that matches the model’s output indices.

3. **Naming**
   - The Python analyzer looks for:
     - `BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite` (or the name you pass)
     - `labels.txt` — one scientific name per line, line index = model
       output index.

## Placement

### Raspberry Pi (Python)

- Put both files in a single directory, e.g. `~/birdnet_model/`.
- Set the environment variable:
  - `BIRDNET_MODEL_DIR=/home/pi/birdnet_model`
- The analyzer loads:
  - `{BIRDNET_MODEL_DIR}/BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite`
  - `{BIRDNET_MODEL_DIR}/labels.txt`

If your files use different names, either rename them or extend the
analyzer to accept configurable filenames.

### Flutter app

- Add the same `.tflite` file and `labels.txt` to `app/assets/`.
- Declare them in `pubspec.yaml` under `flutter: assets:`.
- Load the model with `Interpreter.fromAsset('path/to/model.tflite')` and
  parse `labels.txt` to map indices to names.

## Verifying

- **Pi:** Run the analyzer on a short WAV (3 s, 48 kHz mono) and confirm
  that output indices stay in range and labels match expectations.
- **App:** After wiring inference, run on a known recording and check that
  the top species and labels are sensible.
