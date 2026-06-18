# With vs without FastContext — demo video

**Thesis:** Same vLLM deploy question on the **bundled** `demos/sample-repo/` — API context stuffing vs local NVFP4 exploration + citations.

## Hero hook

> How do I deploy and configure the vLLM model server for this project?

Metrics: `benchmarks/hero_q1_deploy_vllm.json` (from `benchmarks/measure_sample_repo.py`).

## Render

```bash
python3 benchmarks/measure_sample_repo.py
python3 scripts/render_comparison_video.py \
  --metrics ../../benchmarks/hero_q1_deploy_vllm.json \
  --output ../../videos/fc-nvfp4-q1-deploy-vllm.mp4
```

## Live take (optional)

1. `../../configs/vllm-serve.sh` on port `30000`
2. Point FastContext / OpenAI client at `demos/sample-repo` as working directory
3. Re-run measurement or record exploration, then refresh JSON

**Do not** use hermes-concurrent-agents for this demo — this project ships its own fixture.