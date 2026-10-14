# Bootstrap implementation plan

Use [ADR 0001](../../docs/adr/0001-workspace.md) and AGENTS baseline 1.1.0.
Keep a single JSON-formatted YAML manifest consumed by a standard-library Python
helper. Clone over HTTPS; configure upstream only for forks. New forks use exact
commits. Existing checkouts are preflighted and left on their working branch.

Keep upstream-forks.json as the source revision map for full-tree patch checks.
Apply packaging snapshots to the pinned upstream tree in a temporary Git index
and object directory, then compare its tree ID to the fork head. Export snapshots
only from the recorded commits; validate all before replacing snapshot files.

Carry a concise architecture and Spec Kit record plus plain feature templates.
Do not export machine evidence, generated skills, old active-feature state or
unreviewed private histories. Preserve original local roots in a local archive.

Validate using disposable clones and negative scenarios for wrong origins,
dirty existing work, modified snapshots and omitted local headers. These source
checks do not establish package build or runtime acceptance.
