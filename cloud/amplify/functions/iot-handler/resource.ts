/**
 * Lambda triggered by AWS IoT Core rule on topic birdnet/detections.
 * Parses MQTT payload and calls AppSync createDetection mutation.
 */
import { defineFunction } from "@aws-amplify/backend";

export const iotHandler = defineFunction({
  name: "iot-handler",
  entry: "./handler.ts",
  timeoutSeconds: 30,
  memoryMB: 256,
});
