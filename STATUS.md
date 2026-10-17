# Session handoff

Updated: 2026-10-17. Decision owner: Misja Hoebe (@misja).
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

The new candidate has been built and inspected in the existing SDK, reusing
unchanged tree/OATH outputs and pinned upstream sources. Current GitHub drafts
still contain the signed 0.6 runtime / 0.5 pass/OTP candidate pending refresh.
Artifact/signature review of all eleven new RPMs, including source RPMs, is
complete: SDK signature verification and separate cryptographic assistant review
passed with fingerprint `F48588CC6061DAC0C4C09F8734370471919C29A5`. Nothing is published.

Next: Builder records the compact 2026-10-17 candidate manifest from existing
evidence; the independent reviewer assesses it before branches/commits/PRs and
the coordinated draft refresh. Acceptance: preserve existing changes and source
pins, signed RPM/SRPM plus public-key assets only (3 runtime, 10 password-store),
verify all thirteen downloads, and independently check draft metadata. No merge,
publication, rebuild, new installation or device change is authorized.
The coordinated runtime/pass/OTP transition passed an isolated SDK RPM database
check; it was not an installed-device package transaction. The Release Manager
owns the updated documentation and notes, including related-component links.
No full Xperia retest, upstream update, tool framework or automatic publication.

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
