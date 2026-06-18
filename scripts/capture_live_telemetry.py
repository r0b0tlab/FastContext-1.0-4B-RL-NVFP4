#!/usr/bin/env python3
"""Optional: sample live GPU + vLLM /metrics into telemetry_capture.json."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "telemetry_capture.json"
VLLM = "http://127.0.0.1:30000/metrics"
INTERVAL = 1.0
SAMPLES = 30


def nvidia_smi() -> dict:
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,power.draw,temperature.gpu,memory.used",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        ).strip()
        util, power, temp, mem = [x.strip() for x in out.split(",")]
        return {
            "gpu_util_pct": float(util),
            "gpu_power_w": float(power),
            "gpu_temp_c": float(temp),
            "gpu_mem_mib": float(mem),
        }
    except Exception as e:
        return {"error": str(e)}


def vllm_metrics() -> dict:
    try:
        raw = urllib.request.urlopen(VLLM, timeout=3).read().decode("utf-8", errors="replace")
        gen = prompt = 0.0
        for line in raw.splitlines():
            if line.startswith("vllm:generation_tokens_total"):
                gen = float(line.split()[-1])
            if line.startswith("vllm:prompt_tokens_total"):
                prompt = float(line.split()[-1])
        return {"vllm_prompt_tokens_total": prompt, "vllm_generation_tokens_total": gen}
    except Exception as e:
        return {"error": str(e)}


def main() -> None:
    rows = []
    t0 = time.time()
    for i in range(SAMPLES):
        rows.append(
            {
                "t_offset_s": round(time.time() - t0, 2),
                "nvidia_smi": nvidia_smi(),
                "vllm": vllm_metrics(),
            }
        )
        time.sleep(INTERVAL)
    OUT.write_text(json.dumps({"samples": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} samples)")


if __name__ == "__main__":
    main()