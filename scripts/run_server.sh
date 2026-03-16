#!/usr/bin/env bash
# Run the FastAPI server. Activate venv first or use: ./scripts/run_server.sh
# Run from project root.

set -e
cd "$(dirname "$0")/.."

if [ -d "venv" ]; then
  source venv/bin/activate
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
echo "Starting server at http://${HOST}:${PORT}"
exec uvicorn app.main:app --host "$HOST" --port "$PORT"
