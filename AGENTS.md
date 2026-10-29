# Contributor guidance

This repository distributes a portable Agent Skill. Keep the core instructions independent of any agent, OS, account, shell, API, and repository. Product-specific discovery details belong in the README, not in the analysis contract.

- Skill source of truth: `skills/functional-analysis/`.
- Use Python 3.10+ standard library for optional tooling.
- Keep private validation projects and generated business documents outside this repository. Examples committed here must be synthetic.
- Describe observed behavior separately from intent and inference. Never claim application runtime validation from source inspection or hash checks.
- Run `python -m unittest discover -s tests -v` after tooling changes. Inspect the skill references and template together when changing the analysis contract.
- Use commit subjects `<type>(<scope>): <description>` with a concrete scope and no more than 72 Unicode characters.
- Update `VERSION`, skill metadata and `CHANGELOG.md` together for a release. Tag releases as `v<VERSION>`; build archives from committed Git blobs.
