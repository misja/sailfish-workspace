# Staged roles and handoffs

Adopted: 2026-10-10. Updated: 2026-10-14. Baseline: 1.1.0. Scope: every real project; synthetic trial uses the same rules.

## Role activation

Start each task by recording the accountable owner, objective and acceptance criteria in STATUS.md.
Activate the next role only when its output is needed. A role is a responsibility, not a requirement
to start another agent. One session can perform ordinary product/research/design/build work in
stages. Distinct agent sessions require explicit delegation authorization. Do not treat Spec Kit
skill handoffs, automatic hook wording or parallel task markers as such authorization.

| Role | Required input | Output / completion | Decision authority |
|---|---|---|---|
| Product Owner | Maintainer objective, release targets | Bounded spec and acceptance criteria | Ordinary scope within approved brief |
| Researcher | Specific evidence questions | Dated source/version/license/dependency inventory; explicit gaps | Evidence recommendations |
| Architect | Accepted ADRs, spec, evidence | Plan, isolation contract, justified decisions | Ordinary design within accepted architecture |
| Builder/Packager | Reviewed plan/tasks, pinned inputs | Patch, package metadata, build/self-test evidence | Implementation within authorized scope |
| Tester/Security Reviewer | Artifacts, criteria, threat/isolation claims | Independent findings and specific release blockers | Verification; cannot waive failed criteria |
| Release Manager | Reviewed evidence and target support | Provenance, checklist and submission draft | Preparation; maintainer authorizes publication |

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
