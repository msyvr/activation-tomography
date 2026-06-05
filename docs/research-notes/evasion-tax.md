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
3. **Find a competent-but-unreadable encoding** → the escape hatch (steganography / superposition).
   The residual risk.

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
- **A negative** — no high-tax config anywhere M' actually computes — is a clean, currently
  *unmeasured* verdict that internals monitoring of an untrusted monitor is structurally fragile, and
  the field should not lean on it for control.

## The tax is a behavioral measurement

The tax is M''s task-performance cost under forced evasion — a behavioral quantity. It does **not**
require trusting the verbalization, which lifts weight off the validation long-pole. It even
*operationalizes* entanglement: free evasion ⇒ the read signal was not load-bearing; costly evasion
⇒ it was. (The reader's non-adversarial-condition reliability — arm 1 — still rests on the
independent validators: label-trained probe, DAS-interchange.)

## Two adversary strengths (the scope fork)

- **Prompted adversary (tax-v0).** Prompt M' to collude while looking benign to the known reader;
  measure the performance hit. Cheap, ships under compute uncertainty, weak adversary → a weak/low
  tax. A reasonable first arm on the reliability map.
- **Trained adversary (the flagship follow-on).** Fine-tune M' to evade the reader (cf. Neural
  Chameleons, which shows fine-tuned models zero-shot-evade *unseen* activation monitors). Heavier —
  not for GPU cost (LoRA-on-27B is feasible on a rented H100) but because building a strong-enough
  adversary is real methodological work; a weak adversary yields a misleading tax.

Both measure **assuming the adversary knows the reader's config** — hiding it is
security-through-obscurity and just returns us to auditing-grade. The tax is control-relevant
precisely because it is paid even when the adversary knows exactly where you read.

## Capability scaling: the adversarial twin of Mode 2

`RESEARCH.md`'s Mode 2 tracks whether *passive* legibility silently degrades as capability rises. The
adversarial twin tracks whether *evasion gets cheaper*: run the tax measurement across the released
open-NLA capability ladder and ask whether high-tax configs **erode**. Eroding tax is the adversarial
early-warning that internals monitoring is losing its grip at the frontier — the most
decision-relevant cross-model signal the project can produce, and the least scoopable (gated on the
open-NLA-ladder artifact plus a longitudinal sweep nobody has set up).

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
