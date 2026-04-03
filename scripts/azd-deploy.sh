#!/bin/bash
# Deploy CA Hackathon accelerators to Azure Container Apps
# Usage: ./scripts/azd-deploy.sh all        — Deploy everything
# Usage: ./scripts/azd-deploy.sh 001        — Deploy accelerator 001 only
# Usage: ./scripts/azd-deploy.sh platform   — Deploy core platform only

set -e

ACCEL_ID="${1:-}"

if [ -z "$ACCEL_ID" ]; then
  echo "CA Hackathon Accelerator Deployment"
  echo "===================================="
  echo ""
  echo "Usage: $0 <target>"
  echo ""
  echo "Targets:"
  echo "  all        Deploy everything (platform + all accelerators)"
  echo "  platform   Deploy core platform (backend + frontend) only"
  echo "  001-008    Deploy a specific accelerator"
  echo ""
  echo "Examples:"
  echo "  $0 all"
  echo "  $0 001"
  echo "  $0 platform"
  exit 1
fi

case "$ACCEL_ID" in
  all)
    echo "🚀 Deploying full CA Hackathon platform + all accelerators..."
    azd up
    ;;
  platform)
    echo "🚀 Deploying core platform..."
    azd deploy backend
    azd deploy frontend
    ;;
  00[1-8])
    echo "🚀 Deploying accelerator ${ACCEL_ID}..."
    azd deploy "accel-${ACCEL_ID}"
    # Deploy frontend if it exists (all except 005)
    if [ "$ACCEL_ID" != "005" ]; then
      azd deploy "accel-${ACCEL_ID}-fe"
    fi
    ;;
  *)
    echo "❌ Unknown target: ${ACCEL_ID}"
    echo "Valid targets: all, platform, 001-008"
    exit 1
    ;;
esac

echo ""
echo "✅ Deployment complete!"
