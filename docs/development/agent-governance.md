# Staged roles and handoffs

Adopted: 2026-10-10. Updated: 2026-10-17. Baseline: 1.3.0. Scope: every real project; synthetic trial uses the same rules.

## Role activation

Start each task with a bounded objective, acceptance criteria, accountable owner
and required reviewer in the existing issue; STATUS.md carries a concise session
handoff. Activate a role when its output is needed. Ordinary work within reviewed
scope remains autonomous; roles do not require a standing team.

Substantial architecture/scope decisions require a separate agent review before
implementation, checking simpler alternatives and maintenance cost. Crypto,
runtime/package isolation and release-critical changes also require separate
review of the resulting artifacts before maintainer review. The maintainer
explicitly authorizes delegation for these required reviews (AGENTS baseline 1.2.0).
Do not replace a reviewer with the builder under another role label. Resolve
findings first; report an unavailable required reviewer rather than proceeding
with dependent work. Do not add speculative infrastructure or duplicate process
artifacts. Other distinct-agent work still requires explicit delegation;
Spec Kit hooks and parallel markers do not supply it.

| Role | Required input | Output / completion | Decision authority |
|---|---|---|---|
| Product Owner | Maintainer objective, release targets | Bounded spec and acceptance criteria | Ordinary scope within approved brief |
| Researcher | Specific evidence questions | Dated source/version/license/dependency inventory; explicit gaps | Evidence recommendations |
| Architect | Accepted ADRs, spec, evidence | Plan, isolation contract, justified decisions | Ordinary design within accepted architecture |
| Builder/Packager | Reviewed plan/tasks, pinned inputs | Patch, package metadata, build/self-test evidence | Implementation within authorized scope |
| Tester/Security Reviewer | Artifacts, criteria, threat/isolation claims | Independent findings and specific release blockers | Verification; cannot waive failed criteria |
| Release Manager (separate agent) | Reviewed artifacts, changes and existing test evidence | User-facing release proposal: purpose, changes, sources and relevant limitations | Owns release presentation; maintainer authorizes publication |

## Release handoff

Builder/Packager supplies artifacts, changes and test evidence. A separate
technical reviewer assesses claims and remaining risks. A distinct Release
Manager agent then owns the outward-facing release proposal, reading it from
the perspective of someone unfamiliar with the project. The builder must not
also fill that role for the same release. Misja reviews and authorizes publication.

Reuse prior device tests with their recorded scope. A new package revision does
not automatically require another complete device test: any additional check
must address a named changed behavior or uncovered risk. An alternative that changes the requested outcome needs maintainer agreement;
reviewers must flag that mismatch rather than accept it as completion.
The Release Manager
cannot waive technical findings or create new test requirements without such a
reason. Keep review/approval history in the existing release issue.

## Research before proposing new mechanisms

All roles, including delegated agents, follow AGENTS baseline 1.3.0: inspect
maintained upstream behavior and actual platform facilities before adding a
requirement or custom mechanism. The scope/design reviewer must ask whether the
problem comes from an unnecessary project restriction. Record evidence and the
remaining gap in the existing issue. A custom service/lifecycle framework or
other departure needs concrete justification and maintainer agreement.

## One shared artifact set

Each real project owns its constitution and spec/plan/tasks; roles work on those same artifacts.
Keep research and verification evidence beside that feature. Use the extensible release target
registry; each release records its project version, selected target IDs and verification evidence.
Do not create role-specific duplicate specs or independent feature.json state in the same checkout.

Spec Kit commands supply workflow instructions. They do not perform all roles automatically or
replace decision authority. Typical progression: constitution once, specify/clarify, plan,
tasks/analyze, implement, verification/converge, release preparation. Use only useful stages.

## Blockers and ownership transfer

The owner investigates, supplies viable options and a recommendation, then consults the relevant
role once for that unresolved blocker. If still unresolved, escalate to the decision owner.
Reopen decisions only on new evidence. A consultation leaves accountability with the current owner.

Use this STATUS.md handoff:

```text
Current owner / next owner / decision owner:
Objective and acceptance criteria:
Changed artifacts and evidence paths:
Decisions and authorization scope:
Remaining blockers, options and recommendation:
Next action:
```

## Verification and authorization

Builder self-tests are sufficient for routine low-risk integration checks. Crypto behavior,
runtime/package isolation and release-critical changes require verification separate from implementation.
Changing a role label on the builder does not create independence. Distinguish
automated checks, assistant review and human review. Assistant agreement is not
a human audit; the maintainer reviews changes and judges the evidence. No independent review was
performed during the Spec Kit trial; a separate security verification remains due for real packaging.

Existing scoped approval persists. Proceed autonomously with reversible work inside that scope;
prepare concrete artifacts before requesting approval for a new installation, security exception,
device change or publication. Synthetic data only. No skill or role can broaden authorization.

This is an operational staged-role policy. No standing multi-agent team, model configuration,
automatic role bundles, GitHub issue synchronization or release automation is installed.
