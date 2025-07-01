#!/usr/bin/env bash
set -e

pkill -f "uvicorn app.main:app" || true

echo "Starting server..."
uvicorn app.main:app --reload > moderation.log 2>&1 &
UVICORN_PID=$!
echo "→ Server PID is $UVICORN_PID"

echo -n "Waiting for server to be healthy"
for i in {1..20}; do
  if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/healthz | grep -q "200"; then
    echo " ✓"
    break
  fi
  echo -n "."
  sleep 0.5
done

if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/healthz | grep -q "200"; then
  echo "ERROR: server never became healthy"
  kill "$UVICORN_PID" 2>/dev/null || true
  exit 1
fi

echo "Sending 20 test requests..."
declare -a CURL_PIDS=()
for i in $(seq 1 20); do
  curl -s -X POST http://127.0.0.1:8000/moderate \
       -H "Content-Type: application/json" \
       -d '{"text":"test"}' > /dev/null &
  CURL_PIDS+=("$!")
done

for pid in "${CURL_PIDS[@]}"; do
  wait "$pid"
done

echo "Stopping server..."
kill "$UVICORN_PID" 2>/dev/null || true

echo "Computing requests-per-second:"
python scripts/compute_rps.py moderation.log