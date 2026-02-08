# AWS IoT setup for Birdwatch Pi

After deploying the Amplify backend (`npx ampx sandbox`), set up IoT Core so the Pi can publish to `birdnet/detections` and a Lambda is triggered.

1. **Create an IoT Thing** (e.g. `birdnet-pi-01`)
   - AWS Console → IoT Core → Manage → Things → Create thing.
   - Use a single thing or fleet; note the thing name for `AWS_IOT_CLIENT_ID`.

2. **Create and attach a certificate**
   - Create certificate (one-click); attach policy; activate.
   - Download certificate, private key, and root CA (Amazon Root CA 1).
   - Store on the Pi and set:
     - `AWS_IOT_ENDPOINT` (e.g. `xxxxxxxxxxxxx-ats.iot.region.amazonaws.com`)
     - `AWS_IOT_CLIENT_ID` (thing name)
     - `AWS_IOT_CERT_PATH`, `AWS_IOT_KEY_PATH`, `AWS_IOT_CA_PATH`

3. **Create an IoT Policy** (for the certificate)
   - Allow: `iot:Publish` on topic `birdnet/detections`.
   - Allow: `iot:Connect` with client ID matching the thing.

   Example policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "iot:Publish",
         "Resource": "arn:aws:iot:REGION:ACCOUNT:topic/birdnet/detections"
       },
       {
         "Effect": "Allow",
         "Action": "iot:Connect",
         "Resource": "arn:aws:iot:REGION:ACCOUNT:client/birdnet-pi-01"
       }
     ]
   }
   ```

4. **Create an IoT Rule** to invoke the Lambda
   - Rule query: `SELECT * FROM 'birdnet/detections'`
   - Action: Send a message to a Lambda function → choose `iot-handler` (or the deployed function name).
   - Ensure the Lambda execution role has permission for `iot:CreateTopicRule` if needed; the rule needs to be able to invoke the Lambda.

5. **Lambda → AppSync**
   - Grant the Lambda role permission to call AppSync (e.g. `appsync:GraphQL` on the API).
   - Set the Lambda env var `APPSYNC_ENDPOINT` to the Amplify Data GraphQL endpoint (from Amplify outputs or `ampx generate outputs`).
   - Implement the HTTP signed request in `handler.ts` to run the `createDetection` mutation.
