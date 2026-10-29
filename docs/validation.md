# Validation record

Validated on 2026-10-29 against release `v0.1.1`.

## Distribution

- The skill-creator frontmatter and scaffold validator passed.
- The local Windows run executed 27 behavioral tests: 25 passed and two ordinary-symbolic-link tests were skipped because the account lacks link-creation privilege. The Windows junction rejection test passed.
- GitHub Actions passed on Windows, macOS and Linux with Python 3.10. The release publication job passed.
- The downloaded standalone Skill ZIP and source ZIP passed the published SHA-256 checks. Every file in the standalone Skill ZIP matched the corresponding committed blob at `v0.1.1`.
- Current-user Codex/generic and Claude Code installations matched the distributed skill files. Repeating the installation reported identical contents without replacing the installation.
- Codex `app-server` discovered the installed user skill as enabled with no discovery errors in three working directories. This checks discovery, not an autonomous agent's future documentation quality. Claude Code's installed files were verified; its runtime loading was not tested.

Release and CI evidence:

- [Release v0.1.1](https://github.com/DreamWalkerJK/functional-analysis-skill/releases/tag/v0.1.1)
- [Release verification workflow](https://github.com/DreamWalkerJK/functional-analysis-skill/actions/runs/40833227287)

## Functional documentation trial

After installing the skill, agents used its installed entrypoint and references to analyze selected services in a private .NET microservice repository. The trial covers stateful user workflows, event processing and multi-stage imports. Documents and source-anchor indices are retained in the user's local review directory; private source, output, paths and configuration are excluded from this public repository.

The trial checks whether the instructions produce useful capability maps, ordered behavior descriptions, rules and state changes, explicit failure boundaries, and traceable source evidence. Independent review of selected consequential flows is used to challenge the interpretation. Source-anchor hash checks are recorded separately because matching hashes cannot establish that the prose follows from the source.

The trial is source analysis. Application services, databases, message brokers, object storage and OCR models were not started or contacted, and application tests were not executed. Reading an existing test establishes its expected scenario, not that it passed in this trial.

The first documents were generated using the installed `0.1.0` skill. Release `0.1.1` fixes installer handling of Python caches; the analysis method, writing guide, template and evidence checker are unchanged, and the entrypoint differs only in its version metadata. Local installations were then brought to `0.1.1` with the old task-created copies preserved outside discovery directories.

## Interpretation limits

The portability claim concerns the skill's instructions and optional standard-library tooling. Automatic discovery is controlled by each client. Other agents can explicitly read `SKILL.md` and its relative resources; machine-wide activation for every operating-system account requires client-supported organizational deployment or per-user installation.

Cross-platform CI and a private-repository trial demonstrate these concrete cases. They do not guarantee compatibility with every agent or correctness for arbitrary systems. The evidence checker establishes the integrity of listed source locations; readers must assess business meaning and uncovered dependencies separately.
