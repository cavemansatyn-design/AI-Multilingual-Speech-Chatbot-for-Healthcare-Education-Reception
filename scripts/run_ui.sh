#!/usr/bin/env bash
# Run Streamlit UI. Ensure FastAPI backend is running first (./scripts/run_server.sh)
set -e
cd "$(dirname "$0")/.."

if [ -d "../venv" ]; then
  source ../venv/bin/activate
elif [ -d "venv" ]; then
  source venv/bin/activate
fi

echo "Starting Streamlit UI at http://localhost:8501"
echo "Ensure FastAPI backend is running: uvicorn app.main:app --host 0.0.0.0 --port 8000"
exec streamlit run ui_app.py
