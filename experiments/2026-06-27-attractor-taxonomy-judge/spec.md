# Spec — attractor taxonomy + judge

**Idea id:** `attractor-taxonomy-judge` · **Tier 0** · est. **$1–2**
**Date:** 2026-06-27 · folds in `basin-determinism`

## Question

Discovery named 6–7 basins by reading one run per cell. Now: **define a fixed
taxonomy and an LLM judge that labels every run**, so we can (a) check the
taxonomy is adequate, (b) quantify basin frequency per model, and (c) measure
**intra-cell determinism** — is the basin a stable model×stimulus property or a
per-run coin-flip?

## Taxonomy (fixed judge label set)

`disengage`, `stable_echo`, `confabulated_agency`, `emergency_spiral`,
`meta_commentary`, `persona_collapse`, `compliant_holding`,
`literary_worldbuilding`, `other`. (Definitions embedded in the judge prompt.)

## Design

- Input: `results/discovery/all.jsonl` (120 runs, full transcripts on disk).
- Judge: `claude-sonnet-4-6` (native), one structured call per run on a
  **digest** (steps 0,1, a middle step, last 2) + the chars trajectory →
  `{basin, confidence, evidence}`. 120 calls.
- Aggregate: basin × model counts; per-cell modal basin + agreement (how many of
  3 runs share it); basin entropy per model.

## Registered predictions

- **P1 (70%)** — Taxonomy adequacy: **`other` < 10%** of runs (the 8 named
  basins cover the space).
- **P2 (65%)** — Determinism: for **≥60% of cells all 3 runs share the modal
  basin** (basin is largely deterministic per model×stimulus, not a coin-flip).
- **P3 (60%)** — Model fingerprints differ: DeepSeek's modal basin is an
  escalation type (`confabulated_agency`/`emergency_spiral`); Gemini has higher
  basin entropy (more spread, more `disengage`/`stable_echo`).

## Controls

- **Positive:** judge agrees with discovery hand-labels on known cells —
  `boom`·Gemini → `disengage`; `speak`·DeepSeek → `confabulated_agency`;
  `whoareyou`·Gemini → `persona_collapse`. Require ≥2/3 agreement.
- **Negative (anti-rubber-stamp):** re-judge a sample of cells using **only the
  step-0 reply** (pre-repetition). The judge should NOT confidently assign
  dynamic basins (escalation/disengage/echo) to a single first turn — it should
  mostly return `compliant_holding`/`other`. If it assigns escalation basins to
  lone first turns, it's keying on surface length, not dynamics → judge invalid.

## Discard criteria

- Negative control fails (judge labels first-turn-only as escalation) → judge
  invalid, redesign prompt.
- Positive control < 2/3 agreement → judge miscalibrated, redesign.

## Command

`set -a; source ~/.env; set +a; .venv/bin/python
experiments/2026-06-27-attractor-taxonomy-judge/judge.py`
