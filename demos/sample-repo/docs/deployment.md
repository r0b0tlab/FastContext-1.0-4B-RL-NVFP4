# Deployment

## Docker (recommended)

1. Copy `config/vllm/.env.example` to `config/vllm/.env`.
2. Set `MODEL_ID` and `SERVED_MODEL_NAME`.
3. Run `docker compose -f config/vllm/docker-compose.yml up -d`.
4. Verify: `curl http://127.0.0.1:${VLLM_PORT:-8000}/health`.

## Bare metal

Use `scripts/start-vllm.sh` when vLLM is installed on the host.  
Supports NVFP4 via `--quantization modelopt` when weights are ModelOpt FP4.

## Client

Point OpenAI-compatible clients at `http://127.0.0.1:8000/v1` with `enable-auto-tool-choice` for explorer tool loops.