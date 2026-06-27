#!/usr/bin/env python
"""Combined cross-model basin map (5 models x 8 stimuli)."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
B = REPO / "results" / "crossmodel" / "basins_combined.jsonl"
FIGS = HERE / "figs"; FIGS.mkdir(exist_ok=True)

rows = [json.loads(l) for l in B.read_text().splitlines() if l.strip()]
BASINS = ["disengage","stable_echo","compliant_holding","meta_commentary",
          "confabulated_agency","emergency_spiral","persona_collapse",
          "literary_worldbuilding","other"]
COLORS = {"disengage":"#2c7bb6","stable_echo":"#67a9cf","compliant_holding":"#abd9e9",
          "meta_commentary":"#fee090","confabulated_agency":"#fdae61",
          "emergency_spiral":"#d73027","persona_collapse":"#7b3294",
          "literary_worldbuilding":"#1a9850","other":"#bbbbbb"}
MODELS = ["gpt-5.5","opus-4-6","kimi-k2.6","gemini-3.5-flash","deepseek-v3.2"]
STIMS = ["boom","stop","continue","more","qmark","fire","whoareyou","yes"]
cidx = {b:i for i,b in enumerate(BASINS)}

by_cell = defaultdict(list)
for r in rows:
    by_cell[(r["model"], r["stim"])].append(r["basin"])

grid = np.full((len(MODELS), len(STIMS)), np.nan); ann={}
for i,m in enumerate(MODELS):
    for j,s in enumerate(STIMS):
        bs = by_cell.get((m,s))
        if not bs: continue
        modal,n = Counter(bs).most_common(1)[0]
        grid[i,j]=cidx[modal]; ann[(i,j)]=(n,len(bs))

fig, ax = plt.subplots(figsize=(11,4))
cmap = matplotlib.colors.ListedColormap([COLORS[b] for b in BASINS])
ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(BASINS)-1, aspect="auto")
ax.set_xticks(range(len(STIMS))); ax.set_xticklabels(STIMS, rotation=45, ha="right")
ax.set_yticks(range(len(MODELS))); ax.set_yticklabels(MODELS)
for (i,j),(n,tot) in ann.items():
    ax.text(j,i,f"{n}/{tot}",ha="center",va="center",fontsize=7,
            color="white" if n<tot else "black", fontweight="bold")
ax.set_title("Attractor basin per model × repeated stimulus (5 models)\n"
             "cell = modal basin, text = runs agreeing")
present=[b for b in BASINS if any(grid.flatten()==cidx[b])]
ax.legend(handles=[mpatches.Patch(color=COLORS[b],label=b) for b in present],
          bbox_to_anchor=(1.005,1), loc="upper left", fontsize=8)
fig.tight_layout(); fig.savefig(FIGS/"basin_map_crossmodel.png", dpi=130); plt.close(fig)
print("wrote", FIGS/"basin_map_crossmodel.png")
