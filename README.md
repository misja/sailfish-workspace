# Sailfish workspace

A development workspace for Sailfish OS projects: shared working agreements,
source checkout tools and SDK helpers. Current projects package a separate
GnuPG runtime and the pass/OTP command-line password store.

To develop or build, start with [setup on another machine](docs/development/getting-started.md).
This repository does not install the applications. For packages and usage,
start with [GnuPG runtime](https://github.com/misja/sailfish-gnupg-runtime) or
[pass/OTP](https://github.com/misja/sailfish-password-store).

| Repository | Purpose |
| --- | --- |
| [sailfish-workspace](https://github.com/misja/sailfish-workspace) | Working agreements, architecture and shared SDK infrastructure |
| [sailfish-gnupg-runtime](https://github.com/misja/sailfish-gnupg-runtime) | Separate GnuPG package alongside Jolla’s GnuPG; native integration work is separate |
| [sailfish-password-store](https://github.com/misja/sailfish-password-store) | Password/OTP CLI packages, their launchers and supporting tools |

Our GnuPG runtime uses separate commands, libraries, keys and an agent. Pass
uses that runtime but installs the public `pass` command. Integration with
Jolla’s graphical password prompts is separate work in the
[Sailfish Secrets compatibility branch](https://github.com/misja/sailfish-secrets/tree/sailfish/native-pinentry-compat). Source changes are maintained
in [upstream forks](docs/development/upstream-forks.md); packaging and shared
tooling live in the repositories above.

See the [documentation index](docs/index.md) and [working agreements](docs/development/workflow.md).
Issues belong to the repository responsible for the work; the shared
[Sailfish project board](https://github.com/users/misja/projects/2) provides an overview.
SDK helpers are in infrastructure/sdk/.

Development uses AI-assisted tools. Misja Hoebe (@misja) reviews changes and decides what is merged or released; [contribution guidelines](CONTRIBUTING.md) describe the review requirements.

Original work is [GPL-3.0-or-later](LICENSING.md). [Upstream licenses](THIRD_PARTY.md) remain in force.
