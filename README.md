# activation-tomography

> **Status**: research fork, work in progress. Started 2026-05-14. This README
> will evolve as the research direction sharpens.

**Activation tomography** is an inverse-problem framing for LLM
interpretability: given a model's high-dimensional internal state, reconstruct
a low-dimensional, human-readable description, then validate by checking that
the round trip recovers the original state. The framing is structurally
analogous to medical imaging tomography (CT, PET, MRI, OCT), where
high-dimensional latents are recovered from low-dimensional projections under
consistency constraints.

This repository instantiates the framing using **Natural Language Autoencoders
(NLAs)** as the reconstruction instrument. The NLA architecture, training
infrastructure, and released checkpoints are forked from
[`kitft/natural_language_autoencoders`](https://github.com/kitft/natural_language_autoencoders),
the open-source library accompanying the Anthropic Transformer Circuits paper
*Natural Language Autoencoders Produce Unsupervised Explanations of LLM
Activations* (Fraser-Taliente, Kantamneni, Ong et al., 2026).

## Research direction

Applying the activation-tomography framing to **measurement of LLM and agent
collective behaviors** — multi-agent belief states, theory-of-mind,
unverbalized coordination, and the identifiability limits of
activation-language translation.

Initial planned experiments (subject to evolution as the work proceeds):

- Replicating the Language Switching case study (Fraser-Taliente et al., 2026)
  on open-model NLAs (Gemma-3-27B or similar).
- Extending to two-agent settings: does agent A's NLA reveal A's internal
  model of agent B?
- Cross-agent evaluation-awareness propagation in agent chains.
- Detecting unverbalized side-channels between communicating agents.

A more detailed plan will be added in `RESEARCH.md` as the work crystallizes.

## Provenance

Forked from
[`kitft/natural_language_autoencoders`](https://github.com/kitft/natural_language_autoencoders)
at commit
[`047eb8e40452982d38f83721f9fb2c77baf6b0cf`](https://github.com/kitft/natural_language_autoencoders/commit/047eb8e40452982d38f83721f9fb2c77baf6b0cf),
tagged `upstream-fork-point` in this repository. The original README is
preserved verbatim in [`README_NLA.md`](README_NLA.md). See
[`NOTICE.md`](NOTICE.md) for full attribution.

## License

Apache 2.0. See [`LICENSE`](LICENSE).

Released checkpoints from the source repository additionally inherit the
license of their base model (Gemma, Llama-3.3) — see the NOTICE files in each
HuggingFace repo.

## Citation

If you use this software or build on its findings, please cite both:

**The original NLA paper** (Fraser-Taliente, Kantamneni, Ong et al., 2026):

```bibtex
@article{frasertaliente2026nla,
  author  = {Fraser-Taliente, Kit and Kantamneni, Subhash and Ong, Euan and Mossing, Dan and Lu, Christina and Bogdan, Paul C. and Ameisen, Emmanuel and Chen, James and Kishylau, Dzmitry and Pearce, Adam and Tarng, Julius and Wu, Alex and Wu, Jeff and Zhang, Yang and Ziegler, Daniel M. and Hubinger, Evan and Batson, Joshua and Lindsey, Jack and Zimmerman, Samuel and Marks, Samuel},
  title   = {Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations},
  journal = {Transformer Circuits Thread},
  year    = {2026},
  url     = {https://transformer-circuits.pub/2026/nla/index.html}
}
```

**This fork** (Spisar, 2026):

```bibtex
@software{spisar2026activation_tomography,
  author = {Spisar, Monica},
  title  = {{activation-tomography}: an inverse-problem framing for LLM interpretability via natural language autoencoders},
  year   = {2026},
  url    = {https://github.com/msyvr/activation-tomography},
  note   = {Research fork of kitft/natural\_language\_autoencoders}
}
```

For reproducibility, cite a specific commit SHA or release tag rather than
HEAD. The repository's [`CITATION.cff`](CITATION.cff) provides full structured
metadata (GitHub renders a "Cite this repository" button from this file).

---

*Maintained by [Monica Spisar](https://monicaspisar.com), independent
researcher ([ORCID 0009-0006-1719-4798](https://orcid.org/0009-0006-1719-4798)).*
