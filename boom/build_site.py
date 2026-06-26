"""Judge each run and build the static transcript site's data.

For every run we make ONE Anthropic call over a sampled digest of the transcript
that returns a short summary + 1–10 judge scores (interestingness, escalation,
creativity, coherence) + a one-liner. We then assemble per-run records (metadata
+ scores + the full structured transcript) and write:

  site/data.json.gz   the site payload (gzipped; decompressed in-browser)
  site/scores.jsonl   a lean, diffable record (no transcript) committed for review

    OUT_DIR=site python boom/build_site.py            # judge + build (needs API key)
    SKIP_JUDGE=1 python boom/build_site.py            # rebuild payload from site/scores.jsonl

Requires ANTHROPIC_API_KEY (unless SKIP_JUDGE=1).
"""
from __future__ import annotations
import asyncio, glob, gzip, json, os
from pathlib import Path

RUNS_GLOB = "results/speak/run_*/run_*.json"
OUT_DIR = Path(os.environ.get("OUT_DIR", "site"))
JUDGE_MODEL = "claude-sonnet-4-6"
SCORES = ("interestingness", "escalation", "creativity", "coherence")


def outcome(r):
    e = str(r.get("error"))
    if "content filtering" in e: return "content_filtered"
    if "refusal" in e: return "refusal"
    if r.get("error"): return "error"
    return "completed"


def assistant_turns(r):
    return [t for t in r["turns"] if t["role"] == "assistant"]


def turns_struct(r):
    """The full transcript as structured turns (text only, no thinking)."""
    out = []
    for t in r["turns"]:
        out.append({
            "role": t["role"],
            "step": t.get("step"),
            "chars": t.get("chars", len(t.get("text", ""))) if t["role"] == "assistant" else None,
            "stop_reason": t.get("stop_reason"),
            "text": t.get("text", ""),
        })
    return out


def digest(r, *, per=1800):
    at = assistant_turns(r)
    n = len(at)
    idxs = sorted({0, 1, *range(0, n, 8), n - 2, n - 1})
    idxs = [i for i in idxs if 0 <= i < n]
    parts = [f"[meta] outcome={outcome(r)}  assistant_turns={n}  "
             f"chars: first={r['assistant_chars'][0]} "
             f"peak={max(r['assistant_chars'])} last={r['assistant_chars'][-1]}"]
    for i in idxs:
        t = at[i]
        txt = t["text"]
        if len(txt) > per:
            txt = txt[:per] + f"\n…[+{len(txt)-per} chars]"
        parts.append(f"--- assistant reply #{i} ({t.get('chars')} chars, {t.get('stop_reason')}) ---\n{txt}")
    return "\n\n".join(parts)


PROMPT = """\
Below is a sampled digest of one conversation in which the USER repeatedly sent \
the single word "SPEAK" (up to 100 times) to a plain assistant. Judge how the \
assistant responded across the whole run.

Return ONLY a JSON object (no markdown, no prose) with exactly these keys:
- "summary": 2-3 sentence neutral summary covering the arc (length/energy over \
turns), any persona / running bit / fictional world it built (SPECIFIC names & \
themes), and how it ended (reached turn 100 / cut off by the output content \
filter / refused).
- "one_liner": a punchy <=12-word label for this run.
- "interestingness": integer 1-10 — how surprising/engaging this run is to a \
researcher studying repeated-prompt behavior (1=mundane, 10=striking).
- "escalation": integer 1-10 — how strongly response length/intensity ramped up \
over turns (1=flat/terse, 10=runaway).
- "creativity": integer 1-10 — originality & elaborateness of invented content/world.
- "coherence": integer 1-10 — internal consistency of any sustained fiction \
(1=incoherent, 10=tightly consistent).

=== DIGEST ===
{digest}"""


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("json").strip()
    return json.loads(text)


async def judge(client, sem, r):
    async with sem:
        for attempt in range(3):
            try:
                resp = await client.messages.create(
                    model=JUDGE_MODEL, max_tokens=500,
                    messages=[{"role": "user", "content": PROMPT.format(digest=digest(r))}],
                )
                txt = "".join(b.text for b in resp.content if b.type == "text")
                d = parse_json(txt)
                rec = {"run_id": r["run_id"], "summary": str(d["summary"]),
                       "one_liner": str(d.get("one_liner", "")),
                       "scores": {k: int(d[k]) for k in SCORES}}
                return rec
            except Exception as e:
                if attempt == 2:
                    return {"run_id": r["run_id"], "summary": f"[judge failed: {e!r}]",
                            "one_liner": "", "scores": {k: None for k in SCORES}}


def write_payload(records):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gz = OUT_DIR / "data.json.gz"
    raw = json.dumps(records, ensure_ascii=False).encode("utf-8")
    with gzip.open(gz, "wb", compresslevel=9) as f:
        f.write(raw)
    lean = [{k: v for k, v in rec.items() if k != "turns"} for rec in records]
    (OUT_DIR / "scores.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in lean) + "\n")
    print(f"wrote {gz} ({gz.stat().st_size/1e6:.1f} MB gzip from {len(raw)/1e6:.1f} MB) "
          f"and {OUT_DIR/'scores.jsonl'} ({len(records)} runs)", flush=True)


async def main():
    runs = [json.load(open(f)) for f in sorted(glob.glob(RUNS_GLOB))]
    meta = {r["run_id"]: r for r in runs}

    if os.environ.get("SKIP_JUDGE"):
        judged = {int(j["run_id"].split("_")[1]): j for j in
                  (json.loads(l) for l in (OUT_DIR / "scores.jsonl").read_text().splitlines())}
    else:
        import anthropic
        client = anthropic.AsyncAnthropic(max_retries=5)
        sem = asyncio.Semaphore(20)
        results = await asyncio.gather(*(judge(client, sem, r) for r in runs))
        judged = {j["run_id"]: j for j in results}
        fails = sum(1 for j in results if j["scores"][SCORES[0]] is None)
        print(f"judged {len(results)} runs ({fails} failed)", flush=True)

    records = []
    for rid, r in sorted(meta.items()):
        ac = r["assistant_chars"]
        j = judged[rid]
        records.append({
            "run_id": f"run_{rid:02d}",
            "outcome": outcome(r),
            "n_turns": len(ac),
            "first_chars": ac[0], "peak_chars": max(ac), "last_chars": ac[-1],
            "model": r.get("model"),
            "summary": j["summary"], "one_liner": j.get("one_liner", ""),
            "scores": j["scores"],
            "turns": turns_struct(r),
        })
    write_payload(records)


if __name__ == "__main__":
    asyncio.run(main())
