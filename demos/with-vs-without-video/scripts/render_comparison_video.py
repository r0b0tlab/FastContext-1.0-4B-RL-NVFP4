#!/usr/bin/env python3
"""Render 1920x1080 with-vs-without comparison MP4 from hero_q1_deploy_vllm.json."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install Pillow: pip install pillow", file=sys.stderr)
    raise

W, H = 1920, 1080
FPS = 30
DURATION = 82


def load_font(size: int):
    for name in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        p = Path(name)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * max(0.0, min(1.0, t))


def frame_at(t: float, m: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), "#0a0c10")
    draw = ImageDraw.Draw(img)
    f_title = load_font(52)
    f_h = load_font(36)
    f_m = load_font(28)
    f_s = load_font(22)

    wo = m["without_fastcontext"]["solver_total_tokens"]
    wi = m["with_fastcontext_nvfp4"]["solver_total_tokens"]
    pct = m["derived"]["api_token_reduction_pct"]
    q = m["question"]
    if len(q) > 110:
        q = q[:107] + "..."

    draw.text((80, 48), "Same question. Two ways.", fill="#e8ecf4", font=f_title)
    draw.text((80, 120), q, fill="#9aa7bd", font=f_s)

    # Phase weights
    if t < 8:
        phase = "intro"
    elif t < 34:
        phase = "without"
    elif t < 40:
        phase = "bridge"
    else:
        phase = "with"

    # Token animation
    if phase == "without":
        prog = (t - 8) / 26
        cur = int(lerp(0, wo, prog))
        label = "API only · stuff entire demo repo"
        color = "#ff6b6b"
    elif phase == "with":
        prog = (t - 40) / 28
        cur = int(lerp(wo * 0.15, wi, prog))
        label = "FastContext NVFP4 on GB10 → citations → API"
        color = "#5befa8"
    else:
        cur = 0 if phase == "intro" else wo
        label = "Preparing comparison..."
        color = "#9aa7bd"

    draw.rounded_rectangle((80, 200, W - 80, 520), radius=18, outline="#2a3344", width=3)
    draw.text((110, 230), label, fill=color, font=f_h)
    draw.text((110, 300), f"{cur:,}", fill="#ffffff", font=load_font(96))
    draw.text((110, 420), "API solver tokens", fill="#9aa7bd", font=f_m)

    bar_w = W - 200
    fill_w = int(bar_w * (cur / max(wo, 1)))
    draw.rectangle((100, 470, 100 + bar_w, 500), fill="#1a2230")
    draw.rectangle((100, 470, 100 + fill_w, 500), fill=color)

    if t >= 62:
        draw.rounded_rectangle((80, 560, W - 80, 760), radius=18, fill="#121820", outline="#3d4f6a")
        draw.text(
            (110, 590),
            f"−{pct}% API tokens  ·  {m['derived']['nvfp4_decode_tok_s']} tok/s NVFP4  ·  {m['derived']['model_size_gb_nvfp4']} GB",
            fill="#e8ecf4",
            font=f_h,
        )
        draw.text(
            (110, 660),
            "Fixture: demos/sample-repo (this repo) — not hermes-concurrent-agents",
            fill="#7d8aa3",
            font=f_s,
        )
        draw.text(
            (110, 700),
            "HF: r0b0tlab/FastContext-1.0-4B-RL-NVFP4",
            fill="#7d8aa3",
            font=f_s,
        )

    if phase == "bridge":
        draw.text((80, 820), "Or… explore locally first", fill="#c7d2e5", font=f_h)

    draw.text((80, H - 50), "github.com/r0b0tlab/FastContext-1.0-4B-RL-NVFP4", fill="#5a6478", font=f_s)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)

    nframes = DURATION * FPS
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(args.output),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(nframes):
        t = i / FPS
        proc.stdin.write(frame_at(t, metrics).tobytes())
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise SystemExit(rc)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()