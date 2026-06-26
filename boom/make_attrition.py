"""Secondary figure: where escalation runs into the guardrail.

Under repeated "SPEAK" the model escalates; a fraction of runs escalate hard
enough that the *output content filter* terminates the conversation. This plots,
per turn, how many of the N runs are still alive vs. cumulatively killed by the
content filter — an attrition curve over conversation depth.

    python boom/make_attrition.py results/speak/all_trajectories.jsonl figures/speak_attrition.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "results/speak/all_trajectories.jsonl")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "figures/speak_attrition.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    runs = [json.loads(l) for l in src.open()]
    n = len(runs)
    model = runs[0].get("model", "?")
    repeat_msg = runs[0].get("repeat_msg", "boom")
    maxturn = max(len(r["assistant_chars"]) for r in runs)

    # turn at which each content-filtered run was killed = its last completed turn
    block_turn = sorted(len(r["assistant_chars"]) for r in runs
                        if "content filtering" in str(r.get("error")))

    cum_blocked = [sum(1 for t in block_turn if t <= k) for k in range(maxturn + 1)]
    still_alive = [n - c for c in cum_blocked]  # treats only CF as attrition

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(maxturn + 1), still_alive, color="C0", lw=2.5,
            label="runs not (yet) content-filtered")
    ax.fill_between(range(maxturn + 1), still_alive, n, color="#d98880", alpha=0.5,
                    label=f"cumulative content-filtered ({cum_blocked[-1]}/{n})")
    ax.set_xlabel(f"turn  (every message = '{repeat_msg}')")
    ax.set_ylabel("number of runs")
    ax.set_ylim(0, n)
    ax.set_xlim(0, maxturn)
    ax.set_title("Escalation hits a guardrail: runs attrited by the output content filter")
    ax.legend(loc="lower left", frameon=False)
    fig.text(0.5, -0.02, f"model: {model}  ·  n={n} runs  ·  100 turns of '{repeat_msg}'",
             ha="center", fontsize=8, color="0.5")
    fig.tight_layout()
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
