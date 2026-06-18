# Shot list — q1 vLLM deploy (75–90s)

**Fixture:** `demos/sample-repo` (this repo only)

| Scene | t (s) | On-screen text |
|-------|------:|----------------|
| Cold open | 0–3 | **Same question. Two ways.** |
| Question | 3–10 | Hero question + chip `sample-repo` |
| Without | 10–32 | **API only** · tokens from JSON `without_fastcontext` |
| Transition | 32–36 | **Local FastContext NVFP4 on GB10** |
| With FC | 36–58 | Read/Glob/Grep · API tokens from JSON `with_fastcontext_nvfp4` |
| Payoff | 65–78 | **−{api_token_reduction_pct}% API tokens** (from JSON) |
| CTA | 78–90 | HF + github.com/r0b0tlab/FastContext-1.0-4B-RL-NVFP4 |