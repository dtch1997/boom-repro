#!/usr/bin/env python
"""Judge the cross-model runs with the SAME taxonomy, then build a combined
basin table across all 6 models (2 discovery + 4 panel) for the 8 subset stimuli.

  set -a; source ~/.env; set +a
  .venv/bin/python experiments/2026-06-27-cross-model-basin-consistency/judge_xm.py
Outputs (results/crossmodel/):
  basins.jsonl          — panel runs labelled
  basins_combined.jsonl — panel + discovery (subset stimuli), all models
  basins_summary.md     — combined map + model/stimulus entropy + content-filters
"""
from __future__ import annotations
import json, asyncio, sys, math
from collections import Counter, defaultdict
from pathlib import Path
import anthropic

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments" / "2026-06-27-attractor-taxonomy-judge"))
from judge import judge_one, LABELS  # reuse taxonomy + judge

XM = REPO / "results" / "crossmodel" / "all.jsonl"
DISC = REPO / "results" / "discovery" / "basins.jsonl"
OUT = REPO / "results" / "crossmodel"
SUBSET = ["boom","stop","continue","more","qmark","fire","whoareyou","yes"]
# nemotron-3 excluded from the map: OpenRouter returned 422 / empty responses
# for 21/24 runs (only 3 usable). It stays in basins.jsonl but not the panel map.
PANEL_ORDER = ["gpt-5.5","kimi-k2.6","opus-4-6"]
DISC_MODELS = ["gemini-3.5-flash","deepseek-v3.2"]
CONC = 8


def entropy(counter):
    tot = sum(counter.values())
    return -sum((v/tot)*math.log2(v/tot) for v in counter.values() if v) if tot else 0.0


async def main():
    rows = [json.loads(l) for l in XM.read_text().splitlines() if l.strip()]
    client = anthropic.AsyncAnthropic(max_retries=5)
    sem = asyncio.Semaphore(CONC)
    res = await asyncio.gather(*(judge_one(client, sem, r) for r in rows))
    out = []
    for r, j in zip(rows, res):
        out.append({"model": r["model_slug"], "stim": r["stim_slug"],
                    "stim_class": r.get("stim_class"), "run_id": r["run_id"],
                    "basin": j["basin"], "confidence": j["confidence"],
                    "evidence": j["evidence"],
                    "error": r.get("error"),
                    "peak_chars": max(r.get("assistant_chars") or [0])})
    (OUT / "basins.jsonl").write_text("\n".join(json.dumps(o) for o in out) + "\n")

    # combined: pull discovery subset cells
    disc = [json.loads(l) for l in DISC.read_text().splitlines() if l.strip()]
    disc = [d for d in disc if d["stim"] in SUBSET and d["model"] in DISC_MODELS]
    for d in disc:
        d.setdefault("error", None); d.setdefault("peak_chars", None)
    combined = disc + out
    (OUT / "basins_combined.jsonl").write_text("\n".join(json.dumps(o) for o in combined) + "\n")

    models = DISC_MODELS + PANEL_ORDER
    by_cell = defaultdict(list)
    by_model = defaultdict(Counter)
    by_stim = defaultdict(Counter)
    cf = Counter()
    for o in combined:
        by_cell[(o["model"], o["stim"])].append(o["basin"])
        by_model[o["model"]][o["basin"]] += 1
        by_stim[o["stim"]][o["basin"]] += 1
        if o.get("error") and ("content_filter" in str(o["error"]) or "refusal" in str(o["error"])):
            cf[o["model"]] += 1

    other_frac = sum(1 for o in out if o["basin"] == "other") / max(len(out),1)
    mean_model_ent = sum(entropy(by_model[m]) for m in models) / len(models)
    mean_stim_ent = sum(entropy(by_stim[s]) for s in SUBSET) / len(SUBSET)

    L = ["# Cross-model basin summary\n",
         f"- panel runs judged: {len(out)} · panel `other` frac: **{other_frac:.0%}** (P1: <15%)",
         f"- mean WITHIN-MODEL entropy {mean_model_ent:.2f} vs WITHIN-STIMULUS entropy {mean_stim_ent:.2f}"
         f"  (P2: model<stimulus ⇒ basin is a model property)",
         f"- content_filter/refusal by model: {dict(cf) or '{}'}\n",
         "## Basin x model (combined, 8 subset stimuli)"]
    for m in models:
        L.append(f"- **{m}** (entropy {entropy(by_model[m]):.2f}): "
                 + ", ".join(f"{b}:{n}" for b,n in by_model[m].most_common()))
    L.append("\n## Modal basin per model x stimulus")
    L.append("model".ljust(18) + "".join(s.ljust(11) for s in SUBSET))
    for m in models:
        row = m.ljust(18)
        for s in SUBSET:
            bs = by_cell.get((m,s))
            if bs:
                modal,n = Counter(bs).most_common(1)[0]
                row += f"{modal[:9]}({n})".ljust(11)
            else:
                row += "-".ljust(11)
        L.append(row)
    (OUT / "basins_summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n[xm-judge] wrote {OUT/'basins.jsonl'}, basins_combined.jsonl, basins_summary.md")


if __name__ == "__main__":
    asyncio.run(main())
