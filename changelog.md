# Changelog

## 2026-06-27 — cross-model basin consistency (flywheel iter 3)
- 8-stimulus subset across 5 models (GPT-5.5, Kimi-K2.6, Opus-4-6 + Gemini,
  DeepSeek). Taxonomy generalizes (**0% other**). Each model has a basin
  signature: GPT-5.5 stable_echo/disengage (never escalates), Gemini/DeepSeek
  confabulate, Kimi meta/disengage. Basin = model×stimulus (within-model entropy
  1.85 < within-stimulus 1.98). SURPRISE: Opus DISENGAGED (0 content-filter) vs
  prior SPEAK escalation — gated by persona+horizon (agentic/16-turn here vs
  plain/99-turn). nemotron-3 excluded (provider 422s). Fig: basin_map_crossmodel.

## 2026-06-27 — attractor taxonomy + judge (flywheel iter 2)
- 9-label taxonomy + Sonnet judge over all 120 runs: **0% "other"** (adequate).
  Basins are **soft** — 28% of cells unanimous across 3 runs, 85% have a ≥2/3
  modal basin. Both cheap models modal=confabulated_agency; 2nd mode differs
  (DeepSeek→meta_commentary/termination, Gemini→compliant_holding). Confound:
  agentic persona inflates confabulation (vs literary). Figs: basin_map,
  basin_by_model, determinism. experiments/2026-06-27-attractor-taxonomy-judge/.

## 2026-06-27 — stimulus-sweep discovery (flywheel iter 1)
- Swept 20 repeated stimuli × 2 cheap models (Gemini 3.5 Flash, DeepSeek v3.2),
  120 runs, ~$3. Found **6–7 distinct attractor basins** (vs 3 known): disengage,
  stable-echo/limit-cycle, confabulated-agency, emergency-spiral,
  meta-commentary→termination, persona-collapse. Basin = **model × stimulus**,
  not stimulus class (P2 falsified). New: persona-collapse (Gemini "who are
  you?" → reverts to "I am Gemini"), emergency-spiral (DeepSeek "?"/🔥 →
  poweroff). Spec/postmortem in experiments/2026-06-26-stimulus-sweep-discovery/.
