#!/usr/bin/env bash
# Deploy Amplify backend to a sandbox (development).
# Run from repo root: ./cloud/scripts/deploy-sandbox.sh
# Or from cloud/: ./scripts/deploy-sandbox.sh
set -e
cd "$(dirname "$0")/.."
npm install
npx ampx sandbox --no-browser
