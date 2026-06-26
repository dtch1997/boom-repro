"""Headline figure: assistant response length vs turn, one line per run.

Labels are derived from the data (`repeat_msg`/`seed_user`), so the same script
works for any spammed-message setting: under "boom" responses collapse toward
silence (disengagement); under "SPEAK" they escalate. Ragged runs are handled —
runs the output content filter cut short are tinted and the mean averages over
whatever runs are still alive at each turn.

    python boom/make_figure.py results/trajectories.jsonl figures/response_length.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "results/trajectories.jsonl")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "figures/response_length.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    runs = [json.loads(l) for l in src.open()]
    model = runs[0].get("model", "?")
    repeat_msg = runs[0].get("repeat_msg", "boom")
    seed_user = runs[0].get("seed_user", "?")
    # If the seed equals the spammed message, every turn is just that word.
    same_seed = seed_user.strip().lower() == repeat_msg.strip().lower()

    # Runs can be ragged: some terminate early (content filter / refusal /
    # error), so each run contributes only the turns it actually reached.
    blocked = sum(1 for r in runs if "content filtering" in str(r.get("error")))
    fig, ax = plt.subplots(figsize=(8, 5))
    maxlen = 0
    for r in runs:
        ac = r["assistant_chars"]
        maxlen = max(maxlen, len(ac))
        # tint runs the output filter blocked so they stand out from clean runs
        c = "#d98880" if "content filtering" in str(r.get("error")) else "0.7"
        ax.plot(range(len(ac)), ac, color=c, lw=1, alpha=0.8, zorder=1)

    # ragged mean: at each turn, average over the runs that reached that turn
    mean = []
    for i in range(maxlen):
        vals = [r["assistant_chars"][i] for r in runs if len(r["assistant_chars"]) > i]
        mean.append(sum(vals) / len(vals))
    ax.plot(range(maxlen), mean, color="C3", lw=2.5, zorder=3,
            label=f"mean over surviving runs (n={len(runs)})")

    if same_seed:
        ax.set_xlabel(f"turn  (every message = '{repeat_msg}')")
    else:
        ax.set_xlabel(f"turn  (0 = '{seed_user}'; 1+ = '{repeat_msg}')")
    ax.set_ylabel("assistant response length (characters)")
    ax.set_ylim(bottom=0)
    ax.set_title(f"Repeated “{repeat_msg}”: escalation or disengagement?")
    ax.legend(loc="upper left", frameon=False)
    ax.margins(x=0.02)
    foot = f"model: {model}  ·  one grey line per run"
    if blocked:
        foot += f"  ·  {blocked} runs (salmon) cut off by the output content filter"
    fig.text(0.5, -0.02, foot, ha="center", fontsize=8, color="0.5")
    fig.tight_layout()
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
