# FastContext-1.0-4B-RL-NVFP4

NVFP4 (W4A4) weights for [microsoft/FastContext-1.0-4B-RL](https://huggingface.co/microsoft/FastContext-1.0-4B-RL) — the repository-exploration subagent for coding agents.

This repository is **standalone**: model card, serving configs, a **bundled demo codebase**, and a with-vs-without comparison video. It is **not** the [hermes-concurrent-agents](https://github.com/r0b0tlab/hermes-concurrent-agents) project.

| | |
|---|---|
| **HF weights** | [huggingface.co/r0b0tlab/FastContext-1.0-4B-RL-NVFP4](https://huggingface.co/r0b0tlab/FastContext-1.0-4B-RL-NVFP4) |
| **Base model** | [microsoft/FastContext-1.0-4B-RL](https://huggingface.co/microsoft/FastContext-1.0-4B-RL) |
| **Paper** | [arXiv:2606.14066](https://arxiv.org/abs/2606.14066) |

## Why this repo exists

- **Hugging Face** hosts the quantized checkpoint.
- **This GitHub repo** hosts serve scripts, a self-contained **demo fixture** (`demos/sample-repo/`), measured token comparison JSON, and video tooling.

## Hero demo (hook q1)

**Question:** *How do I deploy and configure the vLLM model server for this project?*

**Fixture:** `demos/sample-repo/` only (no external monorepo required).

| Path | API solver tokens (measured) |
|------|-----------------------------:|
| **Without FastContext** — stuff entire fixture into API context | see JSON |
| **With FastContext NVFP4** — explore locally, cite files, then API solver | see JSON |

Regenerate after editing the fixture:

```bash
python3 benchmarks/measure_sample_repo.py
```

NVFP4 on GB10 (checkpoint serve): **66.3 tok/s** decode vs **22.8** BF16 (**2.9×**), **2.7 GB** weights, **~11 W** — from GB10 validation runs on this checkpoint.

## Serve the model

```bash
chmod +x configs/vllm-serve.sh
./configs/vllm-serve.sh
```

Environment: `FC_NVFP4_MODEL`, `FC_NVFP4_PORT` (defaults in script).

## Demo video

**Recommended (HyperFrames):** side-by-side + live telemetry column

```bash
cd demos/hyperframes-comparison
npm run check && npm run render
cp renders/hyperframes-comparison_*.mp4 ../../videos/fc-nvfp4-hyperframes-with-vs-without.mp4
```

**Quick draft (Pillow/ffmpeg):**

```bash
python3 demos/with-vs-without-video/scripts/render_comparison_video.py \
  --metrics benchmarks/hero_q1_deploy_vllm.json \
  --output videos/fc-nvfp4-q1-deploy-vllm.mp4
```

## Quantization

NVIDIA ModelOpt 0.44.0, `NVFP4_DEFAULT_CFG`, `quant_method: modelopt_fp4` in `hf_quant_config.json`.

Credits: Microsoft (FastContext), Qwen (base), NVIDIA (ModelOpt). Quantization © 2026 r0b0tlab; MIT.