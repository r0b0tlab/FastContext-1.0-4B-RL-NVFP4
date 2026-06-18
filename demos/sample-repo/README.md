# Sample service (demo fixture)

Minimal codebase used **only** for the with-vs-without FastContext demo in this repo.  
Not related to [hermes-concurrent-agents](https://github.com/r0b0tlab/hermes-concurrent-agents) or any other r0b0tlab project.

## vLLM backend

Production inference is expected via the compose stack under `config/vllm/`.

Required environment variables:

| Variable | Purpose |
|----------|---------|
| `MODEL_ID` | Hugging Face model id or local path |
| `SERVED_MODEL_NAME` | Name exposed in `/v1/models` |
| `VLLM_PORT` | Host port (default `8000`) |

Optional: `GPU_MEMORY_UTILIZATION`, `MAX_MODEL_LEN`, `MAX_NUM_SEQS`.

## Quick start

```bash
cp config/vllm/.env.example config/vllm/.env
# edit MODEL_ID and SERVED_MODEL_NAME
docker compose -f config/vllm/docker-compose.yml up -d
curl -s http://127.0.0.1:8000/v1/models | jq .
```

See `docs/deployment.md` for health checks and `scripts/start-vllm.sh` for bare-metal vLLM.