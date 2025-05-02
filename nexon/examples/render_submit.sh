#!/usr/bin/env bash
set -euo pipefail

# Example: render_submit.sh
# Usage: ./render_submit.sh <env_name> <scene_file> [priority] [comment]

ENV_NAME="${1:-vp_render}"
SCENE_FILE="${2:-/path/to/scene.mb}"
PRIORITY="${3:-80}"
COMMENT="${4:-"Automated submit"}"

echo "🔧 Creating environment '${ENV_NAME}' with role=artist"
nexon create-env "${ENV_NAME}" --role artist

echo "📦 Installing required packages"
nexon install-package "${ENV_NAME}" "houdini>=19.0" --dry-run
nexon install-package "${ENV_NAME}" "houdini>=19.0"

echo "🐳 Building Docker image for render"
nexon build-docker "${ENV_NAME}" --tag "nexon/${ENV_NAME}:render"

echo "🚀 Submitting to Deadline"
nexon render-submit "${ENV_NAME}" "${SCENE_FILE}" \
  --farm deadline \
  --options "-Priority ${PRIORITY} -Comment \"${COMMENT}\""

echo "✅ Render job submitted."
