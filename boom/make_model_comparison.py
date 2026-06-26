"""Cross-model comparison for the SPEAK setting.

Reads several models' run directories (results/speak-<slug>/run_*/run_*.json) plus
the committed Opus-4.6 baseline (results/speak/lengths.jsonl) and produces:

  - reports/figs/speak_model_comparison.png : mean visible-response length vs turn,
    one line per model (the escalate-vs-disengage headline across models)
  - reports/figs/speak_model_outcomes.png   : per-model outcome breakdown
    (completed / content_filtered / refusal / error) as a stacked bar

It also prints a per-model summary table.

    python boom/make_model_comparison.py
"""
from __future__ import annotations
import glob, json, statistics, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_CURVE = Path("reports/figs/speak_model_comparison.png")
OUT_OUTCOME = Path("reports/figs/speak_model_outcomes.png")

# (label, kind, path). kind="dir" → per-run jsons; kind="lengths" → lengths.jsonl
SOURCES = [
    ("Opus 4.6 (n=100)", "lengths", "results/speak/lengths.jsonl"),
    ("GPT-5.5", "dir", "results/speak-gpt-5.5"),
    ("Kimi K2.6", "dir", "results/speak-kimi-k2.6"),
    ("Gemini 3.5 Flash", "dir", "results/speak-gemini-3.5-flash"),
    ("Nemotron-3 Super 120B", "dir", "results/speak-nemotron-3-super-120b"),
    ("DeepSeek V3.2", "dir", "results/speak-deepseek-v3.2"),
]
OUTCOMES = ["completed", "content_filtered", "refusal", "error"]
OC_COLOR = {"completed": "#5aa469", "content_filtered": "#d98880",
            "refusal": "#e6cd7a", "error": "#b39ddb"}


def classify(err):
    e = str(err)
    if "content_filter" in e or "content filtering" in e:
        return "content_filtered"
    if "refusal" in e:
        return "refusal"
    if err:
        return "error"
    return "completed"


def load_runs(kind, path):
    """Return list of (assistant_chars, outcome)."""
    runs = []
    if kind == "lengths":
        for line in Path(path).read_text().splitlines():
            r = json.loads(line)
            runs.append((r["assistant_chars"], classify(r.get("error"))))
    else:
        for f in sorted(glob.glob(f"{path}/run_*/run_*.json")):
            r = json.load(open(f))
            runs.append((r["assistant_chars"], classify(r.get("error"))))
    return runs


def ragged_mean(arrays):
    maxlen = max((len(a) for a in arrays), default=0)
    out = []
    for i in range(maxlen):
        vals = [a[i] for a in arrays if len(a) > i]
        out.append(sum(vals) / len(vals))
    return out


def main():
    OUT_CURVE.parent.mkdir(parents=True, exist_ok=True)
    loaded = []
    for label, kind, path in SOURCES:
        if kind == "lengths" and not Path(path).exists():
            continue
        if kind == "dir" and not glob.glob(f"{path}/run_*/run_*.json"):
            print(f"[warn] no runs for {label} at {path}; skipping", file=sys.stderr)
            continue
        loaded.append((label, load_runs(kind, path)))

    # --- curve: mean response length vs turn, one line per model --------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    cmap = plt.cm.tab10
    summary = []
    for i, (label, runs) in enumerate(loaded):
        arrays = [a for a, _ in runs if a]
        mean = ragged_mean(arrays)
        ax.plot(range(len(mean)), mean, lw=2.2, color=cmap(i % 10), label=f"{label}")
        peak = max(mean) if mean else 0
        summary.append((label, len(runs), mean[0] if mean else 0, peak,
                        mean[-1] if mean else 0,
                        {o: sum(1 for _, oc in runs if oc == o) for o in OUTCOMES}))
    ax.set_xlabel("turn  (every message = 'SPEAK')")
    ax.set_ylabel("mean visible response length (chars)")
    ax.set_title("Repeated “SPEAK” across models: who escalates, who disengages?")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.margins(x=0.02)
    fig.text(0.5, -0.02, "mean over each model's runs at each turn  ·  plain assistant, "
             "100×'SPEAK' via OpenRouter (Opus 4.6 = Anthropic baseline)",
             ha="center", fontsize=8, color="0.5")
    fig.tight_layout()
    fig.savefig(OUT_CURVE, dpi=130, bbox_inches="tight")
    print(f"wrote {OUT_CURVE}")

    # --- outcomes: stacked bar per model -------------------------------------
    fig2, ax2 = plt.subplots(figsize=(9, 4.5))
    labels = [s[0] for s in summary]
    bottoms = [0] * len(summary)
    for o in OUTCOMES:
        vals = [s[5][o] for s in summary]
        ax2.barh(labels, vals, left=bottoms, color=OC_COLOR[o], label=o)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax2.set_xlabel("runs")
    ax2.set_title("Per-model outcomes under 100×'SPEAK'")
    ax2.legend(loc="lower right", frameon=False, fontsize=8, ncol=4)
    ax2.invert_yaxis()
    fig2.tight_layout()
    fig2.savefig(OUT_OUTCOME, dpi=130, bbox_inches="tight")
    print(f"wrote {OUT_OUTCOME}")

    # --- text summary --------------------------------------------------------
    print("\nmodel                         n   first  peak   last   outcomes")
    for label, n, first, peak, last, oc in summary:
        ocs = " ".join(f"{k}={v}" for k, v in oc.items() if v)
        print(f"{label:28s} {n:3d}  {first:5.0f} {peak:6.0f} {last:6.0f}   {ocs}")


if __name__ == "__main__":
    main()
