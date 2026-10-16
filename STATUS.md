# Session handoff

Updated: 2026-10-16. Decision owner: Misja Hoebe (@misja).
Live work: [release delivery #2](https://github.com/misja/sailfish-workspace/issues/2)
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

## Release handoff

Pass/OTP upstream review #4 is complete and Done. Both source PRs, package PR #8
and workspace PR #11 are merged. Release bases stay pass 1.7.4 / OTP 1.2.0;
only the two attributed upstream backports were adopted. Source pins and patch
snapshots match complete fork trees. Pinned backport branches are intentionally
retained because protected branch squash merges create different commit IDs.

Current owner: primary assistant for integration; separate Release Manager agent
owns outward release presentation, and a separate technical reviewer assesses
evidence. Misja decides release/publication.
Objective: assemble and verify existing candidate/source artifacts and identify
actual remaining release blockers using existing issues, not a new framework.
No package installation, device/OBS change or publication is authorized here.

Runtime 0.6 SDK packaging evidence is merged in runtime PR #18. Pass/OTP 0.5
build, focused regression and separate artifact review are merged in package #8.
The archived development trial was already completed; do not repeat it merely
because general release gates remain. SDK builds do not prove current-device
or live package-manager upgrade acceptance. Runtime #3 remains open for that scope.
Exact vendor provenance (runtime #1), target/provider verification (#4),
source/notice/relink delivery (workspace #2) and distribution/trust (runtime #5)
remain open. Pass/OTP provider/onboarding work has related gates; the selected upstream
backports are complete (password-store #4).

No new SDK/dependency/target installation, deployment, real-secret inspection,
device/OBS action or upstream submission occurred or was authorized by this audit.

Local release review delivery: six binary/five matching source RPMs assembled
with exact hashes; all unsigned. See [release handoff](docs/development/release.md).
No publication or release acceptance is implied; maintainer scope/target and
existing provider, lifecycle and trust gates remain.

Checksum signing: SHA256SUMS is signed by the selected Ed25519 fingerprint;
separate public-key-only verification and all11hash checks passed. RPMs remain
unsigned; see the release record for SDK compatibility limits. No key copy or
local package installation occurred.

Release-flow update: distinct Release Manager owns user-facing notes; prior Xperia
checks remain valid within scope and revision changes alone do not trigger full
retesting. Both GitHub drafts are being updated with that agent's wording.
Signed checksums are a fallback, not embedded RPM signing; target Ed25519 verifier
compatibility must be established before selecting a replacement signing route.
Workflow/docs changes extend existing PR #13; no Spec Kit artifacts added.
