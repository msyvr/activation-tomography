# Research direction: activation tomography

> _Living document_

_This research is motivated by AI safety and alignment: NLAs are being adopted for safety-critical monitoring (pre-deployment auditing already; proposed for AI control) faster than their failure modes are characterized. The technical goal is a systematic methodology for characterizing, configuring, and validating Natural Language Autoencoders (NLAs) as measurement instruments — the prerequisite the field skips. The two near-term deliverables apply it on a released reader: a **reliability map** (where it reads faithfully vs confabulates) and a **silent-legibility probe** (does verbalization quietly degrade under representational stress while reconstruction holds — the audit-tool-looks-fine-but-isn't failure mode). The adversarial axis that defines AI control — does a readout survive a monitor optimizing to evade it — is the named follow-on, the **evasion tax**, scoped as a single-layer lower bound (see [`docs/research-notes/evasion-tax.md`](docs/research-notes/evasion-tax.md)). This characterization is upstream of, and complementary to, the adversarial-robustness work at Redwood / on Neural Chameleons — not in competition with it._

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
steering. A no-activation logit monitor (Aranguri 2026) is a fifth
candidate — the cheapest and most structurally distinct, reading the
model's output distribution and touching no activations — but it
corroborates only in the non-opaque regime: a concept represented too
opaquely to verbalize will neither lift a forced sentence's probability
nor stay NLA-legible, so the two go blind together in exactly the Mode-2 /
steganographic case the silent-legibility work targets. There the
label-trained probe, reading linearly-decodable-but-unverbalizable
structure directly, is the independent validator — not the logit monitor.
Ensures NLA-only positives don't drive downstream conclusions.

## Grant-period deliverables: two powered experiments (the headline)

The methodology's two near-term deliverables are the **reliability map** and the **within-model
silent-legibility probe** — both feasible on one released NLA (Gemma-3-27B, single H100), both with a
**negative control that must fail** so a positive is non-vacuous. The control-protocol demonstration
(§Demonstration) and the evasion tax (§Adversarial extension) are the **stretch / follow-on**, built
once the instrument is characterized. Effect sizes below *size* the work; a day-1 mini-run fixes the
real base rate and task-clustering before N is set (cf. the PoF-E Stage-0 calibration).

**Deliverable 1 — reliability map (recovery PSF + blind-spot map).** *Design:* the phantom-suite
characterization (§Demonstration → First deliverable, and §Detector characterization), scored per
(token × signal-type × off-layer) cell for recovery of *known* content, with a **signal-absent
negative control** giving each cell's false-positive rate — a blind spot is low true-recovery, a
confabulator is high false-positive, both findings. Multi-method validation (label-trained probe +
behavioral + AR-steering subset); the bar is *beat a same-activation probe or deliver a validated
verbalization it can't*. *Power:* per-cell recovery is a proportion p, design effect D = 1+(m−1)·ICC,
so N = z²·p(1−p)/w²·D ⇒ **≈ 125 / cell** for ±10% at p = 0.5; a coarse blind-spot screen needs
**~40 / cell**. Tiered: coarse-40 across ~55 cells (native dense + off-layer sparse) → top-up to ~130
on boundary cells ≈ **3,800 AV inferences**. *Compute:* ≈ **2.5 M** NLA-generation tokens (incl. the
FVE round-trip) → a few GPU-hours.

**Deliverable 2 — within-model silent-legibility degradation (clean Mode 2).** *Design:* hold the
model fixed; stress representations {baseline, long-context, hard-task, multi-turn,
compression-pressure}; per condition measure **FVE** *and* **legibility** (LLM-graded quality,
paraphrase-invariance, compressibility). Silent failure = legibility slope < 0 while FVE slope ≈ 0.
Within-model **by design** — the cross-family curve (§Cross-model) confounds capability with
architecture and read-layer and is suggestive only; FVE-holds is the control that makes a legibility
drop *silent* rather than loud. *Power:* legibility is continuous, N/condition = 2(z_α+z_β)²/d² ⇒
**≈ 63** (d = 0.5) / **≈ 174** (d = 0.3). The headline is an **interaction** (legibility drops more
than FVE) — pre-registered as a descriptive slope-vs-slope trend unless powered to ≥ 150/condition;
Holm across legibility metrics. *Compute:* ≈ **1 M** NLA-generation tokens → ~1.5–3 GPU-hours.

Grant-period compute for both: ≈ **3.5 M** NLA tokens on one H100 — well within a small
rapid/credits budget; bring-up (residual-stream injection + the sglang patches) and investigator time
are the binding cost, and the literature/outreach check (§Immediate next steps) gates the follow-on
and runs first. Full powered + costed plan, including the evasion-tax follow-on, is the source note
this section excerpts.

## Demonstration: NLA characterization for monitor-activation sampling in AI control

_(Stretch / follow-on — the control application built on the characterized instrument from
§Grant-period deliverables.)_ To demonstrate the methodology, we'll apply it to AI control protocols where an untrusted monitor reviews an untrusted model's outputs, and the auditor budget includes activation sampling of the monitor itself via NLA.

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

### Threat-model scope (auditing-grade vs. control-grade)

One distinction governs how to read this demonstration. *Auditing* asks whether a property is
detectable when it is present; *control* — the discipline this borrows its language from — asks
whether a safety property holds **even while the subject optimizes against the check**, including
shaping its internal representations to fool an internals reader. The experiment below induces M''s
collusion with a system prompt and reads it: ground truth is the *imposed condition*, and M' is
**not** optimizing its activations to evade the NLA. That makes the result **auditing-grade** —
evidence that the internals signal is present and readable under non-adversarial conditions. It is
**not** yet control-grade, because the defining control question — does the readout survive a monitor
that *optimizes to evade it* — is not instantiated here.

This is a deliberate scope boundary, not an oversight: characterizing the instrument under
non-adversarial conditions is the prerequisite, and the adversarial axis is addressed separately as
the **evasion-tax extension** (below; full framing in
[`docs/research-notes/evasion-tax.md`](docs/research-notes/evasion-tax.md)). Stated plainly so the
control framing is not over-read: *a positive here shows the NLA can read induced collusion — not
that it catches a monitor actively hiding collusion from it.*

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

### First deliverable: instrument validation + a latent-content transfer demo

The first standalone deliverable **validates the released open instrument and demonstrates its core
capability** — **validate + transfer**, shaped to maximise the probability of a clean, legible, positive
result on a weak open instrument:

- **Validate (guaranteed anchor).** Reproduce the open NLA's published FVE (~70–75%): load AV + AR, run
  a held-out activation set through the round trip, confirm fidelity matches. Instrument-intrinsic and
  scale-robust — it ships regardless of what the target represents.
- **Transfer (legible layer).** Latent-content recovery: the AV verbalising salient content carried by
  an *injected* activation that is not in its prompt — the read-the-internal-state primitive that
  internals-based oversight depends on. Content is chosen as far up the safety-resonance axis as
  smoke-testing supports: *generic* concept recovery first (guaranteed by the released `examples/`
  decodes), *refusal / harm-state* recovery as the stretch.

The goal is a *reliable, legible ability signal*, so probability of a clean positive dominates; the
open NLAs are weak, so subtle-representation classes (implicit user-identity, sandbagging, CoT-hint
use) carry high null risk and are deliberately out here — they belong to the project's safety arc, not
a competence-signal first deliverable. Safety relevance comes for free at the *capability* level
(reading latent internal content), with the refusal stretch adding *content*-level resonance. This is
the smallest unit that ships under uncertain compute, a candidate TAIS output, and a legible way for an
outside reader — a funder, say — to verify the capability to do this class of work *before* the larger
demonstration exists. Bring-up, compute, and time/cost ranges are in
[`docs/research-notes/first-deliverable-checklist.md`](docs/research-notes/first-deliverable-checklist.md).

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
report NLA detection alongside three cheaper baselines — a linear probe on the
same activations, behavioral verdict-vs-output divergence, and a no-activation
logit monitor (token-force a known collusion-/eval-aware sentence, read its
probability; Aranguri 2026) — and state what the NLA adds: either detection
signal beyond those baselines, or a *validated* (non-confabulated) verbalization
they cannot provide. The logit monitor is the cheapest of the three (no
activations, no training) but needs a *named* target, so it bites only for
readily-verbalizable conditions; where M''s collusion is too opaque to lift a
forced sentence's probability it goes blind — usefully narrowing the NLA's
distinctive value to that opaque regime, the one the same-activation probe and
the NLA actually contest. A result where a linear
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

**Adversarial twin of Mode 2 (suggestive only).** Mode 2 tracks whether *passive* legibility silently
degrades as capability rises; its adversarial counterpart would track whether *evasion gets cheaper* —
run the evasion-tax (see §Adversarial extension) across this same ladder and ask whether high-tax
configs **erode**. But the same confound that weakens the passive curve binds harder here: the ladder
is four points, each a different family, NLA, and read-layer, so "capability" is entangled with
architecture and read-layer. Four triply-confounded points cannot support a clean "evasion gets cheaper
with capability" claim — the cross-family curve is **suggestive, not dispositive**. The defensible
version is the *within-model* capability-stress arm (a proxy for capability, not capability scaling);
the cross-model curve is a flagged suggestion, not a result.

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

## Adversarial extension: measuring the evasion tax

The demonstration above is scoped to non-adversarial conditions (§Threat-model scope). The
control-grade question — *does an internals readout survive a monitor optimizing to evade it?* — need
not be a yes/no wall; it can be a measurement. Reframe adversarial robustness as a **surface**: for
each config (layer, token), how much task performance must an adversarial M' sacrifice to look benign
to the reader — the **evasion tax**? (Token-dense, layer-sparse with the released single-layer
NLAs — see *Limitations → Single-layer*; a free layer axis would require training NLAs.)

- **Decision-relevant — but asymmetrically, given single-layer readers.** A high-tax config squeezes
  the adversary's option set (be read, or pay a measurable performance cost a behavioral audit can
  catch). A *negative*, though, is **confounded**: with a fixed-layer reader, "no high-tax config"
  cannot separate *internals monitoring is fragile* from *a one-layer reader is cheaply evaded by
  relocating the computation* — so a flat surface yields a single-layer **lower bound**, not the clean
  fragility verdict. Upgrading the negative would require multi-layer reading (training NLAs, out of
  scope). See [`docs/research-notes/evasion-tax.md`](docs/research-notes/evasion-tax.md).
