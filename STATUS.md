# Session handoff

Updated: 2026-10-16. Decision owner: Misja Hoebe (@misja).
Live work: [runtime #3](https://github.com/misja/sailfish-gnupg-runtime/issues/3)
and the [project board](https://github.com/users/misja/projects/2).

## Recorded state

During the 2026-10-15 audit all six public checkouts were clean, active heads
matched GitHub and no PR remained open. Own repositories use main; upstream
forks retain pinned adaptation branches. No upstream pin was advanced.
Local archives and personal/ignored assistant instructions are local-only;
fresh clones of the three own repositories receive committed AGENTS.md rules.

Workspace SDK/bootstrap issue #5 is complete. The historical
[clean build](docs/development/clean-sdk-build-20261015.md) produced six main binary
and five source RPMs in SDK 3.13.5 / SailfishOS-5.1.0.11-aarch64. This does not
verify current runtime candidate 0.6 or establish Sailfish 5.2/device compatibility.

Runtime PR #15 removed custom Python admission/watch/generation/recovery code,
probes and superseded reports. Shell isolation/identity checks and the IPC
supervisor remain. All 23 remaining host tests passed; no new SDK/full RPM build
was run for that cleanup. Automatic/concurrent upgrade/removal is unsupported.
Historical code and evidence remain in Git history.

Mandatory separate design and relevant implementation review is committed in
workspace #9, runtime #16 and password-store #7 (AGENTS baseline 1.2.0).
The separate assistant cleanup and handoff/scope reviews are not a human security
audit or independent release acceptance.

## Next role handoff

Current owner: primary assistant (status/research handoff).
Next owner: Architect responsibility for runtime #3, with a separate reviewer.
Decision owner: Misja. Objective: define the smallest supported manual maintenance
scenario and acceptance plan; do not implement a transaction framework.

Acceptance: identify exclusion of new starts during actual replacement/removal,
private-agent ownership/stop boundaries, interrupted-change behavior, preservation
of stock software/user data, simpler alternatives/maintenance cost and bounded
synthetic checks. A separate reviewer assesses the proposal before implementation.
The live issue owns detailed criteria and progress; this is not a second backlog.

A fresh 0.6 SDK build remains due as packaging evidence; it cannot prove upgrade
safety. Exact vendor provenance (runtime #1), target/provider verification (#4),
source/notice/relink delivery (workspace #2) and distribution/trust (runtime #5)
remain open. Pass/OTP provider/onboarding work has related gates; newer upstream
pass/OTP revisions remain a separate review (password-store #4).

No new SDK/dependency/target installation, deployment, real-secret inspection,
device/OBS action or upstream submission occurred or was authorized by this audit.
