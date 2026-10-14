# Sailfish workspace

Shared documentation and development tools for GnuPG and pass/OTP packaging on Sailfish OS.

| Repository | Purpose |
| --- | --- |
| [sailfish-workspace](https://github.com/misja/sailfish-workspace) | Working agreements, architecture and shared SDK infrastructure |
| [sailfish-gnupg-runtime](https://github.com/misja/sailfish-gnupg-runtime) | Isolated GnuPG runtime and native pinentry integration |
| [sailfish-password-store](https://github.com/misja/sailfish-password-store) | pass, pass-otp and supporting package integration |

Start with the [documentation index](docs/index.md) or [working agreements](docs/development/workflow.md). Issues belong to the repository responsible for the work; the shared [Sailfish project board](https://github.com/users/misja/projects/2) provides an overview. SDK helpers are in infrastructure/sdk/.

[Upstream adaptations](docs/development/upstream-forks.md) use forks with pinned
commit bases; these repositories contain our packaging and integration work.

The package projects are experimental. Support for a particular device or OS version requires testing on that target.

Development uses AI-assisted tools. Misja Hoebe (@misja) reviews changes and decides what is merged or released; [contribution guidelines](CONTRIBUTING.md) describe the review requirements.

Original work is [GPL-3.0-or-later](LICENSING.md). [Upstream licenses](THIRD_PARTY.md) remain in force.
