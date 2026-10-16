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

Current release delivery: six binary and five matching source RPMs now have
V4 EdDSA/SHA256 signatures from the selected Ed25519 key. All main headers and
payloads match the reviewed unsigned builds. SDK RPM verified all eleven
signatures and digests; the missing-key control returned NOKEY. Separate review
recomputed hashes, compared payload bytes and verified both checksum signatures.

Distinct Release Manager owns the user-facing notes. Existing Xperia checks
remain valid within scope; package revisions alone do not require full retesting.
Both GitHub drafts are updated with signed assets and checksums; publication
and existing target/provider/lifecycle decisions remain with Misja.

Temporary signer downloads, extracted tools and local/SDK signing probes are
removed after upload verification. No system package was installed. Evidence
and unsigned/signed hash mapping remain in the release manifest and issue #2.
Workflow, signing and fallback-agreement changes extend existing PR #13;
no Spec Kit artifacts or permanent signing/test infrastructure were added.
