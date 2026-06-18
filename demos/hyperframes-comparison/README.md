# HyperFrames — with vs without (professional render)

Side-by-side **WITHOUT** | **WITH FastContext NVFP4** | **Telemetry** column.

## Pipeline

```bash
# 1) Regenerate telemetry from benchmarks/hero_q1_deploy_vllm.json
python3 ../../scripts/generate_telemetry_timeline.py

# 2) Optional live GPU/vLLM samples (server on :30000)
python3 ../../scripts/capture_live_telemetry.py

# 3) Lint
npm run check

# 4) Render MP4 (HyperFrames 0.6.2)
npm run render
```

Output: `renders/hyperframes-comparison_*.mp4` → copy to `../../videos/fc-nvfp4-hyperframes-with-vs-without.mp4`

## Telemetry tracked (per second)

| Metric | Source |
|--------|--------|
| Without / with API solver tokens | `hero_q1_deploy_vllm.json` + timeline interpolation |
| FC local tokens, tool calls | Same |
| NVFP4 / BF16 decode tok/s | GB10 validation constants |
| TTFT, GPU util, power, temp | Timeline + optional `capture_live_telemetry.py` |
| API reduction % | Derived at payoff |

Assets: `assets/telemetry_timeline.json`, `assets/telemetry_data.js`