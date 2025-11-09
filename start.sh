#!/usr/bin/env bash
set -euo pipefail

trap 'kill 0' EXIT

rasa run \
  --enable-api \
  --cors "*" \
  --model rasa_project/models \
  --port 5005 \
  --debug \
  &

rasa run actions \
  --actions rasa_project.actions.actions \
  --port 5055 \
  &

uvicorn main:app \
  --host 0.0.0.0 \
  --port 8080 \
  --proxy-headers