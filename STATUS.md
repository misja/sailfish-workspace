# Session handoff

Updated: 2026-10-18. Decision owner: Misja Hoebe (@misja).
Live work: [release delivery #2](https://github.com/misja/sailfish-workspace/issues/2)
and the [Sailfish project board](https://github.com/users/misja/projects/2).

Current owner: primary assistant coordinates with Misja; separate Builder/Packager
owns implementation, independent reviewer checks release artifacts and draft
metadata, and a separate Release Manager owns documentation and presentation.

## Current release preparation

Source changes are merged: runtime package renamed to `sailfish-gnupg-runtime`
2.5.24-0.7; pass 1.7.4-0.6 and OTP 1.2.0-0.6 use coordinated dependencies.
The private executable/library namespace remains unchanged. Ordinary GnuPG
activation handles startup and updates; existing agents retain their previous
code until they exit. Final removal checks for private CLI clients before
requesting agent shutdown. The exact hook passed a bounded synthetic native
Xperia 5.2.0.20 check; this was not installation/removal of the new RPM.

The candidate is built, signed and delivered to the existing unpublished GitHub
drafts: runtime 2.5.24-0.7, pass 1.7.4-0.6 and OTP 1.2.0-0.6, reusing tree/OATH.
SDK signature verification and separate cryptographic assistant review passed
for all eleven RPMs with fingerprint `F48588CC6061DAC0C4C09F8734370471919C29A5`.
The compact [candidate manifest](docs/development/release-candidate-20261017.json)
also passed separate assistant review. Historical records and source pins remain.

Prepared PRs, all awaiting maintainer review (none merged):
- [Workspace #16](https://github.com/misja/sailfish-workspace/pull/16)
- [Runtime #22](https://github.com/misja/sailfish-gnupg-runtime/pull/22)
- [Password store #12](https://github.com/misja/sailfish-password-store/pull/12)

Unpublished drafts, with the Release Manager's existing texts:
- [Runtime draft](https://github.com/misja/sailfish-gnupg-runtime/releases/tag/untagged-8a6ad3eb9eb59c1e39d0), source `58dde123489134a67e92306ce46d6c097ce1b8f7`, three assets.
- [Password-store draft](https://github.com/misja/sailfish-password-store/releases/tag/untagged-a89114055f9e9007f236), source `a3b6b03d0340f12c4c7d5062c118357cc2bdcfb9` (reviewed source commit in PR #12), ten assets.

Only signed binary/source RPMs and public certificates are offered; replaced RPMs
and checksum/signature files are removed. All thirteen downloaded assets match
local delivery hashes. Separate technical assistant review on 2026-10-18 found
no blocker in draft metadata, exact source/spec identities, texts, assets or
independently recomputed download hashes. This is not a human security audit or
publication approval. Evidence and delivery files remain in
`.local-artifacts/release-20261017-cli/`, including `download-verification.json`,
`*-draft-after.json` and `cleanup-verification.json`. Both specified temporary
tool directories have been removed; delivery files and evidence are preserved.

The Release Manager owns the final delivery handoff in workspace #2 and runtime
#3. Next owner: Misja for PR review and any later explicit publication decision.
Nothing is merged or published; no new installation, device change, rebuild or
repetition of completed tests was performed in this completion round.
The coordinated runtime/pass/OTP transition passed an isolated SDK RPM database
check; it was not an installed-device package transaction. Earlier synthetic
Xperia evidence retains its bounded scope. Runtime/pass/OTP must be upgraded
together; public pass ownership and GNU Bash/provider constraints remain.

## Maintained decisions and earlier evidence

Pass/OTP upstream review is complete; release bases remain pass 1.7.4 / OTP 1.2.0
with the two selected upstream backports. Fork pins/patch snapshots remain intact.
[Earlier build evidence](docs/development/clean-sdk-build-20261015.md) and component
records retain their original artifact identities; do not overwrite them.

AGENTS baseline 1.3.0 requires research of actual upstream/platform behavior
before adding constraints or mechanisms, also for delegated agents. Distinct
Release Manager and independent technical review remain mandatory where relevant.
Native graphical integration has separate provenance/provider work; it is not
part of the CLI release. Public pass command ownership/Bash-provider choices
remain user-visible constraints. Use the existing issues for decisions.
