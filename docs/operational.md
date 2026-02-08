# Operational notes

## eBird API key and usage

The app can use the **eBird API 2.0** for spatial validation (e.g. flag
detections that are unlikely in the user’s region).

- **Sign up:** Request an API key at [eBird API](https://ebird.org/api/keygen).
- **Usage:** Send the key in the header `X-eBirdApiToken` on requests to
  `https://api.ebird.org/v2`.
- **Relevant endpoint:** “Recent observations in a region” —
  `GET /v2/data/obs/{regionCode}/recent` — returns recent species for that
  region (e.g. US county). Use it to check if a detected species appears
  in the list; if not, show “Unlikely in this region” or similar.
- **Storage:** Do not hardcode the key. Use environment variables, a
  secure config, or a backend proxy that holds the key.

## Privacy and legal (recording)

Recording audio in public or semi-public spaces can implicate wiretapping
and privacy laws, which vary by jurisdiction.

- **Embedded node:** The system is intended to **analyze** audio and
  **discard** the raw stream after inference. Do not record or store
  continuous 24/7 audio. Store only short clips of *detected* bird sounds
  if you enable that feature, and document it clearly.
- **Mobile app:** Same principle: process chunks for identification;
  avoid retaining raw continuous recording unless the user opts in and
  is informed.
- **Disclosure:** In the app and in any deployment (e.g. Pi in a shared
  space), state that the device listens for bird sounds and does not
  record or store continuous audio, or state exactly what is stored and
  for how long.

Consult local laws and, if needed, legal advice before deploying
microphones in public or others’ property.
