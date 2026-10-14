# ADR 0001: a small multi-repository Sailfish workspace

Status: accepted directions recorded 2026-10-10, refined 2026-10-14.
Decision owner: Misja Hoebe (@misja).

Use a non-Git parent directory with independent repositories. sailfish-workspace
owns common working agreements, architecture and shared development infrastructure.
Component repositories own their code, packaging, tests and component design.
The local directory names match GitHub repository names.

GitHub is the primary source and work tracker. Issues describe open work; pull
requests carry changes and review evidence; one project board provides the
cross-repository view. Durable decisions remain in versioned documentation.
No second live backlog is kept in Spec Kit tasks.

Adapt modified upstream projects in real forks, retaining their original
history. Own packaging repositories retain recipes and generated patch snapshots.
Pinned source identities and authenticated upstream archives remain build inputs;
never apply our patches again to an already patched fork archive. Unmodified
dependencies do not need forks. Review updates explicitly and verify patch
snapshots against the complete pinned fork tree.

Spec Kit is an optional drafting/scaffolding tool, pinned in the manifest.
Keep one feature artifact set with its component, using only useful workflow
stages. It does not require a particular editor, assistant or multi-agent service.

The first components are an isolated GnuPG runtime and pass/OTP packaging.
Preserve stock Jolla software. Native integration, lifecycle, provider upgrades,
exact vendor-source provenance and distribution require their own evidence.
The initial CLI/runtime focus does not limit this workspace to those components:
add other Sailfish work through an explicit scope and repository decision.

Upstream-derived work retains upstream terms; independent original work uses
GPL-3.0-or-later. Misja reviews merges and releases. Source review and package
release acceptance are distinct decisions.

This document is a concise public record of the accepted local architecture.
Historical investigation reports and machine-specific evidence remain local;
their absence does not constitute a passing build or security audit.
