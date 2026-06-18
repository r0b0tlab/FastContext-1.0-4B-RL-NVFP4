# X thread — FastContext NVFP4 (standalone repo)

## Tweet 1 (video)

Same vLLM deploy question. Two ways.

Stuff the whole demo repo into your API: **{without_tokens}** tokens.

**FastContext 1.0 4B NVFP4** on GB10 explores first → **{with_tokens}** API tokens.

Weights: https://huggingface.co/r0b0tlab/FastContext-1.0-4B-RL-NVFP4  
Repo: https://github.com/r0b0tlab/FastContext-1.0-4B-RL-NVFP4

## Tweet 2

Self-contained demo fixture in-repo (`demos/sample-repo`).  
Serve: `./configs/vllm-serve.sh` · vLLM 0.23+ `modelopt` + `hermes` tool parser.

## Tweet 3

Reproduce metrics:

```bash
python3 benchmarks/measure_sample_repo.py
```

Paper: arXiv:2606.14066 · Base: microsoft/FastContext-1.0-4B-RL