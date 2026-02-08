# PLAN

## BACKGROUND

I would like to create an app for bird identification that will work in two stages: 1) an iOs and Android app that just listens on the microphone for audio and identifies the bird calls and songs it hears. and 2) and embedded system that can run on Raspberry Pi or Adafruit hardware that does the same things but uploads the birds it hears to a server that is accessible by the app in stage 1.  

Please see the research below and start to work on this app.

Please keep track of your progress in a TODO.md file.  

Please make documentation using mkdocs. I use uv for python and dependency management. I use ruff for formatting and linting, and I use ty for type checking. Please create a testing suite using pytest.

## **1. Executive Summary**

This report articulates a comprehensive technical specification for the design, development, and deployment of a dual-stage bioacoustic monitoring system. The project mandate envisions a cohesive ecosystem comprising two distinct operational nodes: a mobile application (Stage 1) for real-time, user-directed avian identification on iOS and Android platforms, and an autonomous embedded system (Stage 2) capable of continuous, passive acoustic monitoring (PAM) on Raspberry Pi or Adafruit hardware.

The core technological driver for this ecosystem is **BirdNET**, a state-of-the-art deep learning framework developed by the K. Lisa Yang Center for Conservation Bioacoustics at the Cornell Lab of Ornithology. By leveraging the BirdNET-Analyzer (v2.4) architecture, specifically its TensorFlow Lite (TFLite) derivatives, this system aims to bring research-grade ecological inference to the edge.

The architectural strategy recommended herein prioritizes a **Serverless Cloud Native** approach using **AWS Amplify Gen 2**, facilitating seamless synchronization between the autonomous field nodes and the user-facing mobile client. This report provides an exhaustive analysis of hardware selection—weighing the computational robustness of the Raspberry Pi Zero 2 W against the energy efficiency of ESP32-S3 based Adafruit feather boards—and details the complex signal processing pipelines required to bridge raw audio capture with mel-spectrogram-based neural network inputs. Furthermore, it integrates external ornithological data sources, including the **eBird API** for geospatial validation and **iNaturalist** for taxonomic metadata, to ensure high-fidelity species reporting.

This document is structured as a directive specifically for a coding agent or senior engineering team, covering hardware bills of materials (BOM), software schema definitions, API integration logic, and power management physics for long-duration outdoor deployment.

## **2. Bioacoustic Theory and Model Architecture**

To successfully implement a bird identification app, one must first understand the underlying mechanics of the classification engine. Unlike generic audio classifiers that might rely on simple waveform analysis, modern avian bioacoustics is fundamentally an image recognition problem.

### **2.1 The BirdNET Neural Network Architecture**

The BirdNET-Analyzer framework represents a paradigm shift in ecological monitoring. It utilizes a deep Convolutional Neural Network (CNN) based on the **EfficientNet** backbone.1 EfficientNet is chosen for its superior parameter efficiency, balancing accuracy with computational cost—a critical factor when deploying to edge devices like mobile phones or microcontrollers.

#### **2.1.1 Input Representation: The Mel Spectrogram**

The BirdNET model does not ingest raw audio directly. Instead, the audio signal must be transformed into a visual representation known as a **Mel Spectrogram**. This transformation mimics the non-linear human perception of sound (the Mel scale) and aligns with the physiological production of sound by the avian syrinx.

- **Sampling Rate:** The model is trained on audio sampled at **48,000 Hz (48 kHz)**. This high sampling rate is necessary to capture the high-frequency components of bird calls, which can extend well into the 10-15 kHz range.2
- **Spectrogram Parameters:**

- **FFT Window Size:** 2048 samples.
- **Hop Length:** 278 samples.
- **Mel Bins:** 96 vertical bands.
- **Frequency Range:** 0 Hz to 15,000 Hz.

- **Input Tensor Shape:** The TFLite model typically expects an input tensor of shape (representing a 3-second audio chunk) or a raw audio buffer of if the model includes a preprocessing layer (though most lightweight exports do not).2

#### **2.1.2 Inference Mechanics**

The inference process operates on a fixed temporal window, typically **3.0 seconds**.

1. **Buffering:** The system continuously captures audio into a rolling buffer.
2. **Segmentation:** Every 3 seconds (or with an overlap, e.g., every 1 second), a 3-second slice is extracted.
3. **Preprocessing:** The slice is normalized (amplitude scaling to -1.0 to 1.0) and converted to a Mel Spectrogram.
4. **Forward Pass:** The spectrogram is passed through the CNN layers (Convolution -> Batch Normalization -> Activation -> Pooling).
5. **Classification:** The final fully connected layer outputs a vector of probabilities corresponding to the ~6,000 supported species classes.1
6. **Post-Processing:** A sigmoid function applies a sensitivity threshold (typically 0.7 or higher) to filter out low-confidence predictions.

### **2.2 Edge AI and Quantization**

For both the mobile app and the embedded system, utilizing the full TensorFlow model (hundreds of megabytes) is impractical. Instead, we utilize **TensorFlow Lite (TFLite)**. This involves **quantization**, a process where the model's weights are converted from 32-bit floating-point numbers (FP32) to 16-bit floats (FP16) or 8-bit integers (INT8).

- **FP16 Quantization:** Reduces model size by 50% with negligible accuracy loss. Recommended for modern smartphones (Stage 1) which often have hardware acceleration for FP16 operations.
- **INT8 Quantization:** Reduces model size by 75% and significantly speeds up inference on integer-only hardware (like some microcontrollers). However, for the Raspberry Pi Zero 2 W, the FP16 or standard TFLite model is generally preferred to maintain higher accuracy on subtle bird calls.3

## **3. System Architecture and Topology**

The proposed solution utilizes a **Edge-to-Cloud-to-Edge** topology. This architecture ensures that the embedded system (Stage 2) can operate autonomously in the field, while the mobile app (Stage 1) serves as both an independent sensor and a visualization client for the field data.

