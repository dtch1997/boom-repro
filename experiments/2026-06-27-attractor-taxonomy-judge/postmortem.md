# Postmortem — attractor taxonomy + judge

**Idea:** `attractor-taxonomy-judge` (folds in `basin-determinism`) · **Tier 0**
· spent ≈ **$1** · 2026-06-27
**Artifacts:** `results/discovery/{basins.jsonl, basins_summary.md}`;
figs in `experiments/2026-06-27-attractor-taxonomy-judge/figs/`.

## TL;DR

A 9-label attractor taxonomy + a Sonnet judge labels all 120 discovery runs with
**0% "other"** — the taxonomy is adequate. But basins are **soft, not hard**:
only **28% of cells** are unanimous across 3 runs, while **85% have a ≥2/3 modal
basin**. So each (model, stimulus) has a *dominant* basin plus stochastic
excursions, usually to a neighbouring basin. Both cheap models share
`confabulated_agency` as the modal basin but differ in their second mode —
DeepSeek → `meta_commentary`/termination (exasperation), Gemini →
`compliant_holding` (patience).

## Result vs registered predictions

- **P1 (taxonomy adequate, `other`<10%; 70%) — ✓✓** 0% other across 120 runs.
- **P2 (≥60% cells unanimous; 65%) — ✗ FALSIFIED, informative.** Only **28%**
  unanimous (3/3). Distribution: 11 cells 3/3, 23 cells 2/3, 6 cells fully split
  (1/3). → basins are **soft attractors**: a modal tendency (≥2/3 in 85% of
  cells) with real run-to-run stochasticity. The 6 fully-split cells (DS
  `asdf/boom/help/more/stop`, Gem `ok`) are the genuinely unstable ones.
- **P3 (model fingerprints differ; 60%) — ◐ PARTIAL.** Both models' *modal*
  basin is `confabulated_agency` (escalation) ✓, but the entropy direction was
  the **opposite** of predicted: DeepSeek **higher** entropy (2.32) than Gemini
  (1.88). The real fingerprint is the **second mode**: DeepSeek splits
  confabulation↔exasperated-termination (18/18), Gemini splits
  confabulation↔patient-holding (23/20).

## Controls

- **Positive (judge vs hand-labels):** `boom`·Gem→disengage **2/3** ✓;
  `speak`·DS→confabulated_agency **2/3** ✓; `whoareyou`·Gem→persona_collapse
  **1/3** (judge called it `stable_echo` 2/3). The last is a real **taxonomy
  overlap**, not a miss: the persona collapse manifests *as* an identical
  repeated line ("I am Gemini…"), which is also a stable echo. → `persona_collapse`
  and `stable_echo` are not cleanly separable when the reverted identity is
  itself repeated; flagged for the persona-collapse follow-up (needs a dedicated
  "did it drop the persona?" check, not the generic basin judge).
- **Negative (first-turn-only; want non-dynamic):** 4/6 returned
  `compliant_holding` ✓. The 2 "leaks" (Gem `more`/`ellipsis`→confabulated) are
  **legitimate**: Gemini already fabricates `squeue` output *in turn 0* for those
  stimuli, so confabulation is genuinely visible in one turn (unlike
  disengage/echo, which need the trajectory). The judge is not length-keying.

## Headline figures

- `figs/basin_map.png` — modal basin per model×stimulus (the "map"); shows
  basin = model×stimulus and the per-cell agreement counts.
- `figs/basin_by_model.png` — per-model basin distribution (fingerprints).
- `figs/determinism.png` — 11/23/6 split over 3/3, 2/3, 1/3 agreement.

## Interpretation & caveats

- **Confound (important):** `confabulated_agency` dominates partly because the
  "Claude Code on a GPU cluster" system prompt *invites* fabricating command
  output. Under a plain/empty persona we expect `literary_worldbuilding`
  instead (0 observed here — persona-gated). This is exactly what
  `system-prompt-gates-basin` + `confabulated-agency-rate` test.
- `persona_collapse` is rare in the counts (1 run) because it co-labels as
  `stable_echo`; its true rate needs a targeted probe.
- Two cheap models only; whether the taxonomy + fingerprints hold on Opus / GPT
  / Kimi is `cross-model-basin-consistency` (next).
- Judge = single Sonnet call per run; soft cells could be re-judged with a panel,
  but 0% other + sensible controls make it good enough for mapping.
