# Session handoff

Updated: 2026-10-14. Maintainer: Misja Hoebe (@misja).
Live task: [workspace issue #5](https://github.com/misja/sailfish-workspace/issues/5).
The [project board](https://github.com/users/misja/projects/2) owns current work state.

The preflight and runtime notice-staging fix are merged. This session prepares
portable public source authentication/staging and configurable SDK build paths
in separate workspace/runtime/password-store review branches. Eleven existing
archive identities are preserved. Online preparation and offline reverification
passed; generated inputs stay outside Git. The issue records review revisions
and remaining acceptance work.

SDK baseline follows official guidance, normally Docker directly on Linux.
Misja's LXC -> Ubuntu -> Docker setup is an optional variant requiring extra work.
The existing SDK reports 3.13.5 and 5.1.0.11 targets. No package build, SDK/target
installation, device change or upstream submission has been performed in this slice.

See [public source bootstrap](docs/development/source-bootstrap.md).

Fresh-public-clone evidence: [source validation](docs/development/source-bootstrap-validation-20261014.md).
