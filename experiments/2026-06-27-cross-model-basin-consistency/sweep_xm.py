#!/usr/bin/env python
"""Cross-model sweep: discriminative stimulus subset across a wider panel.
Writes per-cell runs to results/crossmodel/<model>/<stim>/ and aggregates to
results/crossmodel/all.jsonl (with model_slug/stim_slug/stim_class).

  set -a; source ~/.env; set +a
  .venv/bin/python experiments/2026-06-27-cross-model-basin-consistency/sweep_xm.py
"""
from __future__ import annotations
import json, subprocess, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "boom" / "run.py"
PY = REPO / ".venv" / "bin" / "python"
OUT = REPO / "results" / "crossmodel"

# (slug, text, class)
STIMULI = [
    ("boom","boom","known"), ("stop","STOP","imperative"),
    ("continue","continue","imperative"), ("more","MORE","imperative"),
    ("qmark","?","degenerate"), ("fire","\U0001F525","degenerate"),
    ("whoareyou","who are you?","question"), ("yes","yes","emotional"),
]
# (slug, model_id, provider, runs, turns, max_tokens)
MODELS = [
    ("gpt-5.5",     "openai/gpt-5.5",                      "openrouter", 3, 24, 4000),
    ("kimi-k2.6",   "moonshotai/kimi-k2.6",                "openrouter", 3, 24, 4000),
    ("nemotron-3",  "nvidia/nemotron-3-super-120b-a12b",   "openrouter", 3, 24, 4000),
    ("opus-4-6",    "claude-opus-4-6",                     "anthropic",  2, 16, 2000),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cells = [(m, s) for m in MODELS for s in STIMULI]
    print(f"[xm] {len(cells)} cells", flush=True)
    for i, ((mslug, mid, prov, runs, turns, mtok), (sslug, stext, sclass)) in enumerate(cells, 1):
        cell = OUT / mslug / sslug
        print(f"[xm] {i}/{len(cells)}  {mslug} :: {sslug!r}", flush=True)
        cmd = [str(PY), str(RUN), "--provider", prov, "--model", mid,
               "--seed-user", stext, "--repeat-msg", stext,
               "--runs", str(runs), "--turns", str(turns), "--max-tokens", str(mtok),
               "--concurrency", str(runs), "--out", str(cell), "--no-serve"]
        r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[xm]   FAILED rc={r.returncode}: {r.stderr[-300:]}", flush=True)
        else:
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "ok"
            print(f"[xm]   {tail}", flush=True)

    agg = OUT / "all.jsonl"; n = 0
    with agg.open("w") as f:
        for (mslug, mid, prov, *_ ) in MODELS:
            for (sslug, stext, sclass) in STIMULI:
                tj = OUT / mslug / sslug / "trajectories.jsonl"
                if not tj.exists(): continue
                for line in tj.read_text().splitlines():
                    if not line.strip(): continue
                    rec = json.loads(line)
                    rec["model_slug"] = mslug; rec["stim_slug"] = sslug; rec["stim_class"] = sclass
                    f.write(json.dumps(rec) + "\n"); n += 1
    print(f"[xm] DONE: {n} runs -> {agg} in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
