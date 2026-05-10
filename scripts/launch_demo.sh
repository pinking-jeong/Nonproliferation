#!/usr/bin/env bash
# Launch helper — runs FastAPI backend and Streamlit frontend together.
#
# Usage (from ospm/ directory):
#   bash scripts/launch_demo.sh
#
# Stops both with Ctrl+C.

set -euo pipefail
cd "$(dirname "$0")/.."

cleanup() {
  echo "[OS-PM] Stopping ..."
  kill "${BACKEND_PID:-}" 2>/dev/null || true
  kill "${FRONTEND_PID:-}" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[OS-PM] Starting FastAPI backend on :8000 ..."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "[OS-PM] Starting Streamlit on :8501 ..."
export OSPM_API="http://127.0.0.1:8000"
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo ""
echo "[OS-PM] Both services launched."
echo "  Backend  : http://127.0.0.1:8000  (docs: /docs)"
echo "  Frontend : http://127.0.0.1:8501"
echo ""
echo "Ctrl+C to stop."
wait
