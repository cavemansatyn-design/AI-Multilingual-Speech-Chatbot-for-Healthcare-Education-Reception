#!/usr/bin/env bash
# Setup script: create virtual environment and install dependencies.
# Run from project root: ./scripts/setup_env.sh

set -e
cd "$(dirname "$0")/.."

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
# shellcheck source=/dev/null
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Copying .env.example to .env (if .env does not exist)..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit .env and set SECRET_KEY, MONGODB_URI, etc."
else
  echo ".env already exists; skipping."
fi

echo "Setup complete. Activate with: source venv/bin/activate"
