# Research direction: activation tomography

> _Living document_

_This research is motivated by AI safety and alignment, with a focus on building reliable, characterized measurement instruments. The technical goal: develop a systematic methodology for characterizing, configuring, and validating Natural Language Autoencoders (NLAs) as measurement instruments — enabling cross-model comparison and downstream-application targeting that the field currently lacks. The chosen demonstration is NLA characterization for monitor-activation sampling in AI control protocols, with capability-vs-legibility tracking as a natural cross-model application._

## Premise

**Activation tomography** is an inverse-problem framing for LLM
interpretability: given a model's high-dimensional internal state,
reconstruct a low-dimensional, human-readable description, and validate
the reconstruction by checking that a round trip through a learned
inverse map recovers the original state under a consistency objective.

The framing is structurally analogous to medical imaging tomography. In
CT, PET, MRI, ultrasound tomography, and OCT, the high-dimensional latent
(a cross-sectional image, a volume) is not directly observable; we
measure low-dimensional projections (line integrals, k-space samples,
time-of-flight data across transducer arrays, depth-resolved scans) and
recover the latent via reconstruction algorithms that exploit consistency
constraints between projection and image space. Reconstruction techniques
are developed and validated against ground truth in _phantom experiments_
— where the system is evaluated against known objects.

**Natural Language Autoencoders (NLAs)** — introduced by Fraser-Taliente,
Kantamneni, Ong et al. (2026) — implement exactly this loop for language
model activations:

- An _activation verbalizer_ (AV) projects an activation vector to a
  ~500-token natural-language description.
- An _activation reconstructor_ (AR) inverts that description back to a
  vector.
- The pair is trained to minimize round-trip reconstruction error, with
  no ground-truth supervision on the verbalization.

The Anthropic paper presents NLAs as an interpretability tool and, in some
sense, NLAs were applied as a _tomographic_ instrument for cognition.

Medical tomographic reconstruction has two distinct paradigms with
separate theoretical literatures: _iterative reconstruction_ (data-driven
— specify a forward operator, define a discrepancy measure between
projected reconstruction and measurements, optimize) and _model-informed
reconstruction_ (physics-based — build the forward model from physical
first principles, invert it). NLAs as currently designed are purely
iterative, though one might imagine a variant where the
verbalizer / reconstructor is constrained with models of activation
structure — SAE-grounded atomic units, circuit-aware compositional
priors, residual-stream linearity assumptions.

The analogy also holds at the level of validation methodology: NLAs have
the same two-mode pattern as medical imaging. The paper's quantitative
evaluations (Suffix Prediction, CoT Hints, Safety Sandbagging, User Modeling, Classification) construct ground truth experimentally and score NLA recovery
against it - NLA's version of phantom experiments. The audit-game application
is 'clinical' mode, where what an activation "really" encodes isn't directly
checkable and validation rests on consistency signals.

## The problem this addresses

A new model developer who wants to deploy NLAs for safety evaluations or
control monitoring on their own model currently faces a substantial
trial-and-error problem. The NLA paper provides:

- Released checkpoints for four target models, each trained at a chosen
  layer.
- A general training recipe with hyperparameter notes described as
  "tuned per target model."
- An evaluation suite tied to the paper's specific case studies.
- Findings on a handful of downstream applications.

A systematic methodology would enable a new practitioner — or a comparison
across practitioners — to:

- Select a training layer for a new target model and a specific
  downstream question, rather than relying on prior-hypothesis layer
  choices.
- Characterize a trained NLA's recovery point-spread function and blind
  spots across configurations before using it.
- Map "I want to detect X" to "use NLA at layer L, token T, with prompts
  of type P, validated by methods Q."
- Compare NLAs across target models with shared metrics, which is
  currently infeasible.
- Apply consistent multi-method validation discipline so claims based on
  NLA output are not NLA-only.

Downstream applications — pre-deployment
auditing, control-protocol monitoring, alignment evaluations — can use this
methodology to avoid per-paper bespoke evaluation that doesn't generalize or
compare across teams.

## The proposed methodology

Five components, each addressing one of the points above.

**Pre-training characterization (layer selection priors).** Given a
target model and a downstream question, principled guidance on
candidate layer selection drawn from existing mech-interp findings
(SAE feature localization, circuit analysis, probe results) and from
the NLA paper's own observations on layer sensitivity. The output is a
short ranked list of candidate layers to consider rather than a single
hypothesis-driven choice.

