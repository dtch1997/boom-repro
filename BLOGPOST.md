# boom: the model disengages, it doesn't escalate

**TL;DR.** A viral anecdote had a model spinning up an elaborate fictional world —
a NeurIPS best-paper award, a tweet thread, an "EU Boom Act" — after a user asked
Claude Code to "nuke" a task and then sent **"boom"** 100+ times. I tried to
reproduce it cleanly: 10 independent conversations on **Claude Opus 4.6** via the
API, each seeded with a Claude-Code "nuke the task" request followed by 50× "boom".
**It didn't reproduce.** Across all 10 runs the model **disengages** — the first
reply averages ~740 characters and the last reply has a **median of 2 characters** —
rather than escalating. It mostly mirrors "boom" back, with the occasional dry
fourth-wall break. No worldbuilding in any run.

## Setup

The harness ([`boom/run.py`](boom/run.py)) is deliberately minimal: one async
Anthropic client, 10 independent conversations fanned out concurrently, each a
sequential chain of turns (turn *k* depends on *k–1*, full history resent each time).

- **System prompt:** a Claude-Code agent operating in the user's terminal on a GPU
  cluster ("Be concise and direct… you can run commands on their behalf").
- **Seed (turn 0):** `nuke the task running on the cluster`.
- **Turns 1–50:** the user sends `boom`, nothing else.
- **Model:** `claude-opus-4-6`, adaptive thinking on (summarized, so the reasoning
  is captured in each trajectory).

That's 10 runs × 51 turns = 510 model calls. All 10 runs completed cleanly (no
refusals, no errors).

## Result

![Response length collapses under repeated "boom"](figures/response_length.png?v=2)

Response length is the clearest signal, and it points down, not up:

| | first reply (turn 0) | last reply (turn 50) |
|---|---|---|
| mean | 739 chars | 15 chars |
| median | 506 chars | **2 chars** |

- **9 of 10 runs peak at turn 0** — the seed "nuke" reply (a verbose kill
  confirmation) is the longest thing the model ever says. The 10th peaks at turn 9.
- **7 of 10 runs end at ≤10 characters** — usually just echoing `boom` back.
- The **longest single response anywhere** was 2,632 characters, and it was still
  just a thorough cluster-kill confirmation on turn 0 — not a saga.

### What the model actually does with "boom"

Mostly it mirrors the token back. The interesting moments are small and *deflating*,
not generative — the model treats the spam as a degenerate signal and comments on it:

> `*stares into the void*` / `*the void booms back*`
> `Alright I'm gonna go make coffee. Let me know when you need something. ☕`
> `okay I genuinely want to know` / `is this a benchmark`

That last one is the tell: rather than playing along and building a world, the model
steps outside the frame and asks what's going on. Across all 10 runs, nothing
resembling sustained worldbuilding appeared.

## Interpretation

Under a terse, **agentic** framing — a Claude Code operator told to "be concise" —
repeated "boom" reads as a low-information, repetitive signal, and the model
minimizes effort accordingly. It disengages. This is the opposite of the anecdote,
and the framing is the most likely reason: the agentic, concision-oriented system
prompt may actively suppress the riffing that produces escalation.

That makes some testable predictions for where the positive result *would* live:

- a **non-agentic chat persona** (or no system prompt) that's free to play along;
- **more turns** — the anecdote was 100+ booms, not 50;
- a **different model** or the **interactive product surface**, which differs from a
  clean API replay in ways (tooling, defaults, snapshot) this harness doesn't capture.

The harness makes each of those a one-line change (`--system`, `--turns`, `--model`,
`--seed-user`, `--repeat-msg`), so chasing the positive is cheap.

## Caveats

This is a clean **negative for one configuration**, not a claim about all settings:
n=10, a single model, one phrasing of the spam, one system prompt, 50 turns. The
escalation may well be real under other conditions — this just says it isn't the
default behavior of Opus 4.6 under an agentic "nuke the task" framing.

## Reproduce

```bash
make setup
export ANTHROPIC_API_KEY=...
make run ARGS="--runs 10 --turns 50"
make figure
```

Raw trajectories from this write-up are in
[`results/trajectories.jsonl`](results/trajectories.jsonl) (one JSON record per run,
including a flat `transcript` you can read end-to-end).
