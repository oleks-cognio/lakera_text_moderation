set -e

echo "Starting server..."
uvicorn app.main:app --reload > moderation.log 2>&1 &
UVICORN_PID=$!

sleep 2

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
kill "$UVICORN_PID"

echo "Computing requests-per-second:"
python scripts/compute_rps.py moderation.log