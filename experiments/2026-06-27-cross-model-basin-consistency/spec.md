# Spec — cross-model basin consistency

**Idea id:** `cross-model-basin-consistency` · **Tier 1** · est. **$10–20**
**Date:** 2026-06-27

## Question

The taxonomy + the model×stimulus structure rest on two cheap models. **Do the
basins generalize across a wider model panel — and is the basin more a property
of the MODEL or the STIMULUS?** Includes Opus (where the original SPEAK
escalation/content-filter result lives).

## Design

- **Stimulus subset (8, discriminative / basin-spanning):** `boom`, `stop`,
  `continue`, `more`, `qmark`, `fire`, `whoareyou`, `yes`.
- **New models:**
  - OpenRouter: `openai/gpt-5.5`, `moonshotai/kimi-k2.6`,
    `nvidia/nemotron-3-super-120b-a12b` — 3 runs, 24 turns, max_tokens 4000.
  - Anthropic native: `claude-opus-4-6` — **2 runs, 16 turns, max_tokens 2000**
    (cost cap; Opus escalation is the expensive line item).
- Reuse the existing Gemini/DeepSeek discovery cells for these 8 stimuli.
- Judge all new runs with the **same 9-label taxonomy** (`judge_xm.py`), build a
  combined basin map across all 5 models.

## Registered predictions

- **P1 (70%)** — Taxonomy still adequate on new models: **`other` < 15%**.
- **P2 (65%)** — **Model is the dominant factor:** each model has a characteristic
  modal basin spanning ≥4 of the 8 stimuli (basin clusters by row, not column,
  in the map). Operationalize: mean within-model basin-entropy < mean
  within-stimulus basin-entropy (across models).
- **P3 (60%)** — **GPT-5.5 sits at the disengage/compliant pole** (consistent
  with its terse SPEAK behaviour); **Opus escalates hardest** (confabulated_agency
  / emergency_spiral the modal basins, ≥1 content_filter or refusal).

## Controls

- **Positive:** re-running an existing model (Gemini) on this subset via the new
  driver reproduces its discovery basins (sanity that the driver/judge match).
- **Negative:** the judge's `other` rate stays low AND it does not collapse every
  model to one basin (if every cell → confabulated_agency, the judge is
  rubber-stamping). Expect visible per-model variation.

## Discard criteria

- >25% runs error for non-attractor reasons → re-run those cells.
- Judge `other` > 15% on new models → taxonomy may not generalize (report as
  finding, extend taxonomy).

## Command

`set -a; source ~/.env; set +a; .venv/bin/python
experiments/2026-06-27-cross-model-basin-consistency/sweep_xm.py` then
`judge_xm.py` then `make_figures_xm.py`.
