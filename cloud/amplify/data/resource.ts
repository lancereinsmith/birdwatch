/**
 * Amplify Data: Detection model for bird detections (Pi and app).
 */
import { type ClientSchema, a, defineData } from "@aws-amplify/backend";

const schema = a.schema({
  Detection: a
    .model({
      deviceId: a.string().required(),
      speciesCode: a.string().required(),
      scientificName: a.string(),
      commonName: a.string(),
      confidence: a.float().required(),
      timestamp: a.datetime().required(),
      location: a.customType({
        lat: a.float(),
        lon: a.float(),
      }),
      audioUrl: a.string(),
      imageUrl: a.string(),
    })
    .authorization((allow) => [
      allow.publicApiKey(),
      allow.owner(),
      allow.authenticated(),
    ]),
});

export type Schema = ClientSchema<typeof schema>;
export const data = defineData({ schema });
