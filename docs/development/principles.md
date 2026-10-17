# Engineering principles baseline

Version: 1.0.0. Adopted 2026-10-10. Source: accepted Phase A constitution proposal. This is a shared baseline, not a generated Spec Kit constitution.

1. **Evidence before assertion.** Separate supplied observations, dated external facts, recommendations and unknowns. Pin build inputs; maintain source/patch/license provenance. Absence of search results is not proof of absence.
2. **System coexistence.** Community packages must not replace Jolla components. Private runtime isolation covers loader paths, binaries/helpers, RPM resolution, configuration, IPC and upgrade/removal. Demonstrate it through independent evidence.
3. **No real secrets in engineering systems.** Agent, CI and test artifacts use synthetic keys/stores and published test vectors only. Never inspect or log real private keys, passwords, OTP URIs/seeds or recovery material.
4. **Native, bounded secret handling.** Prefer supported APIs and maintained crypto implementations. Validate paths/input, avoid secret argv/env and persistent plaintext, control cache/clipboard/lifecycle exposure. Document limits rather than claim absolute protection.
5. **Independent release verification.** Builders self-test; an independent reviewer checks crypto behavior, packaging isolation and release-critical exposure. Unresolved failures are explicit blockers; no self-approved security/release sign-off.
6. **Reproducible and maintainable inputs.** Sources, targets and patches are reviewable/pinned. Compare clean builds before claiming byte reproducibility. Security dependency changes require analysis and regression evidence.
7. **Clear ownership, minimal process.** One accountable task owner; role activation must add value. One blocker clarification round-trip, then decision-owner escalation. Concise artifact handoffs; one shared spec/plan/task set.
8. **Sparse firm human gates.** Follow the approved scope; do reversible routine work autonomously. Architecture bootstrap, exceptional security/system/destructive changes, device changes and external publication require explicit scoped authorization.
9. **Independent projects.** Apps/packages own their histories, tests and releases. Shared infrastructure serves unrelated Sailfish projects; create common runtime/UI libraries only after demonstrated reuse.

## Platform conventions

Use existing Sailfish, RPM and upstream lifecycle facilities before adding
project-specific mechanisms. Normal users must not inspect or kill processes to
install, update or remove packages. Check the actual target versions and macro
implementations: a familiar macro name is not proof it performs the required
action. Any departure from maintained platform/upstream practice needs a concrete
justification and maintainer agreement before implementation.

Research is a prerequisite to introducing new constraints, not an optional check
after a maintainer questions them. Record the relevant upstream/platform behavior,
the actual unsolved problem and the simpler alternatives in the existing issue.
Independent reviewers must question the necessity of the requirements themselves.
Apply this to the primary assistant and delegated agents; AGENTS baseline 1.3.0
makes it a persistent instruction in each project checkout.
