/**
 * Amplify Auth: email sign-in for app users; IAM for Lambda (IoT bridge).
 */
import { defineAuth } from "@aws-amplify/backend";

export const auth = defineAuth({
  loginWith: {
    email: {
      verificationEmailStyle: "CODE",
      verificationEmailSubject: "Birdwatch verification",
      verificationEmailBody: (createCode) =>
        `Your Birdwatch code is ${createCode()}. It expires in 15 minutes.`,
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: true,
      },
    },
  },
});