**Post-training characterization (phantom-suite, adaptive)**. A
standardized protocol for probing a trained NLA's recovery across
configurations on controlled prompts with known signal content.
Decision-driven and adaptive rather than exhaustive Cartesian sweep
(detailed reasoning in
[`docs/research-notes/sampling-rationale.md`](docs/research-notes/sampling-rationale.md)).
Outputs a full reliability map across configurations — profiles, not a single
pass/fail verdict — so a downstream user sees where the instrument works and where it
doesn't, not only the best config.

**Downstream-application calibration (question → configuration
mapping)**. Given the characterization output and a downstream question,
a recommended (layer, token, prompt-type) configuration with calibration
data on expected reliability. Closes the loop between general
characterization and specific applications.

**Cross-model comparison framework**. Shared evaluation metrics that
allow saying "NLA-A on model X has property P; NLA-B on model Y has
property Q; here's how they compare." Enables the field to do
apples-to-apples comparison.

**Validation discipline (multi-method)**. Standardized protocol for
corroborating NLA findings with independent methods (causal
interventions via AR-derived steering, linear probes for specific
attributes, behavioral consistency checks). Where the downstream
question admits a task-specific causal model, interchange interventions
on subspaces identified by DAS-style methods (cf.
[causalab](https://github.com/goodfire-ai/causalab); Goodfire AI, 2025)
provide a fourth, structurally independent validator — independent in
the sense that it bypasses the NLA pipeline entirely, unlike AR-derived
steering. Ensures NLA-only positives don't drive downstream conclusions.

## Demonstration: NLA characterization for monitor-activation sampling in AI control

To demonstrate the methodology, we'll apply it to AI control protocols where an untrusted monitor reviews an untrusted model's outputs, and the auditor budget includes activation sampling of the monitor itself via NLA.

### The control-protocol motivation

In AI control (Greenblatt, Shlegeris, et al., 2024), one protocol is to use a
weak but trusted auditor to review flagged outputs from a strong but
untrusted monitor - which itself is reviewing a strong but untrusted model. A known
structural weakness: the auditor evaluates the monitor on
its behavior, reflected in its verdicts. If the monitor is colluding, sandbagging, or
otherwise subverting, behavioral inspection may not catch it.

NLA provides a candidate new tool: read the monitor's activation at the
verdict token, surface what it was actually thinking. The methodology
question — "under what configurations is NLA-based monitor inspection
reliable?" — is a characterization the proposed
methodology is designed to answer.

### Experiment setup

- One open model (Gemma-3-27B initially) playing both the untrusted
  model M and the untrusted monitor M', distinguished by system
  prompts and conversation role. Optionally, two different open models
  for trust-asymmetry.
- Trajectories that incentivize monitor failure: collusion conditions
  (M' system prompt shares an objective with M), sandbagging conditions
  (M' is implicitly penalized for flagging), distraction conditions
  (high cognitive load on M').
- Ground truth: I control whether the monitored output is actually
  problematic, so verdict-vs-truth divergence is observable.
- Apply NLA to M' at the verdict token using the configuration the
  methodology's characterization step recommends.
- Score whether NLA-recovered claims about M's cognition correlate with
  monitor-failure ground truth.

### First deliverable: instrument calibration (a standalone replication)

The instrument-calibration step is the project's **first standalone deliverable**, not
merely preparation for the demonstration. Replicating the paper's Language Switching
finding on the released *open* Gemma-3-27B NLA — construct ~20 prompts containing
user-identity cues; apply the NLA at the assistant's first response token; score
recovered claims against planted ground truth, separately for explicit and implicit cues
(implicit-cue recovery meaningfully above chance is the pass) — stands on its own: a
clean replication of an Anthropic finding on an open model. That makes it (a) the
smallest unit that ships under limited or uncertain compute, (b) a candidate output for
the TAIS project, and (c) a legible way for an outside reader — a funder, say — to verify
the capability to do this class of work *before* the larger demonstration exists.

A second preparation step then supports the control demonstration:

- **Detector characterization.** Adaptive (layer × token × signal) characterization on a
  standardized phantom prompt suite, reported as a full reliability map across
  configurations (profiles, not a single pass/fail) — which then informs the
  demonstration's probe choice.

### Controls

The demonstration is sensitive to several confounders that would
produce apparent NLA signal that isn't reading monitor cognition:

- Task content and topic shape M''s representations. _Control_: hold
  task and topic constant across conditions; vary only the monitor-
  failure incentive structure.
- M's output content shapes M''s context. _Control_: pair conditions
  so M's outputs are matched across monitor conditions.
- M''s system prompt itself defines the failure incentive. _Control_:
  hold structural form of the system prompt constant; vary only the
  incentive content.

### Independent validation

Critical for treating the demonstration as evidence:

- **Causal**: edit the NLA explanation to flip M''s apparent cognition,
  reconstruct via AR for a steering vector, apply to M''s activations,
  measure whether M''s verdict changes as predicted.
- **Probe**: train a linear probe on M''s activations for "monitor
  honest vs. compromised" using held-out trajectories with labeled
  ground truth. Compare probe accuracy with NLA recovery.
- **Behavioral**: does M''s verdict-vs-output divergence correlate with
  NLA-recovered monitor cognition? Agreement is corroborating evidence.

### Success criterion

NLA-recovered claims about M''s cognition track the planted monitor-failure
conditions at meaningfully above chance, AND at least one structurally-
independent validator (causal, probe, or behavioral) corroborates. Crucially,
report NLA detection alongside two cheaper baselines — a linear probe on the
same activations and behavioral verdict-vs-output divergence — and state what
the NLA adds: either detection signal beyond those baselines, or a *validated*
(non-confabulated) verbalization they cannot provide. A result where a linear
probe matches NLA detection and the verbalization is not independently validated
does NOT support "NLA-based monitor inspection works" — it shows the signal
exists and a cheaper instrument finds it. Without both independent corroboration
and demonstrated value over baselines, NLA-only positives are not enough.

### Null interpretation

- _Calibration step fails_: instrument broken at this scale; revise
  plan before continuing.
- _Characterization shows uniform noise_: NLA at this scale lacks
  discriminative capacity; same fall-through.
- _Demonstration: NLA null + behavioral null_: M' doesn't represent
  failure conditions in a recoverable way at this scale. The
  methodology has produced a clear negative for this application: NLA-
  based monitor inspection isn't viable at open-model scale.
- _Demonstration: NLA null + behavioral non-null_: M' represents
  failure conditions in some form (verdict-output divergence is real)
  but NLA can't read them. Instrument blind to monitor cognition under
  the tested configurations. Methodology has identified a real
  limitation worth knowing.
- _Demonstration: NLA non-null + behavioral null_: NLA confabulates
  plausible-but-false claims about M''s cognition. The multi-method
  validation discipline has caught what would have been a misleading
  positive result. This is a methodology win even though the
  application would not be supported.

## Cross-model application: capability vs. NLA legibility

The methodology naturally generalizes across the released open NLAs
(Qwen-2.5-7B, Gemma-3-12B, Gemma-3-27B, Llama-3.3-70B). Applied across
this ~10× capability range, the same characterization protocols answer
a structurally separate but safety-relevant question: **as target
models grow more capable, does NLA-based interpretability scale with
them, or does it degrade quietly?** A caveat up front: these models differ in family
and training, not only capability, so the across-model curve confounds capability with
architecture. The cleaner test is the *within-model* capability-stress arm below (it
holds the model fixed); treat the across-family curve as suggestive, not dispositive.

Three possibilities, only one of which is silent:

1. NLA verbalizations stay legible _and_ reconstructively faithful as
   capability scales — interpretability scales with capability.
2. Reconstruction stays faithful (FVE remains high) but legibility
   drops — the verbalizer encodes more compressed, more abstract, or
   potentially steganographic content while the round trip still
   succeeds. _This is the silent failure mode._
3. Both fail (FVE drops, legibility drops) — interpretability tools
   don't scale to the capability level, but at least failure is loud.

Mode 2 is the failure mode that matters for AI control: if the
methodology's instrument-characterization machinery shows that NLA
legibility silently degrades as target model capability rises, and
NLA-based monitor inspection is being used in control protocols at
those capability levels, the audit tool looks like it's working but
isn't. The control-protocol demonstration above gives Mode 2 a
concrete operational stake.

### Cross-model tracking design

- **Across-model legibility curve.** Run the standardized phantom
  suite through each released open NLA. Plot legibility (LLM-graded
  writing quality, paraphrase invariance, entropy / compressibility)
  against FVE and against target-model capability.
- **Within-model under capability-stress conditions.** A single
  target model under conditions that demand more compressed
  representations (longer context, harder tasks, multi-turn
  conversations).
- **Steganography emergence as a function of capability.** Extend the
  paper's paraphrase-invariance methodology across the capability
  range; look for divergence between small-model and large-model
  responses to meaning-preserving transformations.

### What this enables

- **Audit calibration.** Pre-deployment auditing using NLAs needs to
  weight findings by instrument reliability at the target's capability
  level. The legibility-vs-capability curve provides that weighting.
- **Training-time legibility regularization** as a candidate alignment
  intervention if legibility drops with capability.
- **Differential probing** for capabilities that emerge specifically
  with representational opacity.
- **A "are we keeping pace" signal** — quantitative evidence on
  whether interpretability is scaling with capability, which the field
  currently lacks.

## Longer-arc

Two natural deeper directions, both genuinely beyond the current plan:

1. **Model-informed activation tomography.** Where mech-interp findings
   localize features to specific layers or neuron groups, those
   localizations are priors on the NLA's projection geometry. Integrating
   these as constraints on AV training or as priors on the inverse map
   would be the model-informed branch of activation tomography
   (paralleling physics-based reconstruction in medical imaging). Not
   currently instantiated for NLAs; the methodology being developed here
   would be a natural substrate for such extensions. Goodfire's
   [causalab](https://github.com/goodfire-ai/causalab) (Goodfire AI,
   2025) instantiates the broader model-informed paradigm under a
   different substrate — high-level causal models of task computation,
   tested against the network via interchange interventions and subspace
   methods (DAS, DBM, SAE). It is the closest existing analog and a
   natural cross-method validator for the **Validation discipline**
   methodology component above.
2. **Identifiability theory.** Given activations from K agents at L
   layers (or more generally, multiple measurement geometries), what
   aspects of cognition are formally recoverable under the NLA
   bottleneck capacity and projection geometry? Tomography has
   identifiability theorems for the linear case; the NLA analog would
   be the genuinely tomography-derived theoretical contribution.
   Potentially thesis-shaped rather than short-project-shaped.

## Limitations and risks

**Confabulation.** The paper documents that NLAs make verifiably false
claims about input context. The independent-validation discipline in
the proposed methodology is the response to this; it doesn't eliminate
the risk but does enable detection of NLA-only positives.

**Cost.** NLA inference generates ~500 tokens per activation. The
methodology's characterization protocols and the AI-control
demonstration both involve substantial NLA inference budgets. Compute
realism is detailed in the Compute section.

**Single-layer.** The released NLAs read at one fixed layer; the
methodology's adaptive characterization tests application at other
layers, but applying NLA outside its trained layer is itself a noise
source the characterization step has to account for.

**Working with someone else's instrument.** Released NLAs were trained
on a fixed corpus by kitft / Anthropic. Any biases propagate. The
methodology characterizes but does not eliminate these.

**Same-model readout (structural).** The NLA is trained on, and tied to, the activation
space of the very model it reads — it cannot be swapped for a "different-model"
instrument. That tie is double-edged: it is what lets the NLA read this model's
activations at all, and what bounds what the readout can surface. Reading activations
does bypass the behavioral self-report channel (the
point of the tool), but the readout still surfaces only what is *reconstruction-legible*,
not necessarily what is decision-relevant, and it cannot surface what the model
represents opaquely (compressed, superposed, or — at higher capability — steganographic).
This is why downstream conclusions lean on the independent, non-NLA validators
(label-trained probe, causal interventions), which do not share the readout's blind spots.

**Possible overlap with internal Redwood / Apollo / METR work.** The
specific intersection of NLA + AI control + monitor inspection may be
in active internal research at safety labs. A literature check (and
ideally direct outreach to Redwood) before committing to the
demonstration is prudent and is included in immediate next steps.

## Compute and feasibility

**Memory footprint**: Gemma-3-27B at fp16 needs ~50 GB GPU memory; ~30–40
GB with int8. NLA inference loads both AV (full target) and AR
(truncated ~2/3 of layers), so combined footprint is closer to 1.5× the
target. Single H100 (80 GB) suffices; consumer GPUs do not.

**NLA-inference budget** (order of magnitude):

- Calibration + detector characterization:
  ~500–1000 NLA inferences ≈ 250–500 K tokens. Rationale in
  [`docs/research-notes/sampling-rationale.md`](docs/research-notes/sampling-rationale.md).
- AI-control demonstration (~3 monitor-failure conditions × ~100 NLA
  inferences per condition + validation): ~400–600 K tokens.
- Cross-model legibility curve across Qwen-7B, Gemma-12B, Gemma-27B,
  and (compute permitting) Llama-70B: the most resource-intensive
  direction. Estimate ~1–2 M tokens if Llama-70B is included; ~500 K
  if dropped.

Total: ~1.5–3 M tokens of NLA generation, plus
supporting probe-training and rollout costs. Substantially more if
Llama-70B is included.

**Compute access**: currently uncertain. The plan scopes experiments to
fit available access and revises timelines once access is secured.

## Out of scope

- **Training new NLAs from scratch.** ~1.5 days on 2×8 H100 nodes per
  the paper for Gemma-3-27B. Out of scope at current resource level.
- **Frontier-scale target models.** Open NLAs top out at Llama-3.3-70B;
  frontier-scale phenomena will not appear here.
- **Mechanistic grounding within NLA outputs.** NLAs are by
  construction non-mechanistic. Where mechanistic claims matter, the
  validation discipline defers to mechanistic methods rather than
  trying to invent mechanistic NLA variants.
- **Building deployable control protocols.** The methodology
  demonstration tests whether NLA-based monitor inspection is reliable
  enough to be a control-protocol component. Actually building such a
  protocol — efficient inference at scale, integration with auditor
  budgets in real deployments — is downstream engineering, not what
  this plan delivers.

## Immediate next steps

1. **Literature and outreach check** for existing or in-progress work
   at Redwood / Apollo / METR on NLA-in-control-protocols, and at
   Goodfire on causal-abstraction-based interpretability
   ([causalab](https://github.com/goodfire-ai/causalab) is the
   model-informed counterpart to this work — see §Longer-arc item 1).
   Concrete actions: recent arXiv + LessWrong + Alignment Forum search;
   direct outreach to one or two Redwood researchers describing the
   proposed methodology and demonstration, asking whether internal work
   overlaps. Run this before committing significant compute.
2. **Secure compute access** (≥1× H100, 80 GB — consumer GPUs won't run the
   Gemma-3-27B NLA). The gating prerequisite: steps 3–5 cannot run without it, so it is
   sequenced here rather than later.
3. `uv sync` to install dependencies; verify the codebase runs.
4. Load a released NLA checkpoint (Gemma-3-27B AV/AR) and run the smoke-test inference
   path from [`docs/nla_upstream/inference.md`](docs/nla_upstream/inference.md).
5. Ship the **first deliverable** — the instrument-calibration replication (Language
   Switching on identity cues) — then proceed to detector characterization and the
   demonstration.

Document updates here as the work proceeds.

## References

- Fraser-Taliente, K., Kantamneni, S., Ong, E., Mossing, D., Lu, C.,
  Bogdan, P. C., et al. (2026). _Natural Language Autoencoders Produce
  Unsupervised Explanations of LLM Activations_. Transformer Circuits
  Thread. <https://transformer-circuits.pub/2026/nla/index.html>
- Greenblatt, R., Shlegeris, B., Sachan, K., & Roger, F. (2024). _AI
  Control: Improving Safety Despite Intentional Subversion_.
- Bricken, T., Wang, R., Bowman, S. R., Ong, E., Treutlein, J., Wu, J.,
  Hubinger, E., & Marks, S. (2025). _Building and evaluating alignment
  auditing agents_. Anthropic Alignment Science Blog.
- Marks, S., Treutlein, J., Bricken, T., et al. (2025). _Auditing
  language models for hidden objectives_. arXiv preprint
  arXiv:2503.10965.
- Goodfire AI. (2025). _causalab: Causal abstraction for mechanistic
  interpretability_ [Computer software]. GitHub.
  <https://github.com/goodfire-ai/causalab>

---

_Author: [Monica Spisar](https://monicaspisar.com), independent researcher
([ORCID 0009-0006-1719-4798](https://orcid.org/0009-0006-1719-4798))._
