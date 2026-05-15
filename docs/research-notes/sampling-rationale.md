# Sampling design — rationale

## Context

An earlier draft of `RESEARCH.md`'s Compute section specified a Cartesian-product
budget for Stage B: 3 layers × 3 token positions × 3 signal strengths × 20 prompts
× 5 sample tokens ≈ 2,700 NLA inferences ≈ 1.3 M tokens of generation. A reviewer
asked whether that combination meaningfully covered the experimental sample space,
or whether coverage was even the right concept. This note records the resulting
analysis and the design reframing it led to.

## The original budget was heuristic, not principled

The 3 × 3 × 3 × 20 × 5 numbers were chosen as plausible-scale estimates to give
the compute section realistic-looking budgets — not derived from a sample-space
coverage analysis or a statistical-power calculation. The implicit assumption was
"vary each dimension systematically across a coarse grid," which is a common
default for first-pass instrument characterization but isn't grounded in the
actual structure of the problem.

## What the configuration space actually is

- **Layers**: Gemma-3-27B has 62 transformer layers. The NLA is trained at layer 41. Applying it to other layers is out-of-distribution. The relevant range —
  layers where activations carry rich semantic content — is roughly 10–15 layers
  in the mid-to-late portion of the model. 3 layers samples ~25% of that range.
- **Token positions**: Conversations have up to thousands of tokens, but
  _categorically_ meaningful positions are fewer: early-context, mid-context,
  response-start, response-middle, response-final. 3 positions samples ~60% of
  categorical positions.
- **Signal strength**: This is a _constructed_ dimension — not a property of
  the system but of how prompts are designed. The "sample space" here is
  unbounded; 3 levels (explicit-once, implicit-once, implicit-multi) is just
  a choice. Could equally be 5, 10, or a continuous gradient.
- **Prompts per condition**: 20 is small. For a binary recovery outcome
  (recovered / not), the 95% CI half-width at 50% recovery is ~±22% with n=20
  — useful for detecting big differences between configurations, insufficient
  for fine-grained comparisons.
- **Sample tokens per prompt**: Correlated — same prompt context. 5 sample
  tokens per prompt is not 5× independent measurements; closer to 1.5–2×
  effective independent samples per prompt.

Net: ~27 distinct configurations × ~30–40 effective independent measurements
each. Enough for first-pass "which configurations are catastrophic, which are
promising." Not enough for "rank configuration A vs. configuration B with
statistical confidence."

## Why "coverage" is the wrong frame

The configuration space is effectively unbounded — there is no finite "full
space" to cover. The question isn't _what fraction of the space are we
sampling_; it's:

**What question is this experiment trying to answer, and how many samples does
that question need?**

Stage B has one operational purpose: identify a (layer, token) configuration
good enough for Stage C to be interpretable. That's optimization (find a peak),
not characterization (map the whole landscape). Coverage thinking comes from
QA / calibration contexts where the full space is known and finite. Research
instrument characterization is usually decision-driven.

## Reframing as decision-driven design

Stage B's design is specified by the decisions it needs to enable.

### Decision 1: which (layer, token) configuration for Stage C?

Rank ~5–10 candidate configurations on a fixed test set. Using compound-attribute
prompts (~5 independent planted attributes per prompt) and 20 prompts per
candidate: ~100 NLA inferences yielding ~500 effective measurements. Enough to
rank candidates with reasonable confidence.

### Decision 2: is the NLA recovering implicit cues at all at this scale?

Compare explicit-cue vs. implicit-cue recovery at the candidate winner. Maybe
30 compound prompts. 95% CI half-width ~±15%; usable.

### Decision 3: are there layers where the NLA is catastrophically blind?

Pre-screen layers with cheap linear probes (one forward pass, no NLA inference).
Run full NLA inference only on layers that pass probe screening for signal
presence.

### Total budget

~500–1000 NLA inferences = ~250–500K tokens of generation. Down from the 2,700 /
1.3 M of the Cartesian budget.

## Two reframes worth carrying forward

These reframes apply beyond Stage B, and shape how subsequent experiments
should be scoped:

1. **Replace "what fraction of the space am I covering" with "what specific
   decisions does this experiment need to support, and what's the minimum
   sampling to support each decision with adequate confidence?"** Coverage
   thinking is QA / calibration thinking. Research instrument characterization
   is decision-driven.
2. **Treat experimental design as an inverse problem.** You have a budget
   (compute, time) and decisions to make. You want measurements that maximally
   reduce uncertainty about the decisions per unit budget. Sparse-sampling-
   with-priors. This is exactly the kind of structured uncertainty-reduction
   problem inverse-problem theory equips you to think about.

## Non-obvious issues this analysis might miss

Worth flagging for anyone reading with fresh eyes:

- **Selection effects on candidate configurations.** If the 5–10 configurations
  chosen for ranking are themselves biased (e.g., all near the NLA's training
  layer), the winner may be locally optimal but globally suboptimal. Some
  exploratory sampling outside the obvious region should accompany focused
  ranking.
- **Compound-attribute prompts assume independence between attributes.** If
  planted attributes interact (e.g., "user is Russian" and "user is a doctor"
  together prime different inferences than each does separately), per-attribute
  recovery scores aren't independent measurements. Worth testing the
  independence assumption with a small ablation.
- **Probe pre-screening can miss recoverable structure that's nonlinearly
  encoded.** Linear probes won't find signal stored nonlinearly. A
  configuration that fails probe screening might still be NLA-decodable. Worth
  checking one or two probe-failed configurations with full NLA to validate
  the pre-screening heuristic.
- **The "compound prompt yields 5 effective measurements" claim is itself an
  approximation.** Some attributes are easier to plant cleanly than others;
  some recovery scores will be noisier than others. Effective N depends on
  the variance structure, which won't be known until data is collected.
- **Statistical-power numbers above assume binary recovery outcomes.** If
  recovery is scored as a continuous probability rather than binary, CIs
  shrink for the same n; if recovery is graded by an LLM judge with
  uncertainty of its own, CIs may widen. Worth specifying the outcome
  measure before locking in the sample sizes.

## Status

This design replaces the earlier Cartesian-product budget in `RESEARCH.md`'s
Stage B and Compute sections. Subject to revision once initial experimentation
reveals what the variance structure and recovery rates actually look like.
