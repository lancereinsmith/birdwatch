/**
 * IoT Rule invokes this Lambda with MQTT payload from birdnet/detections.
 * Forwards to AppSync createDetection (implementation uses AppSync HTTP or SDK).
 */
export type HandlerEvent = {
  deviceId: string;
  speciesCode: string;
  scientificName?: string;
  commonName?: string;
  confidence: number;
  timestamp: string;
  location?: { lat?: number; lon?: number };
  audioUrl?: string;
  imageUrl?: string;
};

export const handler = async (event: { [key: string]: unknown }): Promise<{ statusCode: number; body?: string }> => {
  // IoT Core rule sends the MQTT message payload as the Lambda event
  const payload = event as unknown as HandlerEvent;
  if (!payload.deviceId || !payload.speciesCode || !payload.timestamp || payload.confidence == null) {
    return { statusCode: 400, body: "Missing required fields" };
  }
  // TODO: call AppSync createDetection via HTTP (signed) or SDK
  // const endpoint = process.env.APPSYNC_ENDPOINT;
  // await postMutation(endpoint, "createDetection", { input: { ...payload } });
  console.log("Detection received:", payload);
  return { statusCode: 200 };
};