### **3.1 Tier 1: Mobile Perception Client (Stage 1)**

- **Platform:** Flutter (Dart).
- **Role:** Active Sensor & User Interface.
- **Key Responsibilities:**

- Real-time audio capture and spectrogram generation.
- On-device inference using tflite_flutter.
- Geospatial validation using eBird API.
- Data synchronization via AWS AppSync.
- Rich media retrieval via Wikipedia/iNaturalist.

### **3.2 Tier 2: Autonomous Acoustic Node (Stage 2)**

- **Platform:** Raspberry Pi Zero 2 W (or ESP32-S3 alternative).
- **Role:** Passive Acoustic Monitor (PAM).
- **Key Responsibilities:**

- 24/7 Audio buffering and event triggering.
- Local inference using tflite_runtime.
- Power management (Solar/Battery).
- Telemetry upload via MQTT (AWS IoT Core).

### **3.3 Tier 3: Cloud Orchestration Layer**

- **Platform:** AWS Amplify Gen 2.
- **Role:** Backend-as-a-Service (BaaS).
- **Key Responsibilities:**

- Identity Management (Cognito).
- Data Persistence (DynamoDB).
- Real-time Synchronization (AppSync/GraphQL).
- Binary Storage for Audio Clips (S3).

## **4. Stage 1: Mobile Application Development Plan**

The mobile application is the primary touchpoint for the user. It must be responsive, visually engaging, and capable of performing heavy computational tasks (DSP and Inference) without freezing the user interface.

### **4.1 Framework Selection: Flutter**

**Flutter** is the recommended framework for this application.

- **Performance:** Flutter's Impeller rendering engine ensures smooth UI performance (60/120fps) even while the CPU is under load from audio processing.
- **Cross-Platform:** A single codebase targets both iOS and Android, reducing development time by ~40%.
- **Native Integration:** Flutter's Platform Channels (FFI) allow efficient communication with native C++ libraries for Digital Signal Processing (DSP), which is critical for fast spectrogram generation.4

### **4.2 Audio Processing Pipeline (The DSP Layer)**

This is the most technically demanding component of the mobile app. The TFLite interpreter on mobile generally cannot execute the complex "Mel Spectrogram" operations inside the model graph because standard TFLite delegates (GPU/NPU) do not support the custom Flex Ops required for signal processing. Therefore, **preprocessing must happen in the app code** before inference.

#### **4.2.1 Audio Capture Strategy**

We utilize the flutter_sound or record package to capture raw PCM audio.

- **Configuration:**

- **Format:** PCM 16-bit Integer.
- **Channels:** Mono (1 channel).
- **Sample Rate:** 48,000 Hz.
- **Buffer Size:** Circular buffer holding 144,000 samples (3 seconds).

#### **4.2.2 The Spectrogram Challenge**

