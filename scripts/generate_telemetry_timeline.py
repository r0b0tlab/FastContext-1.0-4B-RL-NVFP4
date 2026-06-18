#!/usr/bin/env python3
"""Build deterministic per-second telemetry timeline for HyperFrames demo."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "benchmarks" / "hero_q1_deploy_vllm.json"
OUT_JSON = ROOT / "demos" / "hyperframes-comparison" / "assets" / "telemetry_timeline.json"
OUT_JS = ROOT / "demos" / "hyperframes-comparison" / "assets" / "telemetry_data.js"
DURATION_S = 88


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * ease(t)


def main() -> None:
    m = json.loads(METRICS.read_text(encoding="utf-8"))
    wo = m["without_fastcontext"]["solver_total_tokens"]
    wi = m["with_fastcontext_nvfp4"]["solver_total_tokens"]
    fc_local = m["with_fastcontext_nvfp4"]["fc_local_tokens"]
    d = m["derived"]

    frames = []
    for sec in range(DURATION_S + 1):
        # Phases (seconds)
        if sec < 8:
            phase = "intro"
            w_api = 0
            f_api = 0
            fc_loc = 0
            tools = 0
        elif sec < 38:
            phase = "without"
            p = (sec - 8) / 30
            w_api = int(lerp(0, wo, p))
            f_api = 0
            fc_loc = 0
            tools = 0
        elif sec < 44:
            phase = "bridge"
            w_api = wo
            f_api = int(lerp(wo, wo * 0.4, (sec - 38) / 6))
            fc_loc = int(lerp(0, fc_local * 0.3, (sec - 38) / 6))
            tools = int(lerp(0, 2, (sec - 38) / 6))
        else:
            phase = "with"
            p = min(1.0, (sec - 44) / 28)
            w_api = int(lerp(wo * 0.35, wi, p))
            f_api = wi if p > 0.85 else int(lerp(wo * 0.35, wi, p))
            fc_loc = int(lerp(fc_local * 0.3, fc_local, p))
            tools = int(lerp(2, m["with_fastcontext_nvfp4"]["fc_tool_calls"], p))

        gpu_util = 0 if phase == "intro" else (8 if phase == "without" else 62)
        if phase == "with":
            gpu_util = int(lerp(18, 72, min(1.0, (sec - 44) / 12)))

        decode = 0 if phase in ("intro", "without") else d["nvfp4_decode_tok_s"]
        if phase == "with" and sec < 50:
            decode = d["nvfp4_decode_tok_s"] * ease((sec - 44) / 6)

        power = 4.5 if phase == "intro" else (7 if phase == "without" else d["gpu_power_w_nvfp4"])
        temp = 41 if phase != "with" else int(lerp(41, 47, min(1.0, (sec - 44) / 20)))

        frames.append(
            {
                "t": sec,
                "phase": phase,
                "without_api_tokens": w_api,
                "with_api_tokens": f_api,
                "fc_local_tokens": fc_loc,
                "fc_tool_calls": tools,
                "gpu_util_pct": gpu_util,
                "gpu_power_w": round(power, 1),
                "gpu_temp_c": temp,
                "nvfp4_decode_tok_s": round(decode, 1),
                "bf16_decode_tok_s": d["bf16_decode_tok_s"],
                "model_size_gb": d["model_size_gb_nvfp4"],
                "api_reduction_pct": d["api_token_reduction_pct"] if sec >= 70 else 0,
                "ttft_ms": 22 if phase == "with" and sec >= 46 else 0,
            }
        )

    payload = {
        "duration_s": DURATION_S,
        "source_metrics": str(METRICS.relative_to(ROOT)),
        "question": m["question"],
        "without_total": wo,
        "with_total": wi,
        "frames": frames,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_JS.write_text(
        "window.TELEMETRY_DATA = " + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JSON} ({len(frames)} frames)")


if __name__ == "__main__":
    main()