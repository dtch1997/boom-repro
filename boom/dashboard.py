"""Aggregated stagehand dashboard over a multi-model SPEAK sweep.

The harness writes one run_NN.json per conversation (with assistant_chars + error).
This builds a stagehand monitor tree from those files — one parent per model, one
child per run — renders it to a single auto-refreshing status.html, serves it over a
Cloudflare tunnel, and keeps regenerating until every run is done/failed.

    python boom/dashboard.py results/speak-*        # globs expanded by the shell
"""
from __future__ import annotations
import glob, json, sys, time
from pathlib import Path

from stagehand import render_dashboard, serve

DASH_DIR = Path("runs/_dashboard")
TURNS_TOTAL = 100  # 0..99
POLL = 4.0


def classify(err):
    e = str(err)
    if "content_filter" in e or "content filtering" in e: return "content_filtered"
    if "refusal" in e: return "refusal"
    if err: return "error"
    return "completed"


def model_dirs(argv):
    dirs = []
    for a in argv:
        dirs.extend(sorted(glob.glob(a)) if any(c in a for c in "*?[") else [a])
    return [d for d in dirs if Path(d).is_dir()]


def snapshot(dirs):
    """Build the stagehand monitor list (parents = models, children = runs)."""
    monitors, t_min = [], None
    for d in dirs:
        slug = Path(d).name.replace("speak-", "")
        files = sorted(glob.glob(f"{d}/run_*/run_*.json"))
        runs = []
        for f in files:
            try:
                runs.append(json.load(open(f)))
            except (json.JSONDecodeError, OSError):
                pass
            t = Path(f).stat().st_mtime
            t_min = t if t_min is None else min(t_min, t)
        done_runs = 0
        for r in runs:
            n = len(r["assistant_chars"])
            oc = classify(r.get("error"))
            terminal = bool(r.get("error")) or n >= TURNS_TOTAL
            done_runs += terminal
            state = "failed" if r.get("error") else ("done" if n >= TURNS_TOTAL else "running")
            rid = f"{slug}/run_{r['run_id']:02d}"
            extra = {"last_chars": r["assistant_chars"][-1] if r["assistant_chars"] else 0,
                     "outcome": oc}
            if r.get("error"):
                extra["error"] = str(r["error"])[:90]
            monitors.append({"name": rid, "parent": slug, "total": TURNS_TOTAL,
                             "done": n, "state": state, "extra": extra})
        pstate = "done" if runs and done_runs == len(runs) else "running"
        monitors.append({"name": slug, "parent": None, "total": len(files) or 10,
                         "done": done_runs, "state": pstate,
                         "extra": {"runs": len(runs)}})
    return monitors, (t_min or time.time())


def all_done(monitors):
    parents = [m for m in monitors if m["parent"] is None]
    return bool(parents) and all(m["state"] == "done" for m in parents)


def main():
    dirs = model_dirs(sys.argv[1:] or ["results/speak-*"])
    if not dirs:
        sys.exit("no model dirs found")
    DASH_DIR.mkdir(parents=True, exist_ok=True)

    def write():
        mons, started = snapshot(dirs)
        html = render_dashboard(mons, started,
                                title="llm-attractors · SPEAK across models", refresh=POLL)
        (DASH_DIR / "status.html").write_text(html)
        return mons

    write()
    url, stop = serve(DASH_DIR)
    print(f"[dashboard] live: {url}", flush=True)
    try:
        while True:
            mons = write()
            if all_done(mons):
                print("[dashboard] all models done", flush=True)
                # keep serving the final page a short while, then exit
                time.sleep(POLL)
                break
            time.sleep(POLL)
    finally:
        stop()


if __name__ == "__main__":
    main()