Dart (Flutter's language) is fast, but performing Fast Fourier Transforms (FFT) on 144,000 samples every second can cause UI jank (dropped frames).

- **Solution:** Use **Flutter FFI (Foreign Function Interface)** to bind to a high-performance C++ library like **KissFFT** or a compiled version of **Librosa (C++)**.
- **Process Flow:**

1. Dart captures audio stream -> Writes to Shared Memory Buffer.
2. Dart calls C++ function via FFI.
3. C++ performs STFT and Mel-Binning -> Returns Float32List (Spectrogram).
4. Dart passes Float32List to the TFLite Interpreter.

### **4.3 Inference Engine Integration**

We recommend the **tflite_flutter** package over google_mlkit for this specific use case because it offers granular control over tensor shapes and threads.4

- **Model Loading:** The app assets must include the BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite file (~20MB) and the labels.txt mapping file.
- **Interpreter Settings:**

- **Threads:** 2-4 (depending on device core count).
- **Delegates:** Enable NNAPI (Android) or CoreML (iOS) delegates if the model supports hardware acceleration. However, note that some custom architectures behave more predictably on the CPU delegate for audio models.

### **4.4 Data Enrichment: API Integration**

Raw BirdNET output provides only a scientific name and a confidence score. To satisfy the requirement for a "nuanced understanding," we must enrich this data.

#### **4.4.1 eBird API Integration**

The **eBird API 2.0** is essential for spatial validation.5

- **Use Case:** Reducing False Positives.

- *Scenario:* BirdNET detects a "Common Nightingale" with 0.65 confidence. The user is in California. Nightingales are not present in California.
- *Logic:* The app queries eBird's "Recent Observations in a Region" endpoint (/v2/data/obs/{regionCode}/recent) for the user's current US County (e.g., US-CA-037). If the detected species is not in the recent list, the app flags the detection as "Unlikely" or suppresses it.

- **Endpoint Details:**

- Base URL: <https://api.ebird.org/v2>
- Header: X-eBirdApiToken: <API_KEY>
- Region Code: Retrieved via reverse geocoding (Lat/Lon -> County Code).

#### **4.4.2 iNaturalist & Wikipedia Integration**

For imagery and descriptions, **iNaturalist** and **Wikipedia** are the primary sources.

- **Wikipedia API:**

- The Page Summary endpoint is ideal for mobile apps.
- GET <https://en.wikipedia.org/api/rest_v1/page/summary/{Scientific_Name}>
- Returns: High-quality thumbnail, short description, and extract.6

- **iNaturalist API:**

- While iNaturalist has a vision API, for this audio app, we use it for taxonomy and secondary images.
- GET <https://api.inaturalist.org/v1/taxa?q={Scientific_Name}>
- Returns: Common names in localized languages, default photo, and conservation status.7

## **5. Stage 2: Embedded Autonomous System Hardware Research**

The embedded system requires a rigorous hardware selection process. The user mentioned "Raspberry Pi or Adafruit hardware." We will analyze two primary pathways: the **Linux-based SBC (Single Board Computer)** and the **MCU (Microcontroller)** approach.

### **5.1 Pathway A: Raspberry Pi Zero 2 W (Recommended)**

The **Raspberry Pi Zero 2 W** sits in the "Goldilocks zone" for this project. It runs a full Linux OS (Debian), supporting the Python data science stack (numpy, librosa, tflite_runtime) required for BirdNET, yet it consumes significantly less power than a Pi 4 or 5.

- **Processor:** Quad-core 64-bit ARM Cortex-A53 @ 1GHz.
- **RAM:** 512MB LPDDR2. (Note: This is tight for memory-heavy operations. Use zram swap to prevent OOM crashes during inference).
- **Power Consumption:**

- Idle: ~0.7 Watts (140mA @ 5V).
- Load (Inference): ~1.3 Watts (260mA @ 5V).8

- **Advantages:** Runs the full **BirdNET-Analyzer** code or the optimized **BirdNET-Pi** distribution directly. Easiest development path (Python).
- **Disadvantages:** Higher power consumption than a microcontroller; requires ~20-30 seconds to boot.

### **5.2 Pathway B: Adafruit / ESP32-S3 (Alternative)**

For "Adafruit hardware," the **Adafruit ESP32-S3 Feather** is the leading candidate. The ESP32-S3 has AI vector instructions that accelerate TFLite Micro inference.

- **Processor:** Dual-core Xtensa LX7 @ 240 MHz.
- **RAM:** 8MB PSRAM (essential for buffering 3 seconds of audio).
- **Power Consumption:**

- Deep Sleep: ~100 µA.
- Active: ~0.5 Watts.

- **Software:** **BirdNET-Tiny** or **Edge Impulse**.

- *Constraint:* You cannot run the full BirdNET model. You must run a distilled/quantized version (BirdNET-Tiny) or train a custom model via Edge Impulse.9 This reduces accuracy compared to the Pi implementation.

- **Verdict:** Unless extreme battery life is the only priority, the **Raspberry Pi Zero 2 W** is superior for *species diversity* and *accuracy* because it runs the full 6,000-class model. We will proceed with the Pi Zero 2 W design.

### **5.3 Hardware Bill of Materials (BOM) & Engineering**

To achieve 24/7 operation, the system must be ruggedized and energy-independent.

#### **5.3.1 Audio Input Subsystem**

The quality of the microphone determines the detection range.

- **Sensor:** **Primo EM272** Electret Condenser Capsule.

- *Specs:* -28dB sensitivity, 14dBA self-noise (extremely quiet).
- *Implementation:* Can be purchased as a pre-assembled "Clippy" mic or DIY soldered to a 3.5mm jack.11

- **Interface:** **USB Audio Adapter**.

- The Pi Zero 2 W lacks an analog audio input.
- *Recommendation:* **UGREEN USB Audio Adapter** or a **Sound Blaster Play! 3**. Avoid generic $2 dongles as they often introduce electronic whine/hiss that confuses the AI.

#### **5.3.2 Power Management (Solar Physics)**

Running a load of ~1.5W (average with WiFi uploads) continuously requires a robust solar setup.

- **Daily Energy Budget:** ![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAVwAAAAuCAYAAABki6FSAAAQAElEQVR4AezdBXQzMXIH8JSZmZmZma9XZnxXZmamKzMzMzMzc3tlZmZm7sH/52flTZRde+3Yib9EeRpLGsHuzkqjmdFo89Bn429QYFBgUGBQ4FooMBjutZB5XGRQYFBgUODsbDDcMQoGBQYFBgWmKHAE3GC4RyDq6HJQYFBgUGCKAoPhTlFl4AYFBgUGBY5AgcFwj0DU0eWgwKDAdVPg3rjeYLj3xnsadzkoMChwCygwGO4teInjEVYUePj8PlHgWQNPHBhhUOBQFHiUdPRkgecMPGpg77ALw338XOVhAscIj7VDp4/e1ZX/peB+JvBjgR8J/FABefifDe4dAi28ehI/Efj+wHcFvjPwHQGx/PcmrZ8HJH6mQA1PkQz8Dyb+noA22rZ2Px7cawTuQniEPORTBzC8RAcNj5zePi7w3oGp8G5B/kng3wL/E/jLwK8F7hcYYRkFHjvVMBPvMcmDBHziqdKTuZnoUoBQdsrz9mtyk38R+O/Avwf+NOB+nzHx3mEJw33Y9P6egT8PvHXgGOGP0qmH+fDELxYwAExg137S5F8w8IGBXwh48ETnwTOo/yzBaPsSiV+qgPyLJo9peslJroJVC07dVwjmFQOvFBDL3zdpZc+Q+OECNbgvktRLB/lyAW20be2ePzjMItGtDJ7tY/Jkvx4wGP8g8X8Gfj/wpQEMONGVg2u8V3p5o8BUsFA/XgquJHWk/V0LxrNFzHz6+zy8OYWx/E3SXxIw7hPtFMzDN0gLfRoLf5j0vwT+LEDQMWeSPA/qn/K8JWCCQy5Es364VqinDWkwORLExyftJT1U4kMHfT5GOiWuux5ptA0AUosX9tMpx4yfO/EnBGr452QeN/BoAZLn7yaugYRkQmK2H10KvjLpxwlg7Bjmg5Ou4dWSQWz39qtJ14DB6BOT/9pS8H1JP19Amf6TvHXBokaKfJ88Gdp9Y2KT7IGJnybwxoHfCnhPJlWSe4UXT6t3DGwK908h5v9siTH+RCNsoQAJjXDzsamHIX5w4rcMfFEAU3yTxDS7T0ns/SbaGiywv5xaXxEg2X53YguluWcOfUbynxWo4dTnLWHKvRvP9b6vlO4nxFent98O/Ffg9wKY3LHtYZh7LnUpYMT1/v4vNd498BGBuYBRGzi1nCRrxa24mn5QMgYIRp/keXD9/z3PXU5o95tBU1/RCxPCuH8+OPea6NYFk4npxILyPHm6pw+8fuB5A8YJE0uSZybqeyRhwiXaOWCi3qN3sKQxSdt9Lal7l+sQOr41BBBb0DAVc/wLg3uLgHybK++SPH5wlnhTIAT9VCpY9JjZaI3MdRZci/LbpYzJ560Sv1BgKpzqvDXHvzw3/NeBg4TK0HT4XPkhyRq8Vj5S3n8Ed8zgoTb1r5zkSAL+5E0V12XfsI5b5BmWTFySWmsjfk0/C+DZU+eRAiRaUl6StzJYGL8qT+YZSbm/mHQN/5AM8wrpKMlVwHTfcJXa7YcmQlrepZX72qX+XaxL6rRIPmIe/jkC/bz4leBIqYlWwRxgjltlJn5Iyz8a/BME7IW8ZGJmiUSrQAM0H2mfEHMMV5l64ganNG8PNrZ6houABjpCf1ie/NsCGF6io4XWP1PA++cqVI8vS0w6etvE7DwmMmky2a2Buk9lahXZgKn5LT8X9wzklVORipVoY2C7VaFn2HC3CUixbOmkd8/cJlF9RgPzfSsiaVpJosXBBH+n1Cb1JBrhgBR4kXVf7N6fnjRaJ7oQ+nnG/nqhwjqDWX9e0rSdRGfmLk1PugHm3tLiTfPpTszbnuEiyk0A+ymxnWTjBbMjUUc+Nzdj5znRTuGbutoWkA51KXufDmP31ordoS9lXyUYNl4bRkne2oDhejgbCZ+UxIcEpsLPBYkeiVaB1mQhX2W2/NAUmBJ+I/U+NbBLaAv3Lm1uX93NT8QmWWuQcmte+h/9FJhaWBWz+9J0pHkIMaVJV+DB88drBMnXzv86Oxmd6rw92Ng6FYZ7sAdav8Ze2lzCcNmd1s3Po23t+H3ySOivd97BnokXSLurupW9TvpYyuhSdWugadRKtI6ar2naSs0v3fVmT7QB8+ZpvMl+nuJL4dBj6NIFbgGCPbI9Bltt3fBteLb4lhb/jp8J+ICCo5WW7HmSxEtjZuc1frZpLf082jb/XOg65u3BxtapMFwSLuIdCuySg9bf0yXBjSvRZLAZxEbMRlkrbLMjvWoqU636lTnoKwXXNfj2dcP7qFz96wJTKmPQewWbLbWhjcaar2nSTM33klUta2nmCn61nxgEKTnRTuFgk2Knq95blT8nt2vPwQYZU9vfJd+HZ+4QfMo71Blth0dQw/NQaOk+9l6Y+Jii+rI+b86Chj+VeesZ2j1dKT4Vhnulh5hp3DPB15qpB91WyY9MpqrDVnuMIOjJQArlzWGXfLLCnkjuTt+ctibINteoVLsQuPC9XzBs4F+Q+FCBax462dxglyWNzvXdL27sc3N14THkL04CLW3WJrlzmFu0MQZ+vJ+fHvkIM4XYzEn2psONXJ83DbPNP01cnUnHO25FvA76hVZZP5ea2Y/wgWEzsz2hinvAKc7bqbGFdzLJ2G+wYc78aZOYi+rsY2s0W3iNBfWBSJpcSux2Y2Tfnvt43YBd8kSLQ//iNqknGKfNAkCyrBeZa8c/lxtNf53adt/0/6chdyvPbnOD5BfU1oBuDqmwsbKBb22wYwWTj6mCt8i/zrQ1priMtWLvti5iDV9jTNYGC1MCB/xatjTdSyE2aKi6DtVYwEj7fCpdy/1YkJb2fVfqfVAelMtYojNeJ1y5vD/5CtWcxPTD7mtRIzGzv9ts/6s0sK/h8Ao3wWQXhX4+zc0/nV3XvO3Hln0Mkj9NzJh9mdwMbdT8c+DjtZOfDCbHZME1I71UxvnPzHUZ371o9h8Mlz2TrcnLe+GULw28DprBXhuqlMMc0hUQz+4tyQ2+f+FeKnwPvBi40PX1+3r75qlgmBsXPQyUS8+mvqjiVljMULyp7jHLvK+2c+06FjCHZ6SnwKaaZ7Ow8OecqrMrzgk0Jg++odRSwD8UU8cUjHvXfL1dO76l9Z8yz2UBohkleeZUKbu7hUm+hycpCJvdtDDj712Dd5joyROT/JgtLPyO1/OHD3prOPV5S3vzmQALi2c1fu3lMAN6OHzMaT22a/kLYOBdQNxQxgrixt8s17ei8RDgekTKM1HsghoUdj13YbrU8nR5HqaYJzssOmAMKmLyVFtpgHCYtXQF92lgWuUq/pBp0gP1zbcaTAjHMaf6N9ip+U4HiafqXBeORNOuRVolUbZ8H5NCqbcYMreivnzfPNe0x0xjGkg1Z3ivFq8UrQLpZJVY8DNXxRglRR8TlnjLzN3fHN6+BWmMn717twBx6/MeLExMD1NtaZpVbTZXeZS8fSrz4SXtOh3qdFlb0Pjf1g27VN0YTnneOiRC0yPROtDhQQiMpHrfX5G3uNDKpS8ARnMBsSXDRrOlyl7FpDnHeDFEN+7Ft46oNk69yFs9fCDGS5bfBr30qf++DcZJeq6red9OndrOSaiXD8LAQOwkjxYwXdfHdB3H7JluY7afljtYanpI1aMEErkTTDpHlzdNgpkm0WTAGNnBuBjZNZ+stAfSuOZaaFz1zdukgGdmuOqY9nw+grQrUEmdbgQOD5ACfzg3BZjTnNr7geSBhT3JgwaM9uvTI9s2+7n7x0y5ZVq0SW8pvhRohOjbCmgznqVpiA0vNpeblmnuER7gt0E//7Tt25gTNzFvvQvjtr8f+Tq2mssc/DlUwp0jNySuOjjnusZQHYutN1zrMt4b2HBsp0tVZioqlUc7YAOM+C8N9MX+0qRbONC/cC8XvgFmi+n29Vr5oeM5ptuYLWkCDQ993V36Qw8bdq0NiYkpqOX72OYKm6HNBsymL79K3lgBU31UJuyemYWm6i3FWajZL3cF9mSLArAw0e5I3IAXgUWIaQ1gLEvvZ2m9v01F6j4zgGtiEBgJc4Hj8zQ9Lo+pdiE4pXYBkQztK9GlYNElILWCTRutrY74lOctEx/NzX32UMcWDasvn/14zaWKa8SxGK4V1qq+vsxkVFUc9iFi+2TFgmSqIP43lPtvthY4dlgG/Z5xMhNYydQBbIFMC9LASu0rS1Z2+euAnumSjEgin52Lv3PgJgO6Uhl5BKA5dctiMHdPFnqqmcWwl9jn2uyCf8CGylV7Us29iAecndGgeOqgBS8DknfTWOAARi2uwFRT8zVdXQSZB319r5ZPpY2hU523hL+pe4arY2tyXE0itTxBwODabTEtLHlx6vfMtKonGCfGisGq28DK/C0ts46blMuFCaM2ICqB19WOGmG6dkC54ZBIbDBSAd3vUS+8pXMnBNHH/bFdUVM3NSGN0zYw5mYH21R/1zL3Mdemf2cWi7m6dxFv4WzPTZrlWihuOKaIav7BHJvZoNWpcS8NGre1fC59qvN26diaHFe7MtzJTuYotgN+iVpXGa6u7TyLtwGbmE/BtXp2X4n71EmmAYx1imH1LxxD0cfL5ofrTF8e9NGD90Wi5R/sBBAHdJ+0PPqFN1zgbVJGNfWpP/TszTMpvhBoClRWPrFzJqQLDfbI9Ey1doFB1PxIX6SAU4LV5c88Y/aotaqUa/HfxIS4ONa2PEhqfi59qvP2SmPLBJ574Cn8oRkuswDGRcrhc1p3P/vr9y+O8b6vM5VnV9F3K8PceUD4WDhHb9dvZTWmslcmz90JoyMVG5A2NWr9Y6e9K2o4ex9vBM77HK59ZKgeszz2fdT+eXhw5aM2+tC7SVLLjReueHWScYq32JnEFroHnZ2debcmrY3TBp6x9eVZG17s/bWyFqNPS29iqq7Z6t21mFeIY7aVVj0N0IdduuIt7DXvfbe8+dXSU7H+Kp4Jr+bn0vo9lXlb6XWlsVU7mnvwijeBav6qaVIjFb+p6TYO5vokldayegSw4qfSPVN1TYyTBwTGOtXGSmaXtZV5drvwbMA8Bkz8Vnbs2HuqzJY3gvvDtDBdEmPzoTz2vbT+mQR8jIRJhpro036trMW+i8C+5z03HInIjniDn0yBU2x8G9nHGnAvStEq8MlueHHVWFYV8oNGiVZh06RYVSg/3mvJ7pzkXmXT6Jhgwdn5xroGXLN8y8DH4rmBTW2ItSb92PaMrUzMtisGhCbxHGDytYwfdM1vSp/KvN1nbE2Oq9rRpgdvZZOdtMI94t6/tWeqtUseBTW/6fx2rSdNda12J6ovKQlDxbjUmYL+hdtVJ631+Km2h8J5Rz2zbX2798Z0fT/hGBtQ7Vo15qdpt9YE5lqFqdbyluZbLc38IQa+8YBBbwPuUOoD/qK1PiYNX4FLU8v3UlXDHyO+Tzplkz4W2BBlhsllrhR49jQPHQcTLNpzHRrjtcyiWvPMcC3PLaylp2LCVMU7MFDzm9KnMm8PNrZM5k0PfNUyEiFHah8onuqrSqkYqKOYU/XgeAqIgQle1X24Azq4GQAABj1JREFUTUBCcvKo1bEqs8Pyo224qdikZ+5oZXwTbQLUvlrZMWILnE2LZkaYmiSV6dpl5o51jHtZ93lm99oBFP9gzw52PxlbPTF7ubgyXPljQB3LdYL010LTiuvztWxJ2gYhpnIssGFFMFhyL5vq9JvMjflOtennq4NHtZ68o7twzENOlElPQTUTkqy5fE3Vm8KdyrzdZ2xNjqva0dQD97jJTvpK67wjpqQZbib+bc/UC+ZWhWGw1ZCGTOJ18wsRRlc/Im7Vv1BhQaaXSv0PLF+p39SUasV8UOtYde3UVtwx0mhtMjOz8G+dYrbtumjIr9NJH6qt7ym0skPGpBn04P7FFOMD8ezHwObd/XMxNmWM34d3SN8+krKLGpkuVqGOTbRYIRf+sNPPVe376vNz7e51PI+W9gxs5t5Py9eY9sIXt+GYb6rnAjwNovpYt4VVWQ80gIYjUGnb8kviU5u3S8fW5Liqg3rq4a1O1QZj02iqXo9zMVJZwzMVsJu2fItJqnbdbaTwKW34Gru+He12r84pk7BqnSVpKrCNmVaXlEpabfm5uN917wfAXLur4tGFA/xSUwG7JQZncmxj0Pvcm/fgNFHbdHF+/kPTEfsx4NQuz+zCtMF7gSaxr3RrkU33q2D8tPe/Qkz8VJOT+hNVVij/7WCVWP/U66xRtzLyrQoLM2Zr/4L9fepBLZwNb344ujwlYKhHkFLXIj91+tM3Spr92YYqIUz9XeCm5y0Ng/bS7nnp2KJBX2LO/SB27t0BBEZxKyL/Ojv57WLsQM5JUwvs0oMpJmwV0761E2sj7sEEtSuKSXghzo27UWohqdamEHurdlT8TZKeOnPAs0D7Vr7NnNDqYcxUG3k7p4dQ7/S1CWyAYVg+JUh63FS3lmG6FjoHSXwzoJ1lr3X2TWOi9StRS/tZynDZgo0n9lmqZ5WMSFw226iy6tgAcn0StlNqvpfANxoO8AW2mCujIWDG2vkwCg1FnQbGng07/zev4W5j7NktiBZO0ilNxKYm4cjzWngwTifm5I15Xig9vZQBTJhPuL0RZibHhHmq6A9f8f74qqvr/dwvCQw/0U7hpuYtDcBY9J0Pgme7aUfobRDjk4QPz2wxcTIPfVs97nTa2hzG21Z4hFkl1j++hIPJOXZpkFMn2OgaUPm1YcRnArCRURnyuptVRGJFcJOHXZGNdlXQ/biG47VerGOGbp59lipqR9rksdIqu2/aqp9or9Ck1SlTwVyHBhamqxzDvsr19bEETA4fA6kvcEk7dTBdkrFNHJtNcIeAfqd6aZ9LGS7Jk+cDlZZEYazVcee5MAh12gQwqH3OkyTd13c4Rpk2XJFIW/7rAJt87df7VQfDX/pM92o9Woj5hAYEHYxQ2jviW2ueejbMg5CzzeRmA8z3c3k++FCQBQ5tzRFtMXHaKJ7iVKG+94GbmLeYqf+YYtzVsYVOFhhuoqR67qnc5oxfZZ4faGPxwUt9L2T13JjnKrH+sclloGrM5soYbpA2kMeIGdVdzED20tbNL0SO4noZBrPvRF4o7DIYrG8peGnsPBgtBk0Ncs7bkUBfJCI5d013ytpdJcn4opWVc2ljq5qVyjcLlra5Sj2LD5PCvn2gk3vuT9Dt2592zvQbQLuCU2jabwMaB8Zp7NGajLU67uAMbnXY/PVH46LimQB9fThlGAsbMtWw9d33C2/zR5+3HUii5jBXPXsExjWmyzZvjhFqbFATfJbQAmPFcNhx9W0zjQToH0xa5Pi7E56W9DVX5ybmLbc5C0bPB9EO/zMOCWCeGc+EU1bHlrb4JJqunq1nuCvkDf54yY6qOs1lB9zmGPWYaeMQt8W3k1pMVd+lPyYW0nz9EMcu7RfVHZUGBa6JAkxjFjhHq7lIYpjMB7RIDHSf2yDdkp71Za4wic2ZEXft/9bM21NjuLu+iFF/UGBQYFDgnqHAYLj3zKsaNzooMChwr1NgMNx93+BoNygwKDAosCMFBsPdkWCj+qDAoMCgwL4UGAx3X8qNdoMCgwKDAjtS4I4w3B2pMqoPCgwKDAocgQKD4R6BqKPLQYFBgUGBKQoMhjtFlYEbFBgUGBQ4AgVOkeEe4TFHl4MCgwKDAjdPgcFwb/4djDsYFBgUuCMUeAgAAAD//zPrrLkAAAAGSURBVAMAS2aXmQH+NP0AAAAASUVORK5CYII=).
- **Solar Panel Sizing:**

- Winter Isolation Factor: In many regions, effective "peak sun hours" in winter drop to 2-3 hours.
- Required Generation: ![img](data:image/png;base64,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).
- Efficiency Loss: Panels rarely hit rated output. Charge controllers have efficiency losses (85-95%).
- *Recommendation:* **25 Watt to 35 Watt 12V Solar Panel**. (Dimensions approx. 45cm x 35cm).

- **Battery Chemistry:**

- **LiFePO4 (Lithium Iron Phosphate):** Superior to Li-Ion for outdoors. Safe (no thermal runaway), performs better in cold, and matches 12V solar systems natively.
- *Capacity:* **12V 12Ah Battery** (![img](data:image/png;base64,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)). This provides ~4 days of autonomy (no sun) (![img](data:image/png;base64,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)), ensuring reliability during storms.

- **Regulation:**

- **MPPT Controller:** A Maximum Power Point Tracking controller is preferred over PWM for efficiency.
- **Buck Converter:** A high-efficiency (95%+) DC-DC Buck converter is needed to step down the 12V battery voltage to 5.1V for the Raspberry Pi.

#### **5.3.3 Environmental Enclosure**

- **Box:** IP65 or IP67 rated ABS junction box.
- **Acoustic Venting:** The microphone must be outside the box but protected.

- *Technique:* Use a downward-facing PVC elbow joint attached to the bottom of the box. Place the mic inside the elbow, covered with an acoustic foam windscreen and a "dead cat" fur cover to mitigate wind noise (which causes false positives in the low-frequency spectrum).12
- *Venting:* A Gore-Tex breather vent is recommended to equalize pressure and prevent condensation buildup inside the sealed box.

## **6. Cloud Service Architecture**

The user requires a system to store and sync data. While AWS is preferred, we must analyze the trade-offs.

### **6.1 Cloud Service Comparison**

| **Feature**         | **AWS Amplify (Gen 2)**          | **Supabase**                | **Firebase**                    |
| ------------------- | -------------------------------- | --------------------------- | ------------------------------- |
| **Database**        | DynamoDB (NoSQL)                 | PostgreSQL (SQL)            | Firestore (NoSQL)               |
| **Real-time Sync**  | AppSync (GraphQL Subscriptions)  | Realtime (Postgres WAL)     | Firestore Listeners             |
| **IoT Integration** | **Native (IoT Core + MQTT)**     | Weak (Requires HTTP bridge) | Weak (Requires Cloud Functions) |
| **Auth**            | Cognito (Robust, Complex)        | GoTrue (Simple)             | Firebase Auth (Simple)          |
| **Learning Curve**  | Medium-High                      | Low-Medium                  | Low                             |
| **Cost**            | Pay-per-use (Free Tier generous) | Generous Free Tier          | Generous Free Tier              |

**Recommendation:** **AWS Amplify Gen 2**.

- *Reasoning:* The presence of the **Stage 2 Embedded System** tips the scale heavily toward AWS. AWS provides **IoT Core**, a dedicated MQTT message broker designed exactly for embedded devices like Raspberry Pis. Integrating a Pi with Supabase or Firebase usually requires polling or writing custom WebSocket code, whereas AWS IoT Core handles the connection management, security certificates, and message routing ("Rules") natively.

### **6.2 AWS Architecture Design**

#### **6.2.1 Data Schema (Amplify DataStore)**

We define the data model in TypeScript (Amplify Gen 2 convention).

TypeScript

// amplify/data/resource.ts
import { type ClientSchema, a, defineData } from '@aws-amplify/backend';

const schema = a.schema({
 Detection: a.model({
  deviceId: a.string().required(), // "pi-garden-01"
  speciesCode: a.string().required(), // e.g., "turmig"
  scientificName: a.string(),    // "Turdus migratorius"
  commonName: a.string(), // "American Robin"
  confidence: a.float().required(), // 0.85
  timestamp: a.datetime().required(), // ISO8601
  location: a.customType({
   lat: a.float(),
   lon: a.float()
  }),
  audioUrl: a.string(), // S3 Link to 3s clip
  imageUrl: a.string(), // Cached Wikipedia Link
 })
 .authorization(allow => [
  allow.publicApiKey(), // For the Pi (simplified) or Guest
  allow.owner() // For the App User
 ])
});

export type Schema = ClientSchema<typeof schema>;
export const data = defineData({ schema });

#### **6.2.2 The IoT Ingestion Pipeline**

This is the critical bridge between Stage 2 and Stage 1.

1. **MQTT Topic:** The Pi publishes detection JSON payloads to birdnet/detections.
2. **IoT Rule:** A SQL-like rule in IoT Core selects these messages: SELECT * FROM 'birdnet/detections'.
3. **Action:** The Rule triggers an AWS Lambda function (IoTToAppSync).
4. **Lambda Logic:**

- Receives the JSON payload.
- (Optional) Validates the species code against an internal list.
- Uses the AWS AppSync SDK (or simple HTTP POST signed with IAM) to execute a GraphQL mutation: createDetection(...).13

1. **Synchronization:** AppSync commits the data to DynamoDB and *immediately* pushes the new record to any connected Mobile App via a GraphQL Subscription.

## **7. Implementation Roadmap (Coding Agent Directive)**

This section contains the specific, actionable instructions to be passed to a coding agent.

### **Phase 1: Cloud Backend (AWS Amplify Gen 2)**

**Directives for Agent:**

1. **Initialize Project:** Create a new Amplify Gen 2 project. Configure amplify/auth/resource.ts to support Email login (for app users) and IAM authentication (for the Lambda bridge).
2. **Schema Definition:** Implement the Detection schema defined in Section 6.2.1.
3. **Storage:** Configure amplify/storage/resource.ts to create an S3 bucket named birdnet-audio-clips with public read access (or signed URL generation).
4. **IoT Integration:**

- Create a Lambda function packages/functions/src/iot-handler.ts.
- Grant this Lambda AppSync:GraphQL permissions.
- Write logic to parse the MQTT event and call the createDetection mutation.
- Generate a setup script to create an AWS IoT Thing and Policy, and download the Cert/Key files for the Raspberry Pi.

### **Phase 2: Embedded System (Raspberry Pi)**

**Directives for Agent:**

1. **Environment Setup:** Create a setup.sh script for Raspberry Pi OS Lite (Bullseye/Bookworm).

- apt-get install python3-pip libatlas-base-dev libportaudio2
- pip3 install tflite_runtime numpy librosa awsiotsdk paho-mqtt

1. **Audio Engine (recorder.py):**

- Use sounddevice library (wrapper for PortAudio).
- Create a RingBuffer class using numpy.roll to maintain a continuous 3-second buffer of Float32 audio at 48kHz.

1. **Inference Engine (analyzer.py):**

- Load BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite.
- Implement a function preprocess_audio(buffer): Normalize audio -> Compute Mel Spectrogram using librosa.feature.melspectrogram. *Important constraint:* Ensure Librosa parameters (n_fft=2048, hop_length=278, n_mels=96) match the model training exactly.

1. **Uploader (mqtt_client.py):**

- Use awsiotsdk. Configure mutual TLS (mTLS) using the certificates generated in Phase 1.
- On valid detection (Confidence > 0.7), publish JSON payload to birdnet/detections.

### **Phase 3: Mobile Application (Flutter)**

**Directives for Agent:**

1. **Dependencies:** Add amplify_flutter, amplify_api, tflite_flutter, flutter_sound, permission_handler.
2. **Real-Time Audio:**

- Implement a AudioStream service. Note: iOS requires specific AVAudioSession configurations for "Measurement Mode" to disable automatic gain control (AGC), which can distort bird calls.

1. **DSP & Inference:**

- Create a dedicated Isolate (background thread) for inference to prevent UI stutter.
- *Spectrogram:* Use the fftea package (Dart) or bind to kiss_fft (C++) for STFT generation.
- *TFLite:* Pass the output tensor to tflite_flutter.

1. **Cloud Sync:**

- Implement Amplify.DataStore.observe(Detection.classType) to listen for incoming birds from the Pi.
- Build a DetectionList widget that updates in real-time.

1. **External APIs:**

- Create WikipediaService to fetch thumbnails.
- Create eBirdService to fetch recent observations for the user's Lat/Lon.

## **8. Operational Considerations and Risks**

### **8.1 False Positives and Noise**

BirdNET is robust, but wind and anthropogenic noise (cars, voices) can cause false triggers.

- **Mitigation:** Implement a "Noise Threshold" in the recorder.py script. If the RMS amplitude of the 3-second buffer is below a certain floor (silence) or above a ceiling (clipping/wind), skip inference to save power and reduce junk data.

### **8.2 Privacy and Legal**

Recording audio in public or semi-public spaces carries legal implications (wiretapping laws).

- **Mitigation:** The embedded system should be configured to **discard raw audio** immediately after analysis unless specifically configured to save short clips of *birds only*. Do not save continuous 24/7 audio. The system acts as a "smart sensor," not a wiretap.

### **8.3 Data Connectivity**

The Raspberry Pi relies on Wi-Fi.

- **Offline Mode:** If the Pi loses Wi-Fi, the mqtt_client.py should cache detections in a local SQLite database (offline_cache.db). A separate "Watchdog" thread should check for connectivity and flush the cache to AWS IoT Core when the connection is restored.

## **9. Conclusion**

This report outlines a complete path to building a professional-grade bioacoustic monitoring system. By combining the precision of the **BirdNET** algorithm with the versatility of the **Raspberry Pi Zero 2 W** and the scalability of **AWS Amplify**, the proposed solution meets all user requirements for both active (mobile) and passive (embedded) identification.

The inclusion of specific hardware calculations for solar power and detailed software integration strategies for TFLite spectrogram generation ensures that this is not just a theoretical concept, but a buildable, operational engineering plan. The recommended utilization of **eBird** and **iNaturalist** APIs transforms the application from a simple detector into a context-aware ecological tool.

| **Component** | **Recommendation**       | **Why?**                                             |
| ------------- | ------------------------ | ---------------------------------------------------- |
| **Model**     | BirdNET v2.4 (TFLite)    | Industry standard accuracy (6,000 species).          |
| **Mobile**    | Flutter + TFLite         | Cross-platform, high-performance UI.                 |
| **Embedded**  | RPi Zero 2 W             | Balance of power (low) and Python support (high).    |
| **Cloud**     | AWS Amplify Gen 2        | Native IoT integration, scalable serverless backend. |
| **Power**     | 30W Solar + 12Ah LiFePO4 | Required for reliable 24/7 winter operation.         |

This specification is ready for immediate hand-off to a development team or coding agent for execution.

### **Works cited**

1. BirdNET-Analyzer, accessed February 8, 2026, <https://birdnet.cornell.edu/analyzer/>
2. BirdNET analyzer for scientific audio data processing. - GitHub, accessed February 8, 2026, <https://github.com/birdnet-team/BirdNET-Analyzer-Sierra>
3. BirdNET Model V2.4 - Zenodo, accessed February 8, 2026, <https://zenodo.org/records/15050749>
4. Integrating TFLite Models into a React Native App for Real-Time Currency Recognition, accessed February 8, 2026, <https://medium.com/@amitvermaphd/integrating-tflite-models-into-a-react-native-app-for-real-time-currency-recognition-6e19006bdcbb>
5. eBird API 2.0 - Postman, accessed February 8, 2026, <https://documenter.getpostman.com/view/664302/S1ENwy59>
6. How to get the "Scientific Classification" information from Wikipedia page using API?, accessed February 8, 2026, <https://stackoverflow.com/questions/64001004/how-to-get-the-scientific-classification-information-from-wikipedia-page-using>
7. Access iNaturalist data through APIs - CRAN, accessed February 8, 2026, <https://cran.r-project.org/web/packages/rinat/vignettes/rinat-intro.html>
8. Raspberry Pi Zero 2 W temperature and power consumption - André Jacobs, accessed February 8, 2026, <https://andrejacobs.org/b24/electronics/raspberry-pi-zero-2-w-temperature-and-power-consumption/>
9. Adafruit IoT Monthly: Bird Classification Network, Robotic Lawnmower, and more!, accessed February 8, 2026, <https://io.adafruit.com/blog/notebook/2023/09/08/iot-monthly/>
10. Add Sight to Your ESP32 - Edge Impulse, accessed February 8, 2026, <https://www.edgeimpulse.com/blog/add-sight-to-your-esp32/>
11. Suggestions for USB microphone systems · mcguirepr89 BirdNET-Pi · Discussion #39, accessed February 8, 2026, <https://github.com/mcguirepr89/BirdNET-Pi/discussions/39>
12. Recommended microphones for Birdnet-Pi : r/BirdNET_Analyzer - Reddit, accessed February 8, 2026, <https://www.reddit.com/r/BirdNET_Analyzer/comments/xg2ppp/recommended_microphones_for_birdnetpi/>
13. Building a GraphQL API with AWS AppSync Using Direct Lambda Resolvers in .NET, accessed February 8, 2026, <https://aws.amazon.com/blogs/dotnet/building-a-graphql-api-with-aws-appsync-using-direct-lambda-resolvers-in-net/>
