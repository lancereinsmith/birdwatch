/**
 * Amplify Gen 2 backend: auth, data, storage, IoT Lambda.
 * IoT Rule (birdnet/detections -> this Lambda) and Lambda->AppSync wiring
 * are set up via cloud/scripts/iot-setup.md or AWS Console.
 */
import { defineBackend } from "@aws-amplify/backend";
import { auth } from "./auth/resource";
import { data } from "./data/resource";
import { storage } from "./storage/resource";
import { iotHandler } from "./functions/iot-handler/resource";

defineBackend({
  auth,
  data,
  storage,
  iotHandler,
});
