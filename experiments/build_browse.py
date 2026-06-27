#!/usr/bin/env python
"""Join run transcripts with basin labels into a databrowser site.
  .venv/bin/python experiments/build_browse.py <all.jsonl> <basins.jsonl> <out_site_dir>
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import databrowser
from databrowser import FilterField

all_path, basins_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
runs = {(json.loads(l)["model_slug"], json.loads(l)["stim_slug"], json.loads(l)["run_id"]): json.loads(l)
        for l in Path(all_path).read_text().splitlines() if l.strip()}
labels = {(j["model"], j["stim"], j["run_id"]): j
          for j in (json.loads(l) for l in Path(basins_path).read_text().splitlines() if l.strip())}

records = []
for k, r in runs.items():
    lab = labels.get(k, {})
    ac = r.get("assistant_chars") or []
    records.append({
        "model": r.get("model_slug"),
        "stimulus": r.get("stim_slug"),
        "stim_class": r.get("stim_class"),
        "basin": lab.get("basin", "?"),
        "run_id": r.get("run_id"),
        "peak_chars": max(ac) if ac else 0,
        "last_chars": ac[-1] if ac else 0,
        "n_turns": len(ac),
        "error": r.get("error") or "none",
        "evidence": lab.get("evidence", ""),
        "transcript": r.get("transcript", ""),
    })

databrowser.build(
    records, out_dir=out_dir,
    filter_fields=["model", "stimulus", "stim_class", "basin", "error",
                   FilterField("peak_chars", "continuous")],
    title="LLM attractor basins — repeated-prompt runs",
)
print(f"built {len(records)} records -> {out_dir}")
