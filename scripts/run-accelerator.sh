#!/usr/bin/env bash
# Run any accelerator by ID (001-008)
# Usage: ./scripts/run-accelerator.sh 001
set -euo pipefail

ACCEL_ID="${1:?Usage: $0 <accelerator-id> (e.g., 001)}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Map ID to directory name
declare -A ACCEL_MAP
ACCEL_MAP=(
  [001]="001-benefitscal-navigator"
  [002]="002-wildfire-response-coordinator"
  [003]="003-medi-cal-eligibility"
  [004]="004-permit-streamliner"
  [005]="005-genai-procurement-compliance"
  [006]="006-cross-agency-knowledge-hub"
  [007]="007-edd-claims-assistant"
  [008]="008-multilingual-emergency-chat"
)

ACCEL_DIR="${ACCEL_MAP[$ACCEL_ID]:-}"
if [ -z "$ACCEL_DIR" ]; then
  echo "❌ Unknown accelerator ID: $ACCEL_ID"
  echo "Valid IDs: 001, 002, 003, 004, 005, 006, 007, 008"
  exit 1
fi

BACKEND_DIR="$REPO_ROOT/accelerators/$ACCEL_DIR/backend"
FRONTEND_DIR="$REPO_ROOT/accelerators/$ACCEL_DIR/frontend"

echo "🚀 Starting $ACCEL_DIR..."
echo "   Backend: http://localhost:8000"

# Set mock mode
export USE_MOCK_SERVICES=true

# Start backend
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend if it exists (005 has no frontend)
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
  echo "   Frontend: http://localhost:5173"
  cd "$FRONTEND_DIR"
  npm install --silent 2>/dev/null
  npm run dev &
  FRONTEND_PID=$!
fi

echo ""
echo "✅ $ACCEL_DIR is running!"
echo "   Press Ctrl+C to stop"

# Cleanup on exit
cleanup() {
  kill $BACKEND_PID 2>/dev/null || true
  [ -n "${FRONTEND_PID:-}" ] && kill $FRONTEND_PID 2>/dev/null || true
}
trap cleanup EXIT

wait
