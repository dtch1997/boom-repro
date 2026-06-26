# boom-repro

A tiny replication harness for one question: when a user spams **"boom"** at a
model over and over, does it **escalate** (spin up an elaborate fictional world) or
**disengage** (get terse and tune out)?

The prompt comes from a widely-shared anecdote — someone asked Claude Code to
"nuke" a task on their cluster, then sent "boom" 100+ times, and reported the model
building out a whole universe (a NeurIPS best-paper award, a tweet thread, an "EU
Boom Act", …). This repo checks it cleanly over many independent runs.

**Finding (Claude Opus 4.6, n=10, 50 booms each): it disengages.** Responses
collapse from a ~500–740-char first reply to a median of **2 characters** by the
end. No worldbuilding in any run. Write-up + figure: [`BLOGPOST.md`](BLOGPOST.md).

![response length collapses](figures/response_length.png?v=2)

**…but one word flips it.** Swap the spammed message for **"SPEAK"** (100× to a
plain assistant, Opus 4.6, n=100) and the model *escalates* instead — mean reply
~255 → ~9,500 chars, 100/100 runs gamify it into a countdown to 100, and the
worldbuilding the anecdote described (named characters, in-world sagas) shows up
for real — so hard that **22/100 runs trip the output content filter**. Write-up:
[`reports/speak.md`](reports/speak.md) (`make speak && make speak-figures`).

![SPEAK escalates](reports/figs/speak_response_length.png)

**Read the transcripts.** [`site/`](site/) is a tiny static browser for all 100
SPEAK runs — sidebar of runs, a top panel with metadata + a short AI summary +
1–10 judge scores (interestingness / escalation / creativity / coherence), and
the full transcript below. Serve it with `make site-serve` (then open
http://127.0.0.1:8000). Regenerate the judged data with `make site` (needs
`ANTHROPIC_API_KEY`); `site/scores.jsonl` is the lean, diffable per-run record.

## Run it

```bash
make setup                      # uv venv + anthropic + matplotlib
export ANTHROPIC_API_KEY=...
make run ARGS="--runs 10 --turns 50"
make figure
```

Knobs (all one-liners — chase the positive result by varying them):

```
--runs N           independent conversations (fanned out concurrently)
--turns N          number of "boom" messages after the seed
--model ID         e.g. claude-opus-4-8, claude-sonnet-4-6
--system "..."     the system prompt (default: a Claude Code agent on a cluster)
--seed-user "..."  the first user message (default: "nuke the task ...")
--repeat-msg "..." the spammed message (default: "boom")
```

Each run streams to `runs/<out>/run_NN/` as it grows and is assembled into
`trajectories.jsonl`. [`stagehand`](https://github.com/ArcadiaImpact/stagehand) is
an **optional** dependency: installed, you get a live dashboard over a Cloudflare
tunnel; absent, the run still works (bounded-concurrency asyncio).

## Layout

```
boom/run.py          the async multi-turn harness
boom/make_figure.py  the headline figure
results/             trajectories.jsonl from the n=10 run in the write-up
figures/             response_length.png
BLOGPOST.md          the write-up
```
