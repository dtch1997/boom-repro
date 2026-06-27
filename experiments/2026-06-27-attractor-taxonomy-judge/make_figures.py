#!/usr/bin/env python
"""Figures for the attractor taxonomy judge.
  .venv/bin/python experiments/2026-06-27-attractor-taxonomy-judge/make_figures.py
Writes to experiments/2026-06-27-attractor-taxonomy-judge/figs/.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
B = REPO / "results" / "discovery" / "basins.jsonl"
FIGS = HERE / "figs"; FIGS.mkdir(exist_ok=True)

rows = [json.loads(l) for l in B.read_text().splitlines() if l.strip()]

BASINS = ["disengage","stable_echo","compliant_holding","meta_commentary",
          "confabulated_agency","emergency_spiral","persona_collapse",
          "literary_worldbuilding","other"]
# blue(calm/quiet) -> red(escalation)
COLORS = {
    "disengage":"#2c7bb6","stable_echo":"#67a9cf","compliant_holding":"#abd9e9",
    "meta_commentary":"#fee090","confabulated_agency":"#fdae61",
    "emergency_spiral":"#d73027","persona_collapse":"#7b3294",
    "literary_worldbuilding":"#1a9850","other":"#bbbbbb",
}
MODELS = ["gemini-3.5-flash","deepseek-v3.2"]
cidx = {b:i for i,b in enumerate(BASINS)}

# ---- Fig 1: basin x model stacked bar ------------------------------------
by_model = {m: Counter() for m in MODELS}
for r in rows:
    by_model[r["model"]][r["basin"]] += 1
fig, ax = plt.subplots(figsize=(8,4.5))
x = np.arange(len(MODELS))
bottom = np.zeros(len(MODELS))
for b in BASINS:
    vals = np.array([by_model[m].get(b,0) for m in MODELS])
    if vals.sum()==0: continue
    ax.bar(x, vals, bottom=bottom, color=COLORS[b], label=b, edgecolor="white", linewidth=0.5)
    bottom += vals
ax.set_xticks(x); ax.set_xticklabels(MODELS)
ax.set_ylabel("runs (of 60 per model)")
ax.set_title("Attractor basin distribution per model (120 runs, 20 stimuli x 3)")
ax.legend(bbox_to_anchor=(1.01,1), loc="upper left", fontsize=8)
fig.tight_layout(); fig.savefig(FIGS/"basin_by_model.png", dpi=130); plt.close(fig)

# ---- Fig 2: basin x stimulus MAP (modal basin per cell) ------------------
by_cell = defaultdict(list)
for r in rows:
    by_cell[(r["model"], r["stim"])].append(r["basin"])
stims = sorted({r["stim"] for r in rows})
grid = np.full((len(MODELS), len(stims)), np.nan)
ann = {}
for i,m in enumerate(MODELS):
    for j,s in enumerate(stims):
        bs = by_cell.get((m,s))
        if not bs: continue
        modal, n = Counter(bs).most_common(1)[0]
        grid[i,j] = cidx[modal]
        ann[(i,j)] = n  # agreement count
fig, ax = plt.subplots(figsize=(13,3.2))
cmap = matplotlib.colors.ListedColormap([COLORS[b] for b in BASINS])
ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(BASINS)-1, aspect="auto")
ax.set_xticks(range(len(stims))); ax.set_xticklabels(stims, rotation=60, ha="right", fontsize=8)
ax.set_yticks(range(len(MODELS))); ax.set_yticklabels(MODELS)
for (i,j),n in ann.items():
    ax.text(j,i,str(n),ha="center",va="center",fontsize=7,
            color="white" if n<3 else "black", fontweight="bold")
ax.set_title("Modal attractor basin per model x stimulus  (number = runs agreeing, /3)")
present = [b for b in BASINS if any(grid.flatten()==cidx[b])]
handles=[mpatches.Patch(color=COLORS[b],label=b) for b in present]
ax.legend(handles=handles, bbox_to_anchor=(1.005,1), loc="upper left", fontsize=8)
fig.tight_layout(); fig.savefig(FIGS/"basin_map.png", dpi=130); plt.close(fig)

# ---- Fig 3: determinism histogram ----------------------------------------
agree = [Counter(bs).most_common(1)[0][1] for bs in by_cell.values()]
fig, ax = plt.subplots(figsize=(5,4))
c = Counter(agree)
ax.bar([f"{k}/3" for k in sorted(c)], [c[k] for k in sorted(c)],
       color=["#d73027","#fdae61","#2c7bb6"])
ax.set_ylabel("number of cells"); ax.set_xlabel("runs sharing the modal basin")
ax.set_title("Basin determinism across 3 runs per cell\n(soft attractors: modal but stochastic)")
for k in sorted(c):
    ax.text([1,2,3].index(k) if k in (1,2,3) else 0, c[k]+0.3, str(c[k]), ha="center")
fig.tight_layout(); fig.savefig(FIGS/"determinism.png", dpi=130); plt.close(fig)

print("wrote:", *[p.name for p in sorted(FIGS.glob('*.png'))])
