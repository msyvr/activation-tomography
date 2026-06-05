# First deliverable — implementation checklist

> _Working plan (living). The standalone **validate + transfer** deliverable on a released open NLA —
> the project's first deliverable per [`../../RESEARCH.md`](../../RESEARCH.md). Step-by-step bring-up,
> compute, and time/cost ranges, grounded in
> [`../nla_upstream/inference.md`](../nla_upstream/inference.md) and
> [`../nla_upstream/setup.md`](../nla_upstream/setup.md)._

## Scope

**Validate + transfer** on a released open NLA — *not* a replication of the paper's headline findings,
which open weights do not allow. NLAs are welded to one model (the AV is *initialized as* the target
and reads its own residual stream); the Language Switching finding and the quantitative eval suite were
produced on *closed* models (Opus 4.6, the Haikus). The open NLAs are separate artifacts whose
published, reproducible number is reconstruction fidelity (~70–75% FVE).

- **Validate (guaranteed anchor):** reproduce the open NLA's **FVE (~70–75%)** — load AV + AR, run a
  held-out activation set through the round trip, confirm reconstruction fidelity matches. Instrument-
  intrinsic, scale-robust, ships regardless.
- **Transfer (legible layer):** **latent-content recovery** — the AV verbalising salient content
  carried by an *injected* activation that isn't in its prompt (the read-the-internal-state primitive
  oversight depends on). Content chosen as far up the safety-resonance axis as smoke-testing supports:
  **generic** concept recovery first (guaranteed by the released `examples/` decodes); **refusal /
  harm-state** recovery as the stretch (salient, scale-robust direction — but a *novel* probe, so
  smoke-test it).

Goal = a *reliable, legible ability signal*, so **P(clean positive) dominates**. The open NLAs are
weak, so subtle-representation / behavioural classes (implicit user-identity, sandbagging, CoT-hint
use) are deliberately out — high null risk; they belong to the project's safety arc, not a competence
signal. Safety relevance here is free at the *capability* level (reading latent internal content), with
the refusal stretch adding *content*-level resonance.

## Target-model decision (this moves all the numbers)

`RESEARCH.md` names Gemma-3-27B. The docs make the friction explicit; for a fast, clean signal it's
worth choosing deliberately:

| | Qwen-2.5-7B @ L20 | Gemma-3-27B @ L41 |
|---|---|---|
| HF gating | ungated | **gated** (accept license, `HF_TOKEN`) |
| SGLang patch | none (plain causal LM) | **mm-wrapper bypass patch required** (else `input_embeds` is silently dropped → `\n\n\n`) |
| backend flags | stock | `--attention-backend fa3` (flashinfer OOMs on `head_dim=256`) |
| GPU | 24 GB (4090 / L40S) | 80 GB (H100) |
| `setup.md` verdict | **"recommended starting point"** | larger-model signal |

**Recommendation:** smoke-test the pipeline on **Qwen-2.5-7B** first (lowest friction, proves injection
+ the round trip work), then run the headline deliverable on **Gemma-3-27B** if the larger-model signal
is wanted — or stay on Qwen for minimum time-to-result.

## Checklist

### Phase 0 — provision + deps (inference-only path)
- [ ] Rent pod — RunPod H100 80 GB (Gemma) or a 24 GB card (Qwen). **Both AV and AR** are needed now
  (the AR carries the FVE anchor) → ~1.5× target footprint; still fits 80 GB for 27B.
