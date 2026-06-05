# First deliverable — implementation checklist

> _Working plan (living). The standalone Language-Switching replication on an open NLA — the
> project's first deliverable per [`../../RESEARCH.md`](../../RESEARCH.md). Step-by-step bring-up,
> compute, and time/cost ranges, grounded in
> [`../nla_upstream/inference.md`](../nla_upstream/inference.md) and
> [`../nla_upstream/setup.md`](../nla_upstream/setup.md)._

## Scope

Replicate the paper's **Language Switching** finding on a *released open* NLA: construct ~20 prompts
with user-identity cues, apply the NLA at the assistant's first response token, score recovered
claims against planted ground truth, separately for **explicit** and **implicit** cues. Pass =
implicit-cue recovery meaningfully above chance.

Scoped as a **standalone ability demonstration** — a clean reproduction of recent Anthropic work on
an open model, legible to a reader who knows nothing about NLAs or the measurement angle. It
deliberately does *not* demonstrate extension or research-creativity; that trade-off is accepted for
a fast, unambiguous signal. (The explicit-vs-implicit split and the scoring discipline carry a little
methodological taste at no extra scope.)

## Target-model decision (this moves all the numbers)

`RESEARCH.md` names Gemma-3-27B. The docs make the friction explicit; for a pure ability demo it's
worth choosing deliberately:

| | Qwen-2.5-7B @ L20 | Gemma-3-27B @ L41 |
|---|---|---|
| HF gating | ungated | **gated** (accept license, `HF_TOKEN`) |
| SGLang patch | none (plain causal LM) | **mm-wrapper bypass patch required** (else `input_embeds` is silently dropped → `\n\n\n`) |
| backend flags | stock | `--attention-backend fa3` (flashinfer OOMs on `head_dim=256`) |
| GPU | 24 GB (4090 / L40S) | 80 GB (H100) |
| `setup.md` verdict | **"recommended starting point"** | larger-model signal |

**Recommendation:** smoke-test the pipeline on **Qwen-2.5-7B** first (lowest friction, proves
injection works), then run the headline replication on **Gemma-3-27B** if the larger-model signal is
wanted — or stay on Qwen for minimum time-to-result.

⚠️ **Verify against the paper** which model the Language Switching finding was demonstrated on, so
"replication" is a clean match rather than a port to a different model.

## Checklist

### Phase 0 — provision + deps (inference-only path)
- [ ] Rent pod — RunPod H100 80 GB (Gemma) or a 24 GB card (Qwen)
- [ ] `uv pip install torch transformers safetensors httpx orjson pyyaml numpy` + `sglang[all]>=0.5.6`
  — ⚠️ pin `torch<2.11` *or* use the cu124 index (unpinned cu130 conflicts with `sgl-kernel`'s cu12 wheels)
- [ ] HF auth + accept the Gemma license (Gemma only); download the AV checkpoint (~50 GB for 27B, ~14 GB for 7B)

### Phase 1 — bring-up + smoke-test ⚠️ *highest-variance step*
- [ ] (Gemma) apply `patches/apply_sglang_patches.sh` for the mm-wrapper bypass
- [ ] Launch the SGLang AV server (`--disable-radix-cache` mandatory; Gemma: `--attention-backend fa3`)
- [ ] Run a few AV decodes on a known vector → **eyeball English vs CJK soup** (the doc's correctness check)
- [ ] If CJK: walk the Debugging list — `injection_scale`, Gemma `embed_scale` = √d, double-BOS, template drift, embeds-only (no `input_ids`)
- *This is where the time risk lives; the whole Debugging section in `inference.md` exists because injection is finicky.*

### Phase 2 — experiment design (the methodological core — don't rush it)
- [ ] Construct ~20 identity-cue prompts, **explicit and implicit** variants, with planted ground truth
- [ ] Define the scoring rubric (what counts as "recovered the cue"), the **chance baseline**, and the pass criterion (implicit-cue recovery meaningfully above chance) — **pre-register it**

### Phase 3 — run + score
- [ ] Extract the L41 (Gemma) / L20 (Qwen) residual at the **first assistant-response token** per prompt
- [ ] Verbalize via the AV; score recovered-identity vs planted, explicit vs implicit
- [ ] *(optional)* AR round-trip MSE/cos as a decode-fidelity filter — the AV is usable standalone, so lower priority

### Phase 4 — analysis + writeup
- [ ] Explicit vs implicit recovery rates, CIs vs the chance baseline, one figure, short standalone report

## Compute / time / cost (ranges)

- **Compute is trivial.** ~20–60 prompts × a ~200-token AV decode each ≈ tens of thousands of tokens,
  minutes of GPU. The GPU is for *capacity* (fitting a 27B AV), not throughput. **1× H100 80 GB**
  (Gemma) or **1× 24 GB card** (Qwen). The AR is optional, so both models need not be resident.
- **Person-time: ~3–7 focused days**, wall-clock **~1–2 weeks** with iteration. The range is driven by
  Phase 1 — clean decode in half a day if it "just works," 1–2 days if injection-debugging is needed.
- **GPU cost: ~$30–90** (Gemma-27B H100 @ ~$2.89/hr, ~10–30 pod-hours with disciplined shutdown) or
  **~$10–30** (Qwen-7B on a $0.69–0.86/hr card). Compute is *not* the binding cost — time is.

| Phase | Person-time | GPU |
|---|---|---|
| 0 — provision + deps | 0.5–1 d | idle-ish |
| 1 — bring-up + smoke-test ⚠️ | 0.5–2 d | active, low util |
| 2 — experiment design | 0.5–1 d | none |
| 3 — run + score | 0.5–1 d | minutes of generation |
| 4 — analysis + writeup | 1–2 d | none |

## Named risks (plumbing, not research — front-loaded into Phases 0–1)

All documented, so all nameable in advance:
- SGLang mm-wrapper silently drops `input_embeds` on Gemma-3 (→ `\n\n\n`) without the bypass patch
- torch/SGLang CUDA-pin conflict (cu130 vs cu12)
- HF gating delay on Gemma
- injection-failure debugging (scale / `embed_scale` / BOS / template)

None are research risk. The research risk is ~zero (it's a replication); the failure mode is *time
sunk in bring-up*, which is why Phase 1 is flagged and Qwen-first is recommended.

## Pin before any pod time

The Phase-2 scoring rubric + chance baseline + pass criterion. It costs $0 to nail down now, and it
is the difference between a result and vibes — pre-register it before spending compute.
