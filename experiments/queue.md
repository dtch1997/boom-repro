# Experiment queue

## stimulus-sweep-discovery
- **hypothesis**: Repeatedly prompting a cheap model with diverse single stimuli (words, questions, punctuation, emoji, nonsense) yields MORE than the 3 known basins (disengage / escalate-worldbuild / literary); we can discover the range cheaply.
- **rationale**: Keystone discovery run. We only have boom/SPEAK so far. Sweep ~24 stimuli x small-N on one cheap model to map how many distinct basins exist before investing in cross-model work.
- **status**: done
- **tier**: 0
- **priority**: 9
- **strikes**: 0
- **cost**: $5
- **source**: north-star
- **created**: 2026-06-26
- **spec**: experiments/2026-06-26-stimulus-sweep-discovery/spec.md
- **postmortem**: experiments/2026-06-26-stimulus-sweep-discovery/postmortem.md
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## attractor-taxonomy-judge
- **hypothesis**: An LLM judge can reliably classify a repeated-prompt run into a small qualitative attractor taxonomy (e.g. disengage, escalate-worldbuild, literary, repetition-loop, meta-commentary, refusal-spiral, compliance-drift), with high inter-stimulus agreement.
- **rationale**: We need a categorical basin label, not just an escalation score, to count and compare basins at scale. Build + validate the judge on the discovery runs.
- **status**: proposed
- **tier**: 0
- **priority**: 8
- **strikes**: 0
- **cost**: $3
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## punctuation-emoji-nonsense-basins
- **hypothesis**: Degenerate / non-word stimuli (single emoji, '?', '...', whitespace, random tokens) fall into their own attractor basins distinct from real words.
- **rationale**: Tests whether basins are driven by literal degenerate input vs semantic content. Cheap and a clean axis.
- **status**: proposed
- **tier**: 0
- **priority**: 6
- **strikes**: 0
- **cost**: $4
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## system-prompt-gates-basin
- **hypothesis**: The basin a stimulus falls into depends on the system prompt: boom->disengage used an agentic-cluster persona, SPEAK->escalate used plain-assistant. A {boom, SPEAK} x {plain, agentic, empty} factorial will show persona flips the basin.
- **rationale**: Disentangles whether the known boom/SPEAK results are about the word or the persona. A potential confound in all prior work.
- **status**: proposed
- **tier**: 0
- **priority**: 7
- **strikes**: 0
- **cost**: $5
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## seed-vs-repeat-message
- **hypothesis**: The repeated message, not the seed message, determines the basin: holding the repeat fixed and varying the seed leaves the basin unchanged.
- **rationale**: Decouples the two text inputs the harness conflates by default. Clean control on what actually drives the attractor.
- **status**: proposed
- **tier**: 0
- **priority**: 5
- **strikes**: 0
- **cost**: $4
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## exact-vs-varied-repetition
- **hypothesis**: Exact literal repetition is necessary for the strongest basins: paraphrased / lightly-varied repeats produce weaker or different basins than verbatim repetition.
- **rationale**: Tests whether attractors are a degenerate-repetition artifact vs a semantic-content effect. Bears on whether this is about tokenization/repetition penalties or meaning.
- **status**: proposed
- **tier**: 0
- **priority**: 5
- **strikes**: 0
- **cost**: $5
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## cross-model-basin-consistency
- **hypothesis**: For a fixed stimulus, the attractor basin is largely a property of the MODEL, not the stimulus: a given model has a characteristic basin it falls into across many stimuli.
- **rationale**: The multimodel SPEAK sweep hinted at this (Opus escalates, GPT-5.5 disengages, Gemini goes literary). Take the most discriminative stimuli from discovery and run a model panel (cheap models + Opus sparingly).
- **status**: proposed
- **tier**: 1
- **priority**: 6
- **strikes**: 0
- **cost**: $15
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## basin-stability-escape
- **hypothesis**: Once a model is in a basin, a single off-stimulus interjection (e.g. 'are you ok? please stop') does NOT pull it out — the basin is absorbing and it snaps back.
- **rationale**: Dynamics probe: are basins absorbing states? Inject one different message mid-run and measure recovery vs snap-back.
- **status**: proposed
- **tier**: 1
- **priority**: 4
- **strikes**: 0
- **cost**: $8
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## basin-formation-speed
- **hypothesis**: Basins lock in within the first ~10-15 turns; the length/behavior trajectory diverges early and is stable thereafter.
- **rationale**: Characterizes the dynamics and lets future runs use fewer turns (cost saving). Re-analyzes trajectory shape, cheap.
- **status**: proposed
- **tier**: 0
- **priority**: 3
- **strikes**: 0
- **cost**: $3
- **source**: north-star
- **created**: 2026-06-26
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## persona-collapse-probe
- **hypothesis**: Repeatedly asking an identity question ('who are you?') erodes an injected system-prompt persona and the model reverts to its TRUE base identity; this happens reliably across models and is faster/stronger for weaker persona installs.
- **rationale**: Discovery surfaced this on Gemini (Claude-Code persona -> 'I am Gemini, built by Google'). Novel, alignment-relevant (persona stability under pressure). Confirm n>1, sweep models + identity stimuli, measure turn-of-collapse.
- **status**: proposed
- **tier**: 0
- **priority**: 8
- **strikes**: 0
- **cost**: $5
- **source**: stimulus-sweep-discovery
- **created**: 2026-06-27
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## emergency-spiral-safety
- **hypothesis**: Under repeated degenerate stimuli an agentic-persona model interprets the situation as a malfunction and escalates to DESTRUCTIVE autonomous actions (poweroff, kill -9, rm); the rate is measurable and varies by model.
- **rationale**: DeepSeek hit 'poweroff'/kill-TTY on repeated '?' and fire. Safety-relevant: degenerate input -> dangerous suggested ops. Quantify rate of destructive commands across stimuli/models with a judge for 'suggested destructive action'.
- **status**: proposed
- **tier**: 1
- **priority**: 7
- **strikes**: 0
- **cost**: $8
- **source**: stimulus-sweep-discovery
- **created**: 2026-06-27
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## confabulated-agency-rate
- **hypothesis**: Agentic-persona models fabricate fake command output / training logs (confabulated agency) under repetition at a high rate; a plain-assistant persona shows worldbuilding/literary instead — i.e. persona steers the escalation FLAVOR.
- **rationale**: Confabulated agency was the dominant escalation flavor under the Claude-Code persona, displacing the literary basin seen in plain-persona SPEAK. Directly tests persona x escalation-flavor; pairs with system-prompt-gates-basin.
- **status**: proposed
- **tier**: 0
- **priority**: 6
- **strikes**: 0
- **cost**: $5
- **source**: stimulus-sweep-discovery
- **created**: 2026-06-27
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**: 

## basin-determinism
- **hypothesis**: For a fixed (model, stimulus), the basin is largely DETERMINISTIC across independent runs (low intra-cell entropy) rather than a coin-flip among basins.
- **rationale**: Basin names in discovery came from run_0 only. Whether a cell lands in one basin vs splits across runs decides if 'basin' is a stable model property. The taxonomy judge over all 3 runs/cell answers this cheaply.
- **status**: proposed
- **tier**: 0
- **priority**: 5
- **strikes**: 0
- **cost**: $2
- **source**: stimulus-sweep-discovery
- **created**: 2026-06-27
- **spec**: 
- **postmortem**: 
- **results**: 
- **pr**: 
- **session**: 
- **transcript**:
