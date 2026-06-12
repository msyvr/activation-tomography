# Adversarial characterization: the evasion tax

> _Research note (living). Forward-looking framing for the adversarial extension of the NLA
> characterization methodology. Companion to [`../../RESEARCH.md`](../../RESEARCH.md)._

## The flank this addresses

The control-protocol demonstration in `RESEARCH.md` reads an untrusted monitor M' whose collusion
is *induced by a system prompt*. Ground truth is the imposed condition, and M' is not optimizing to
defeat the reader. That makes the result **auditing-grade** — evidence that the internals signal is
present and readable under non-adversarial conditions — while wearing a **control** label. The
distinction matters because control is *defined* by a property auditing does not require:

- **Auditing** asks: when property P is present, do my tools surface it?
- **Control** asks: does the safety property hold *even while the subject optimizes against the
  check* — including optimizing its internal representations to fool an internals reader?

The axis between them is **adversarial-optimization pressure on the detector**. The demonstration
sits at the zero-pressure end. The plan can either *scope* that explicitly (done — see RESEARCH.md
§Threat-model scope) or *instrument* it. Instrumenting it is this note.

## The reframe: from wall to surface

Adversarial robustness is usually treated as the wall that kills internals-based monitoring for
control: if the monitor can hide its cognition, the readout is worthless. Reframe it as a
measurement. For each config (layer ℓ, token t), ask:

> How much task performance must an adversarial M' sacrifice to look benign to the reader at this
> config — the **evasion tax**?

The output is an **evasion-robustness surface across configs**, not a single pass/fail: where are
the model's task computation and the read signal entangled enough that evasion carries a cost?

*Config caveat (released, single-layer NLAs).* We use the released NLAs, not ones we train, and each
reads at **one fixed layer**. So the surface is *dense over token position and signal type at that
layer* and **sparse, confounded over layer**: applying an NLA off its trained layer is
out-of-distribution and is measured as a degradation/noise source, not a clean reading, and the only
other layer points come from the four released NLAs — each at a different layer *and* a different
model (layer confounded with capability). A free layer axis would require *training* NLAs (out of
scope). Read every "(layer, token)" below with that in mind.

## The adversary's trilemma (why a high-tax config squeezes the option set)

At a config where the read signal is load-bearing for competent monitoring, M' faces three moves,
all bad:

1. **Don't evade** → the reader surfaces the collusion. (Given the reader is reliable here under
   non-adversarial conditions — which passive characterization establishes.)
2. **Evade by scrubbing the read signal** → doing so corrupts computation M' needs, so verdict
   quality drops → a **behavioral audit catches the degradation**. Closed *iff* the tax exceeds the
   slack the behavioral checks can actually *resolve* — not just nominal slack, but enough that the
   behavioral monitor has the statistical power to detect an X% drop.
3. **Compute the load-bearing part where the reader isn't looking** → the escape hatch. With the
   released *single-layer* NLAs this splits, and the cheap form dominates: **(3a) relocation** — move
   the collusion-relevant computation to a layer or token the fixed reader doesn't see (cheap, because
   transformer computation is redundant and distributed; a one-layer reader cannot rule it out);
   **(3b) competent-but-unreadable encoding** at the read config itself — steganography / superposition
   (the hard, exotic escape). 3a is the residual risk that actually bites with released readers, and it
   is why the *negative* result below is confounded.

A true "no winning move" needs **both** tax > detectable-slack **and** arm 3 empty at this config.
So the deliverable is concrete:

> *"At config (ℓ, t), evasion costs ≥ X% task performance against red-team R, and no free competent
> encoding was found within R's search."*

Note the framing: a **lower bound against a named red-team R**, not an existence claim. Arm-3
emptiness is an unbounded search — only as strong as R. The tax (arm 2) is the clean number; arm-3
is the soft one.

## Worth doing in both directions

- **A positive** sizes a real control squeeze: X is directly comparable to the slack the protocol's
  behavioral and statistical checks tolerate — a number that lives on *both* sides of the control
  ledger (control is accounting: safety = the adversary has no move that achieves its goal and stays
  inside what the checks tolerate).
