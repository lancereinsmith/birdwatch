/**
 * S3 bucket for short bird audio clips (e.g. from Pi).
 */
import { defineStorage } from "@aws-amplify/backend";

export const storage = defineStorage({
  name: "birdnetAudioClips",
  access: (allow) => ({
    "audio/*": [
      allow.authenticated.to("read", "write"),
      allow.guest.to("read", "write"),
    ],
  }),
});
