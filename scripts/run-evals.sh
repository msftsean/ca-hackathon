#!/usr/bin/env bash
# Run evals for any accelerator by ID, or all
# Usage: ./scripts/run-evals.sh 001
#        ./scripts/run-evals.sh all
set -euo pipefail

ACCEL_ID="${1:?Usage: $0 <accelerator-id|all>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

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

run_evals() {
  local id=$1
  local dir="${ACCEL_MAP[$id]:-}"
  if [ -z "$dir" ]; then
    echo "❌ Unknown accelerator ID: $id"
    return 1
  fi
  
  local eval_dir="$REPO_ROOT/accelerators/$dir/backend/evals"
  if [ ! -d "$eval_dir" ]; then
    echo "⏭️  $dir — no evals directory, skipping"
    return 0
  fi
  
  echo "🧪 Running evals for $dir..."
  cd "$REPO_ROOT/accelerators/$dir/backend"
  USE_MOCK_SERVICES=true python -m pytest evals/ -v --tb=short 2>&1
  echo ""
}

run_tests() {
  local id=$1
  local dir="${ACCEL_MAP[$id]:-}"
  
  echo "🧪 Running tests for $dir..."
  cd "$REPO_ROOT/accelerators/$dir/backend"
  USE_MOCK_SERVICES=true python -m pytest tests/ -v --tb=short 2>&1
  echo ""
}

if [ "$ACCEL_ID" = "all" ]; then
  PASSED=0
  FAILED=0
  for id in 001 002 003 004 005 006 007 008; do
    if run_tests "$id" && run_evals "$id"; then
      PASSED=$((PASSED + 1))
    else
      FAILED=$((FAILED + 1))
    fi
  done
  echo "━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 Results: $PASSED passed, $FAILED failed (of 8 accelerators)"
else
  run_tests "$ACCEL_ID"
  run_evals "$ACCEL_ID"
fi
