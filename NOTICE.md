# Notice

This repository, `activation-tomography`, is a research fork of
[`kitft/natural_language_autoencoders`](https://github.com/kitft/natural_language_autoencoders)
by Kit Fraser-Taliente, derived at commit
`047eb8e40452982d38f83721f9fb2c77baf6b0cf` (tagged `upstream-fork-point` in
this repository).

The original work is the open-source library accompanying the Anthropic
Transformer Circuits paper *Natural Language Autoencoders Produce Unsupervised
Explanations of LLM Activations* (Fraser-Taliente, Kantamneni, Ong et al.,
2026, <https://transformer-circuits.pub/2026/nla/index.html>). The original
README is preserved verbatim in `README_NLA.md`.

## License

This fork is licensed under the Apache License, Version 2.0, the same license
as the source repository. See `LICENSE` for the full text.

In accordance with Apache 2.0 §4(b), significant modifications by this fork
will be marked in git history and summarized below as the work progresses.

## Modifications

No substantive code modifications yet. As the work develops, summaries will be
added here with pointers to relevant commits or release tags.

The initial fork-establishment commit (this commit) adds the following non-code
files to organize the fork:

- `README.md` — new front page describing the research direction; the original
  README is preserved at `README_NLA.md`.
- `README_NLA.md` — original README, preserved verbatim.
- `NOTICE.md` — this file.
- `CITATION.cff` — structured citation metadata for this fork.
- `pyproject.toml` — updated `[project].name`, description, and URLs to reflect
  this fork; the Python package directory (`nla/`) and all imports are
  unchanged.

## Citation

If you use this software or build on its findings, please cite both the
original work and (where appropriate) this fork. See `CITATION.cff` for full
metadata and `README.md` for BibTeX entries.

## Maintainer

This fork is maintained by Monica Spisar
([ORCID 0009-0006-1719-4798](https://orcid.org/0009-0006-1719-4798)),
independent researcher.
