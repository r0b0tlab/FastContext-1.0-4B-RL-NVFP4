#!/usr/bin/env python3
"""Build deterministic per-second telemetry timeline for HyperFrames demo."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "benchmarks" / "hero_q1_deploy_vllm.json"
OUT_JSON = ROOT / "demos" / "hyperframes-comparison" / "assets" / "telemetry_timeline.json"
OUT_JS = ROOT / "demos" / "hyperframes-comparison" / "assets" / "telemetry_data.js"
DURATION_S = 88

# Composition timeline (seconds)
INTRO_END = 12
WITHOUT_END = 42
BRIDGE_END = 48
# When all WI_WORK_LINES are visible and API tokens have settled
FC_WORK_COMPLETE_AT = 82
PAYOFF_AT = 85

WO_WORK_LINES = [
    "solver: attach demos/sample-repo/README.md",
    "solver: attach docs/deployment.md",
    "solver: attach config/vllm/docker-compose.yml",
    "solver: attach config/vllm/.env.example",
    "solver: attach scripts/start-vllm.sh",
    "solver: attach docs/archive/note-000.md",
    "solver: attach docs/archive/note-015.md",
    "solver: attach docs/archive/note-032.md",
    "solver: attach src/services/svc_0.py",
    "solver: attach src/services/svc_12.py …",
    "solver: attach docs/archive/note-048.md …",
    "solver: context FULL — entire tree in API prompt",
    "solver: waiting on API completion…",
]

WI_WORK_LINES = [
    "vLLM :30000 — FastContext-1.0-4B-RL-NVFP4 ready",
    "FC turn 1 — Glob directory=demos/sample-repo pattern=config/**",
    "FC turn 1 — hit config/vllm/docker-compose.yml",
    "FC turn 2 — Read config/vllm/.env.example",
    "FC turn 2 — Read docs/deployment.md",
    "FC turn 3 — Grep pattern=VLLM_PORT path=.",
    "FC turn 3 — Read scripts/start-vllm.sh",
    "FC turn 4 — <final_answer> citations ready",
    "solver: inject 5 cited files only (not full tree)",
    "solver: API completion streaming…",
]


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * ease(t)


def phase_at(sec: int) -> str:
    if sec < INTRO_END:
        return "intro"
    if sec < WITHOUT_END:
        return "without"
    if sec < BRIDGE_END:
        return "bridge"
    return "with"


def main() -> None:
    m = json.loads(METRICS.read_text(encoding="utf-8"))
    wo = m["without_fastcontext"]["solver_total_tokens"]
    wi = m["with_fastcontext_nvfp4"]["solver_total_tokens"]
    fc_local = m["with_fastcontext_nvfp4"]["fc_local_tokens"]
    max_tools = m["with_fastcontext_nvfp4"]["fc_tool_calls"]
    d = m["derived"]

    frames = []
    for sec in range(DURATION_S + 1):
        phase = phase_at(sec)

        if phase == "intro":
            w_api = 0
            f_api = 0
            fc_loc = 0
            tools = 0
            wo_lines = 0
            wi_lines = 0
        elif phase == "without":
            p = (sec - INTRO_END) / (WITHOUT_END - INTRO_END)
            w_api = int(lerp(0, wo, p))
            f_api = 0
            fc_loc = 0
            tools = 0
            wo_lines = min(len(WO_WORK_LINES), 1 + int(p * (len(WO_WORK_LINES) - 1)))
            wi_lines = 0
        elif phase == "bridge":
            # WITHOUT column frozen at final token count
            w_api = wo
            f_api = 0
            p = (sec - WITHOUT_END) / (BRIDGE_END - WITHOUT_END)
            fc_loc = int(lerp(0, fc_local * 0.45, p))
            tools = int(lerp(0, 2, p))
            wo_lines = len(WO_WORK_LINES)
            wi_lines = min(len(WI_WORK_LINES), 1 + int(p * 4))
        else:
            w_api = wo  # frozen after WITHOUT completes
            work_span = max(1, FC_WORK_COMPLETE_AT - BRIDGE_END)
            work_p = min(1.0, (sec - BRIDGE_END) / work_span)
            wi_lines = min(
                len(WI_WORK_LINES),
                max(1, int(work_p * len(WI_WORK_LINES))),
            )
            # API solver tokens rise after exploration lines are mostly done
            token_start = BRIDGE_END + int(work_span * 0.65)
            if sec < token_start:
                f_api = 0
            else:
                token_p = min(
                    1.0,
                    (sec - token_start) / max(1, FC_WORK_COMPLETE_AT - token_start),
                )
                f_api = int(lerp(0, wi, token_p))
            fc_loc = int(lerp(fc_local * 0.45, fc_local, min(1.0, work_p * 1.15)))
            tools = int(lerp(2, max_tools, min(1.0, work_p * 1.05)))
            wo_lines = len(WO_WORK_LINES)

        gpu_util = 0 if phase == "intro" else (6 if phase == "without" else 12)
        if phase == "bridge":
            gpu_util = int(lerp(12, 48, (sec - WITHOUT_END) / (BRIDGE_END - WITHOUT_END)))
        if phase == "with":
            gpu_util = int(lerp(48, 72, min(1.0, (sec - BRIDGE_END) / 14)))

        decode = 0.0 if phase in ("intro", "without") else float(d["nvfp4_decode_tok_s"])
        if phase == "bridge":
            decode = d["nvfp4_decode_tok_s"] * ease((sec - WITHOUT_END) / (BRIDGE_END - WITHOUT_END)) * 0.5
        if phase == "with" and sec < BRIDGE_END + 8:
            decode = d["nvfp4_decode_tok_s"] * ease((sec - BRIDGE_END) / 8)

        power = 4.5 if phase == "intro" else (7.0 if phase == "without" else float(d["gpu_power_w_nvfp4"]))
        temp = 41 if phase in ("intro", "without") else int(lerp(41, 47, min(1.0, (sec - WITHOUT_END) / 25)))

        frames.append(
            {
                "t": sec,
                "phase": phase,
                "without_api_tokens": w_api,
                "with_api_tokens": f_api,
                "without_frozen": sec >= WITHOUT_END,
                "fc_local_tokens": fc_loc,
                "fc_tool_calls": tools,
                "wo_work_lines": WO_WORK_LINES[:wo_lines],
                "wi_work_lines": WI_WORK_LINES[:wi_lines],
                "gpu_util_pct": gpu_util,
                "gpu_power_w": round(power, 1),
                "gpu_temp_c": temp,
                "nvfp4_decode_tok_s": round(decode, 1),
                "bf16_decode_tok_s": d["bf16_decode_tok_s"],
                "model_size_gb": d["model_size_gb_nvfp4"],
                "api_reduction_pct": d["api_token_reduction_pct"] if sec >= PAYOFF_AT else 0,
                "fc_work_complete": wi_lines >= len(WI_WORK_LINES) and f_api >= int(wi * 0.98),
                "ttft_ms": 22 if phase == "with" and sec >= BRIDGE_END + 2 else 0,
            }
        )

    payload = {
        "duration_s": DURATION_S,
        "intro_end_s": INTRO_END,
        "without_end_s": WITHOUT_END,
        "fc_work_complete_at_s": FC_WORK_COMPLETE_AT,
        "payoff_at_s": PAYOFF_AT,
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