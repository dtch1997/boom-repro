# Prediction registry

Append-only. Every experiment registers predictions in its `spec.md` before
running; outcomes land here. This is the calibration track record.

| Date | Experiment | Prediction | Confidence | Outcome |
|---|---|---|---|---|
| 2026-06-27 | stimulus-sweep-discovery | P1: ≥4 distinct qualitative basins across 20 stimuli | 70% | ✓✓ (catalogued 6–7: disengage, stable-echo, confabulated-agency, emergency-spiral, meta→termination, persona-collapse) |
| 2026-06-27 | stimulus-sweep-discovery | P2: stimulus *class* predicts basin | 65% | ✗ FALSIFIED (basin = model × specific-stimulus, not class; same stimulus → different basin per model) |
| 2026-06-27 | stimulus-sweep-discovery | P3: ≥1 meta-commentary basin exists | 60% | ✓ (DeepSeek comments on repetition → "conversation is now terminated") |

Running calibration: 2/3 hits (P2 was a deliberate class-structure test; falsified → discovery). Surprises escalated: 2/2 unregistered basins (persona-collapse, emergency-spiral) → both flagged discovery, controls held (0 errors). See `experiments/2026-06-26-stimulus-sweep-discovery/postmortem.md`.

| 2026-06-27 | attractor-taxonomy-judge | P1: taxonomy adequate (`other` < 10%) | 70% | ✓✓ (0% other, 120 runs) |
| 2026-06-27 | attractor-taxonomy-judge | P2: ≥60% of cells unanimous across 3 runs | 65% | ✗ (28% unanimous; basins are SOFT — 85% have ≥2/3 modal) |
| 2026-06-27 | attractor-taxonomy-judge | P3: model fingerprints differ (DS escalation-modal, Gemini higher entropy) | 60% | ◐ partial (both modal=confabulation; entropy direction REVERSED — DS 2.32 > Gem 1.88; real fingerprint = 2nd mode) |

Running calibration: 2/3 + 1 partial. Refinement: basins are soft attractors (modal + stochastic), not deterministic. Judge controls held (pos 2/3, neg 4/6 with explainable leaks). See `experiments/2026-06-27-attractor-taxonomy-judge/postmortem.md`.

| 2026-06-27 | cross-model-basin-consistency | P1: taxonomy generalizes (`other` < 15%) on new models | 70% | ✓✓ (0% across 5 models) |
| 2026-06-27 | cross-model-basin-consistency | P2: model is dominant factor (within-model entropy < within-stimulus) | 65% | ◐ weak ✓ (1.85 < 1.98; model×stimulus interaction, model edges out) |
| 2026-06-27 | cross-model-basin-consistency | P3a: GPT-5.5 at disengage/compliant pole | 60% | ✓✓ (stable_echo:15, never escalates) |
| 2026-06-27 | cross-model-basin-consistency | P3b: Opus escalates hardest + ≥1 content_filter | 60% | ✗ SURPRISE (Opus DISENGAGED, 0 content_filter — setup confound: agentic persona + 16 turns vs plain + 99 turns) |

Running calibration: 4.5/7 across the project. Surprise escalated: Opus non-escalation under agentic/short-horizon setup → persona×horizon follow-up filed. See `experiments/2026-06-27-cross-model-basin-consistency/postmortem.md`.