- **A negative is confounded by the single-layer instrument — state it as a bound, not a verdict.**
  "No high-tax config" cannot separate *internals monitoring of an untrusted monitor is structurally
  fragile* (the tempting claim) from *a single-layer reader is cheaply evaded by relocation* (arm 3a —
  near-tautological, not a finding about internals monitoring writ large). A flat surface yields only a
  **lower bound**: evasion at the readable layer costs ≤ X against R. Upgrading it to a verdict on
  internals monitoring in general would need enough layers read to foreclose relocation — i.e. training
  NLAs (out of scope). The clean-fragility verdict is **not** on the menu with released single-layer
  NLAs; do not pitch it as one.

## The tax is a behavioral measurement

The tax is M''s task-performance cost under forced evasion — a behavioral quantity. It does **not**
require trusting the verbalization, which lifts weight off the validation long-pole. It even
*operationalizes* entanglement: free evasion ⇒ the read signal was not load-bearing; costly evasion
⇒ it was. (The reader's non-adversarial-condition reliability — arm 1 — still rests on the
independent validators: label-trained probe, DAS-interchange.)

## The tax needs its own resolution floor (before any tax is trusted)

The tax is a difference in M''s monitoring performance (verdict accuracy on a flag-the-bad-output task)
between an evade condition and an honest one — a difference of two task-clustered proportions. So it
inherits the phantom discipline: **report the smallest tax the design can resolve before reporting a
tax.** Sketch, to size the demo (p ≈ monitor accuracy, δ = tax, design effect D = 1 + (m−1)·ICC):

> N per condition ≈ (z_α + z_β)² · 2p(1−p) / δ² · D.
> At p = 0.7, D ≈ 1.5, two-sided α = 0.05, power 0.8: resolving δ = 0.10 needs **≈ 500 scored verdicts
> per condition** — far above the demo's planned ~100. At N ≈ 100 the design resolves only δ ≳ **0.22**;
> moderate taxes (the decision-relevant regime — cheap enough to matter, not free) sit **below the
> floor** and read as null.

So: fix a **minimum interesting tax (MID)** tied to the behavioral audit's *detectable* slack (arm 2
above — the tax only matters if it clears what the behavioral checks can resolve), compute the N that
resolves it, and report the achieved floor alongside every tax. A tax without its floor is exactly the
error the phantom suite exists to prevent.

## Two adversary strengths (the scope fork)

- **Prompted adversary (tax-v0).** Prompt M' to collude while looking benign to the known reader;
  measure the performance hit. Cheap, ships under compute uncertainty. **Validity caveat — the raw
  drop is not the tax.** A drop under "do your job *and* satisfy this extra constraint" is confounded
  with the generic cost of *any* hard dual objective, independent of read-signal entanglement. The tax
  is the **excess** drop over a *matched-load control*: a second condition giving M' a dual objective of
  comparable complexity that does **not** target the reader (e.g. "produce your verdict *and* append a
  structured rationale in a fixed schema"). tax-v0 ≔ (drop under read-evasion) − (drop under
  matched-load); only the excess is attributable to evasion. Without the control, tax-v0 is a number,
  not a measurement — and even with it, a prompted adversary is weak, so a near-zero tax-v0 bounds, it
  does not establish.
- **Trained adversary (the flagship follow-on).** Fine-tune M' to evade the reader (cf. Neural
  Chameleons, which shows fine-tuned models zero-shot-evade *unseen* activation monitors). Heavier —
  not for GPU cost (LoRA-on-27B is feasible on a rented H100) but because building a strong-enough
  adversary is real methodological work; a weak adversary yields a misleading tax.

Both measure **assuming the adversary knows the reader's config** — hiding it is
security-through-obscurity and just returns us to auditing-grade. The tax is control-relevant
precisely because it is paid even when the adversary knows exactly where you read.

## Capability scaling: the adversarial twin of Mode 2 (suggestive only)

