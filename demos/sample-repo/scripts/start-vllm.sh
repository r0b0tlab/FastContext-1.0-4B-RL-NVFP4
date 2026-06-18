#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/config/vllm/.env" 2>/dev/null || true

MODEL_ID="${MODEL_ID:-r0b0tlab/FastContext-1.0-4B-RL-NVFP4}"
PORT="${VLLM_PORT:-8000}"

exec vllm serve "$MODEL_ID" \
  --quantization modelopt \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port "$PORT" \
  --served-model-name "${SERVED_MODEL_NAME:-FastContext-1.0-4B-RL-NVFP4}"