- **It is a behavioral measurement.** The tax is M''s task-performance cost under forced evasion — it
  does not depend on trusting the verbalization, which lifts weight off the validation long-pole. (The
  reader's non-adversarial-condition reliability still rests on the independent validators.)
- **Two adversary strengths.** A *prompted* adversary (tax-v0) is cheap and ships under compute
  uncertainty; a *trained* adversary (cf. Neural Chameleons) is the heavier, methodologically harder
  version the flagship follow-on targets. Either way the deliverable is a **lower bound against a named
  red-team R**: *"evasion costs ≥ X% against R; no free competent encoding found within R's search"* —
  not an existence claim.
- **Capability scaling.** Tracking the tax surface across the open-NLA ladder is the adversarial twin
  of Mode 2: does evasion get cheaper as capability rises?

Full framing — the adversary's trilemma, the control-ledger accounting, the lower-bound discipline,
and the v0-vs-trained-adversary distinction — is in
[`docs/research-notes/evasion-tax.md`](docs/research-notes/evasion-tax.md). This extension is named
here as the project's primary adversarial follow-on; the passive characterization and the first
deliverable do not depend on it.

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

*Two trust axes, only one of which a different base would help.* It is tempting to fix the same-model
tie by reading M' with an NLA built on a *different* base. Split the concern. **(A) Independence of
failure modes** — a same-base reader shares M''s training and blind spots, so a confabulation
tendency in M' plausibly recurs in the reader; a different base helps here (less-correlated failures),
and is arguably the better design even for the non-adversarial use. **(B) Robustness under adversarial
optimization** — the activations being read are still M''s, and M' controls them; if M' learns to emit
activations that verbalize as benign while colluding, the reader's lineage is irrelevant (Neural
Chameleons evades *unseen* monitors). So (B) — the control-critical axis — is **not** fixed by changing
the base; the locus of subversion is upstream of the reader. There is also a mechanical blocker: an
NLA's verbalizer is *initialized as the target model* and reads its own residual stream via injection,
so M''s residual stream cannot literally be fed to a base-B NLA (different, unaligned spaces); bridging
would need a learned cross-model map that must itself be fit on M''s activations — re-importing the
untrusted-derived machinery the swap was meant to remove. Put the *independence* in the **validators**
(label-trained probe, DAS-interchange), not in the NLA's base.

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
- **The trained-adversary evasion tax at full scale.** The demonstration is non-adversarial by
  construction (§Threat-model scope); the evasion-tax extension frames and begins to measure
  adversarial robustness, but its *trained-adversary* form — fine-tuning M' to evade across the
  capability ladder, à la Neural Chameleons — is the larger follow-on, scoped beyond this plan's first
  results.

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
5. Ship the **first deliverable** — instrument validation (reproduce the open NLA's FVE)
   plus the latent-content recovery demo — then proceed to detector characterization and
   the demonstration.

Document updates here as the work proceeds.

## References

- Aranguri, S. (2026). _Logits as a new monitor for evaluation
  awareness_. LessWrong / Alignment Forum (Goodfire Research).
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
- McGuinness, M., Serrano, A., Bailey, L., & Emmons, S. _Neural
  Chameleons: Language Models Can Learn to Hide Their Thoughts from
  Unseen Activation Monitors_. arXiv:2512.11949.

---

_Author: [Monica Spisar](https://monicaspisar.com), independent researcher
([ORCID 0009-0006-1719-4798](https://orcid.org/0009-0006-1719-4798))._
