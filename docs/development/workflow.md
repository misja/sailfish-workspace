# Working agreements

One accountable owner per issue. Issues describe objectives, acceptance criteria,
dependencies and current work state. Pull requests contain the proposed changes
and validation. Durable decisions belong in an ADR or maintained contract.

Use short branches and pull requests against main. Link the issue; use Closes
only when the change satisfies its acceptance criteria. Existing feature
specifications and plans remain design references, not a second backlog.

The Sailfish project board provides one view across the repositories.
Shared work belongs in sailfish-workspace; choose the runtime
or password-store repository when creating an issue about that component.
The status options are Todo, In Progress and Done. Select work from the board
and set its issue In Progress before implementation. Record current findings,
linked PRs and the next action in that issue; keep dependencies current.
Closing an issue after its acceptance criteria pass moves the board item to Done.
Do not close an umbrella issue merely because one preparation PR is merged.
Keep work In Progress
during review; label unresolved dependencies blocked and state the next action.

## Review and decisions

The maintainer reviews changes before merge and remains responsible for merge
and release decisions. We use AI-assisted development; the contribution
guidelines explain disclosure, validation and human responsibility. AGENTS.md
contains instructions for assistants, not a substitute for maintainer review.

Routine changes need appropriate checks. Crypto behavior, runtime/package
isolation and release-critical changes need verification separate from
implementation. Identify automated checks, assistant review and human review
accurately. Neither passing tests nor an AI report automatically grants release
acceptance.

Installation, device/system changes, package publication and upstream submission
need explicit approval of their concrete scope. A source merge does not grant it.
Use only synthetic or published test data in project automation.

## Release preparation

Follow the [release handoff](agent-governance.md#release-handoff): builder,
separate technical reviewer, distinct Release Manager agent, then maintainer.
The Release Manager owns the user-facing proposal, not just an artifact checklist.
Use existing evidence; justify additional testing by a specific changed risk.
Record the handoff in the existing release issue. Spec Kit is not required for
adjusting these working agreements or preparing a release.

## Repository responsibilities

| Repository | Work |
| --- | --- |
| sailfish-workspace | Shared policy, architecture and SDK infrastructure |
| sailfish-gnupg-runtime | Runtime and native pinentry behavior, packaging and lifecycle |
| sailfish-password-store | pass/OTP integration and supporting packages |

Keep design and evidence with the responsible component, linking related issues
and PRs across repositories. Record an enduring decision once and link back to
its discussion. STATUS.md is a short session handoff, not a task/status database. Local task lists
and historical Markdown records do not override live issue or board state.

Essential assistant/contribution instructions and templates are kept in each
repository. Shared templates are maintained in workspace and copied after
review; there is no automatic synchronization. Spec Kit is an optional drafting
tool; it does not add authority or replace the maintainer's judgment.

References checked 2026-10-14: [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow),
[project default repository](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-your-project/adding-your-project-to-a-repository).
