# Portable Sailfish workspace bootstrap

Owner/decision owner: Misja Hoebe (@misja).
Related review: https://github.com/misja/sailfish-workspace/issues/4.
Record: curated 2026-10-14 from the initial Spec Kit-assisted organization.

A contributor on another machine needs the repository boundaries, agreements
and source identities without access to the maintainer's private local history.

The workspace must describe its accepted architecture and Spec Kit provenance,
provide a Git/Python-only checkout entry point, use GitHub repository names as
sibling directories, preserve existing local work, and distinguish source setup
from SDK/package readiness. Adaptations must be traceable in upstream forks;
packaging snapshots must reproduce the complete pinned fork trees.

Acceptance: fresh six-repository checkout and repeat invocation work; existing
work and unexpected origins are protected; fork pins are checked; the eight
packaging patches reproduce all three pinned source trees; both pinentry variants
materialize their declared local headers. Public documentation has valid local
links and explains optional Spec Kit continuation without generated private state.

SDK installation, automatic dependency upgrades, production device validation,
package releases and upstream submission are outside this bootstrap.