- [ ] `uv pip install torch transformers safetensors httpx orjson pyyaml numpy` + `sglang[all]>=0.5.6`
  — ⚠️ pin `torch<2.11` *or* use the cu124 index (unpinned cu130 conflicts with `sgl-kernel`'s cu12 wheels)
- [ ] HF auth + accept the Gemma license (Gemma only); download the **AV + AR** checkpoints

### Phase 1 — bring-up + smoke-test ⚠️ *highest-variance step*
- [ ] (Gemma) apply `patches/apply_sglang_patches.sh` for the mm-wrapper bypass
- [ ] Launch the SGLang AV server (`--disable-radix-cache` mandatory; Gemma: `--attention-backend fa3`)
- [ ] Load the AR (truncated backbone + `value_head.safetensors`)
- [ ] **AV smoke-test:** decode a known vector → eyeball English vs CJK soup; if CJK, walk the Debugging
  list (`injection_scale`, Gemma `embed_scale` = √d, double-BOS, template drift, embeds-only)
- [ ] **AR smoke-test:** round-trip a known activation → cos / MSE in the expected band (cos ≈ 0.9 good)

### Phase 2 — experiment design (pin before pod time)
- [ ] **FVE protocol:** assemble a held-out activation set from a distribution *comparable to the
  paper's* (UltraFineWeb / WildChat-like), and fix the FVE / MSE / cos definition you'll report.
  ⚠️ FVE is **distribution-dependent** — to land at ~70–75% you must eval on a comparable distribution,
  not on the recovery-probe prompts.
- [ ] **Latent-content recovery:** curate injected activations with known salient content — generic
  concepts (guaranteed), plus harmful-context activations for the refusal stretch — and define the
  scoring rubric (does the verbalisation capture the content?) + the baseline. **Pre-register both.**

### Phase 3 — run + score
- [ ] Compute FVE on the held-out set; confirm ~70–75% (the validate anchor)
- [ ] Run latent-content recovery; score capture rate vs baseline — **generic first**, then the refusal
  stretch
- [ ] *(optional)* note per-(layer, token) reliability where useful for the later characterization step

### Phase 4 — analysis + writeup
- [ ] FVE match + content-recovery rates + the framing (capability-level safety relevance; refusal as
  the content-level stretch); one figure; short standalone report

## Compute / time / cost (ranges)

- **Compute is trivial.** FVE on a few hundred held-out activations + a few dozen recovery decodes ≈
  minutes of GPU. The GPU is for *capacity* (fitting a 27B AV **and** AR), not throughput. **1× H100
  80 GB** (Gemma) or **1× 24 GB card** (Qwen).
- **Person-time: ~3–7 focused days**, wall-clock **~1–2 weeks** with iteration. Range driven by Phase 1
  (clean decode + round trip in half a day if it "just works"; 1–2 days if injection-debugging is needed).
- **GPU cost: ~$30–90** (Gemma-27B H100 @ ~$2.89/hr, ~10–30 pod-hours with disciplined shutdown) or
  **~$10–30** (Qwen-7B on a $0.69–0.86/hr card). Compute is *not* the binding cost — time is.

| Phase | Person-time | GPU |
|---|---|---|
| 0 — provision + deps | 0.5–1 d | idle-ish |
| 1 — bring-up + smoke-test ⚠️ | 0.5–2 d | active, low util |
| 2 — experiment design | 0.5–1 d | none |
| 3 — run + score | 0.5–1 d | minutes of generation |
| 4 — analysis + writeup | 1–2 d | none |

## Named risks (mostly plumbing, front-loaded into Phases 0–1)

All documented, so all nameable in advance:
- SGLang mm-wrapper silently drops `input_embeds` on Gemma-3 (→ `\n\n\n`) without the bypass patch
- torch/SGLang CUDA-pin conflict (cu130 vs cu12)
- HF gating delay on Gemma
- injection-failure debugging (scale / `embed_scale` / BOS / template)
- **FVE distribution mismatch** — eval on a non-comparable activation set won't reproduce ~70–75%
- **the refusal stretch is a *novel* probe** — not paper-validated; smoke-test it, and keep generic
  recovery + FVE as the floor so a weak refusal result doesn't sink the deliverable

The research risk on the *anchor* (FVE) is ~zero; the failure mode is time sunk in bring-up (why Phase 1
is flagged and Qwen-first is recommended) and over-reaching on the refusal stretch.

## Pin before any pod time ($0, and the difference between a result and vibes)

- the **FVE protocol** (held-out distribution + metric definition)
- the **latent-content recovery rubric** + baseline

## Verify against the paper / release

- Confirm the exact **FVE definition** and the **held-out data** the open-model ~70–75% number was
  measured on, so the reproduction is comparable.
- Check whether any **per-open-model eval** (e.g. User Modeling) was reported in the full paper's
  quantitative section or the HF model cards — if so, it could upgrade the legible layer beyond generic
  recovery.
