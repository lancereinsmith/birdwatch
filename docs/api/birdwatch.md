# birdwatch

Python package for the Raspberry Pi pipeline: record audio, run BirdNET
inference, publish detections to AWS IoT.

## Modules

::: birdwatch.recorder
    options:
      show_root_heading: true
      members: [RingBuffer, run_recorder, BUFFER_SAMPLES]

::: birdwatch.analyzer
    options:
      show_root_heading: true
      members: [preprocess_audio, BirdNETAnalyzer]

::: birdwatch.mqtt_client
    options:
      show_root_heading: true
      members: [DetectionPayload, MQTTClient]

::: birdwatch.pi.main
    options:
      show_root_heading: true
      members: [main_pi]
