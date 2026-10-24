#!/usr/bin/env bash
# Starts the MathQuest FastAPI backend server on Linux / macOS
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=========================================================="
echo "  MathQuest: Adaptive AI-Based Educational Toy Server   "
echo "=========================================================="

export PYTHONPATH="."
export DISABLE_SQLALCHEMY_C_EXTENSIONS="1"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    ./.venv/bin/pip install -r backend/requirements-dev.txt
fi

python3 scripts/ensure_pure_python.py

echo "Starting server on http://localhost:8000"
./.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
