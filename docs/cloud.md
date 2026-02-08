# Cloud backend (AWS Amplify Gen 2)

The Birdwatch backend lives under **`cloud/`**. It provides authentication,
a Detection data model with real-time sync, file storage for audio clips,
and an IoT path so the Raspberry Pi can publish detections that appear in
the app.

## Overview

| Component | Role |
|-----------|------|
| **Auth** | Cognito: email sign-in for app users; IAM for Lambda (IoT bridge). |
| **Data** | Amplify Data (GraphQL): Detection model stored in DynamoDB, real-time via AppSync. |
| **Storage** | S3 bucket (e.g. birdnetAudioClips) for short audio clips; access rules for auth/guest. |
| **IoT Lambda** | Function triggered by an IoT Rule on topic `birdnet/detections`; parses payload and can write to AppSync. |

## Project structure

```text
cloud/
├── package.json          # ampx scripts (sandbox, deploy)
├── amplify/
│   ├── backend.ts        # defineBackend(auth, data, storage, iotHandler)
│   ├── auth/resource.ts  # defineAuth (email login)
│   ├── data/resource.ts  # Detection schema
│   ├── storage/resource.ts
│   └── functions/
│       └── iot-handler/  # Lambda: handler.ts, resource.ts
└── scripts/
    └── iot-setup.md      # Step-by-step IoT Thing, policy, rule
```

## Detection schema

The Amplify Data model matches what the Pi and app use:

- **deviceId** (string, required) — e.g. `pi-01`.
- **speciesCode** (string, required) — e.g. 4-letter code or derived from
  scientific name.
- **scientificName**, **commonName** (string, optional).
- **confidence** (float, required) — model score (e.g. 0.0–1.0).
- **timestamp** (datetime, required) — ISO8601.
- **location** (custom type, optional) — `lat`, `lon` (float).
- **audioUrl**, **imageUrl** (string, optional) — S3 or CDN URLs.

Authorization: public API key, owner, and authenticated access as defined
in `data/resource.ts`.

## Deploying the backend

Prerequisites: Node ≥18, AWS CLI configured (or Amplify/SSO).

From the repo root:

```bash
cd cloud
npm install
npx ampx sandbox
```

Or run the helper script from repo root:
`./cloud/scripts/deploy-sandbox.sh`

This deploys (or updates) the sandbox. After the first run, use
`amplify_outputs.json` or `ampx generate outputs` to get the GraphQL
endpoint and other config for the Flutter app and for the Lambda (e.g.
`APPSYNC_ENDPOINT`).

For production, use Amplify’s CI/CD (e.g. connect the repo and deploy from
a branch); see Amplify Gen 2 docs.

## IoT setup for the Pi

So that the Pi can publish to AWS IoT and a Lambda runs on each message:

1. **Create an IoT Thing** (e.g. `birdnet-pi-01`) in AWS IoT Core → Manage
   → Things.
2. **Create a certificate** for the thing; download certificate, private key,
   and (if needed) Amazon Root CA 1. Attach the certificate to the thing.
3. **Create an IoT policy** and attach it to the certificate. The policy
   must allow:
   - `iot:Publish` on resource
     `arn:aws:iot:REGION:ACCOUNT:topic/birdnet/detections`
   - `iot:Connect` on resource
     `arn:aws:iot:REGION:ACCOUNT:client/birdnet-pi-01` (or your client id).
4. **Create an IoT Rule** that selects messages from `birdnet/detections`
   and invokes the Lambda. Rule query: `SELECT * FROM 'birdnet/detections'`.
   Action: send to Lambda → choose the deployed `iot-handler` (or same
   function name from your backend).
5. **Lambda permissions:** Ensure the Lambda execution role can invoke
   (and that the rule has permission to call the Lambda). To have the
   Lambda write to AppSync, grant the role `appsync:GraphQL` on the API
   and set the Lambda env var `APPSYNC_ENDPOINT` to the Amplify Data
   GraphQL URL.

Step-by-step with example policy JSON is in **`cloud/scripts/iot-setup.md`**.

## Lambda handler (iot-handler)

The Lambda receives the MQTT message payload (JSON) as the event. Expected
fields include `deviceId`, `speciesCode`, `confidence`, `timestamp`; optional
`location`, `audioUrl`, etc.

Current implementation validates the payload and logs it. To complete the
flow:

- Use the AppSync endpoint from env and IAM (or signing) to call the
  Amplify Data API (e.g. `createDetection` mutation) with the payload
  fields.

## Storage (S3)

The storage resource defines a bucket (e.g. birdnetAudioClips) and access
rules for paths like `audio/*`. The app or Pi can upload short clips and
store the URL in `Detection.audioUrl` for playback in the app.