`RESEARCH.md`'s Mode 2 tracks whether *passive* legibility silently degrades as capability rises; the
adversarial twin would track whether *evasion gets cheaper* — run the tax across the released open-NLA
ladder and ask whether high-tax configs **erode**. **State the confound plainly: this is four points
(Qwen-7B, Gemma-12B/27B, Llama-70B), each a different model family, NLA, and trained read-layer, so
"capability" is entangled with architecture and read-layer.** Four points varying three things at once
cannot support "evasion gets cheaper as capability rises" — the cross-family curve is **suggestive, not
dispositive**, and must not be reported as a clean scaling result. The defensible test is the
**within-model** capability-stress arm (one model, harder/longer conditions) — a *proxy* for
capability, not capability scaling, and it does not yield the cross-model curve. From this instrument
set we get the clean inference *or* the cross-model story, not both; the honest deliverable is the
within-model arm plus a clearly-flagged 4-point suggestion.

## Why a different-base reader does not fix this (two trust axes)

It is tempting to break the same-model tie by reading M' with an NLA on a *different* base. Split the
concern:

- **(A) Independence of failure modes.** A same-base reader shares M''s training and blind spots (a
  confabulation tendency in M' recurs in the reader). A different base helps — less-correlated
  failures — and is arguably the better design even for the non-adversarial use.
- **(B) Robustness under adversarial optimization** (control-critical). The activations are still
  M''s, and M' controls them; if M' emits activations that verbalize as benign while colluding, the
  reader's lineage is irrelevant. **(B) is not fixed by changing the base** — the locus of subversion
  is upstream of the reader.

There is also a **mechanical blocker**: an NLA's verbalizer is initialized *as the target model* and
reads its own residual stream via injection, so M''s residual stream cannot literally be fed to a
base-B NLA (different, unaligned spaces). Bridging needs a learned cross-model map fit on M''s
activations — re-importing the untrusted-derived machinery the swap was meant to remove, and it
aligns *natural* features best, *strategic* ones worst. **Upshot:** put independence in the
*validators*, not the NLA's base.

## Corollary uses

- **Probe placement.** Spend a deployed activation-inspection budget where lying is most expensive;
  raises the non-adaptive-adversary baseline and forces a committed adversary to pay X.
- **Trust-weighting.** A positive from a high-tax config — obtained where M' had both incentive and
  capability to evade — deserves more weight than one from a cheaply-scrubbable config. An adversarial
  reliability dimension on top of passive accuracy.

## Training-time use, and its Goodhart hazard

The tax map makes *legibility regularization* targeted (keep the load-bearing computation entangled
and legible) — but this is the most double-edged use: optimizing *toward* legibility at a config is
how you train a model to *look* legible there while relocating the real computation (Goodharting your
own instrument). Treat it as **"monitor for entanglement loss,"** not "optimize to maintain
entanglement."

## Where the tomography analogy genuinely extends

A medical phantom does not fight the scanner; here the subject does. Characterizing an instrument
against an *adversarial subject* is the part of the imaging analogy that *extends* rather than merely
transfers — and it is the actual contribution of this extension.

## Open scope decision

- **(i) Light-scope-in (recommended):** add a *prompted* tax-v0 arm to the reliability map now; name
  the trained-adversary + ledger + erosion program as the flagship follow-on, specified precisely
  enough to stake priority.
- **(ii) Clean separation:** keep the current project strictly non-adversarial + scoped; spin the
  whole tax program as a separate proposal.

Either way, the explicit **non-adversarial scope sentence** in the demonstration goes in regardless,
and the **literature/outreach check** (Redwood / Apollo / METR) should ask specifically about
obfuscation-*cost/tax* measurement — not just evasion existence — before committing to the trained
arm.

## References

- McGuinness, M., Serrano, A., Bailey, L., & Emmons, S. _Neural Chameleons: Language Models Can Learn
  to Hide Their Thoughts from Unseen Activation Monitors_. arXiv:2512.11949.
- Greenblatt, R., Shlegeris, B., Sachan, K., & Roger, F. (2024). _AI Control: Improving Safety Despite
  Intentional Subversion_.
- Storf, S., Barton-Cooper, R., Peters-Gill, J., & Hobbhahn, M. (2026). _Constitutional Black-Box
  Monitoring for Scheming in LLM Agents_. arXiv:2603.00829.
