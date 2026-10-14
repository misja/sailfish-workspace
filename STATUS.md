# Current workspace handoff

Updated: 2026-10-14. Maintainer: Misja Hoebe (@misja).
Current work: portable workspace bootstrap and upstream-fork migration.
Review: https://github.com/misja/sailfish-workspace/issues/4.

Draft PRs: workspace #3, runtime #6, password-store #3. No merge or upstream
submission is implied. The migration branch includes the six-repository checkout
helper, public architecture/Spec Kit record, feature templates and complete-tree
packaging patch verification. Runtime materialization includes assuancompat.h.

Local public checkouts now use their GitHub names under code/sailfish. Original
repositories and local evidence are preserved in .local-history/20261014 outside
the public repositories. These paths describe the maintainer's machine only.

Open product gates include clean-checkout package/bootstrap support, SDK setup,
exact vendor provenance, production lifecycle, provider/upgrade and distribution.
General source/planning work needs Git and Python; package/device readiness is
not established by the workspace setup. See docs/development/getting-started.md.
