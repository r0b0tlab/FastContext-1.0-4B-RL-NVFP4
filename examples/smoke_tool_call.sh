#!/usr/bin/env bash
# Minimal smoke: health + models list. Requires vLLM on :30000
set -euo pipefail
BASE="${BASE_URL:-http://127.0.0.1:30000}"
curl -sf "${BASE}/health" && echo "health ok"
curl -sf "${BASE}/v1/models" | python3 -m json.tool | head -30