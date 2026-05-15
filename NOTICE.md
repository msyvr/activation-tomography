# Notice

This repository, `activation-tomography`, is a research fork of
[`kitft/natural_language_autoencoders`](https://github.com/kitft/natural_language_autoencoders)
by Kit Fraser-Taliente, derived at commit
`047eb8e40452982d38f83721f9fb2c77baf6b0cf` (tagged `upstream-fork-point` in
this repository).

The original work is the open-source library accompanying the Anthropic
Transformer Circuits paper *Natural Language Autoencoders Produce Unsupervised
Explanations of LLM Activations* (Fraser-Taliente, Kantamneni, Ong et al.,
2026, <https://transformer-circuits.pub/2026/nla/index.html>). The upstream
README and the three upstream developer-facing docs (`design.md`,
`inference.md`, `setup.md`) are preserved under `docs/nla_upstream/`, with
content unchanged except for a provenance header note and internal path
references updated to reflect this fork's organization.

## License

This fork is licensed under the Apache License, Version 2.0, the same license
as the source repository. See `LICENSE` for the full text.

In accordance with Apache 2.0 §4(b), significant modifications by this fork
will be marked in git history and summarized below as the work progresses.

## Modifications

In accordance with Apache 2.0 §4(b), the following non-code modifications have
been made relative to the upstream commit
`047eb8e40452982d38f83721f9fb2c77baf6b0cf`. Significant code modifications
will be summarized here as the work progresses.

### Fork-establishment commit
- Added `README.md` (new front page describing this fork's research direction).
- Added `NOTICE.md` (this file).
- Added `CITATION.cff` (structured citation metadata for this fork).
- Updated `pyproject.toml`: changed `[project].name` from `nla` to
  `activation-tomography`, reset version to 0.0.1, updated description and
  URLs. The Python package directory (`nla/`) and all Python imports are
  unchanged.

### Documentation reorganization commit
- Moved the upstream README and developer-facing docs into `docs/nla_upstream/`
  (was: `README_NLA.md`, `docs/design.md`, `docs/inference.md`,
  `docs/setup.md`).
- Added a provenance header note to each moved file.
- Updated internal cross-references and path references within the moved
  files, in this `NOTICE.md`, in `README.md`, and in the upstream `CLAUDE.md`
  (which remains at the repo root because Claude Code consumes it from there).

## Citation

If you use this software or build on its findings, please cite both the
original work and (where appropriate) this fork. See `CITATION.cff` for full
metadata and `README.md` for BibTeX entries.

## Maintainer

This fork is maintained by Monica Spisar
([ORCID 0009-0006-1719-4798](https://orcid.org/0009-0006-1719-4798)),
independent researcher.
