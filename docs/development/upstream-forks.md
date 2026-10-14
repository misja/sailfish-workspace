# Upstream forks and packaging repositories

We adapt upstream code in forks and keep the package recipes, runtime wrappers
and integration tests in the Sailfish packaging repositories.

| Upstream | Fork | Adaptation |
| --- | --- | --- |
| Sailfish Secrets | [misja/sailfish-secrets](https://github.com/misja/sailfish-secrets) | Native pinentry compatibility; separate cache-free prototype |
| password-store | [misja/sailfish-pass](https://github.com/misja/sailfish-pass) | Private GnuPG binding and BusyBox-compatible listing |
| pass-otp | [misja/pass-otp](https://github.com/misja/pass-otp) | Standard-input secret handling and packaged OATH backend |

Each adaptation branch starts from a pinned upstream commit and preserves the
upstream history. [The source map](upstream-forks.json) records exact bases,
heads and comparison links. Review our changes against that base. New upstream
versions require an explicit update and affected regression checks.

GnuPG, tree and OATH are currently unmodified upstream inputs; they do not need
forks. Packaging still authenticates the locked upstream archives and applies
the recorded patches. Using a patched fork archive as well as those patches
would apply the changes twice, so the source-fetch/build recipe is not changed
implicitly by the fork migration.

The forks retain upstream licenses and copyright notices. Original standalone
integration tools and documentation use GPL-3.0-or-later. A fork does not
establish the exact source provenance of a vendor binary.

Issues stay in the responsible packaging repository or sailfish-workspace,
with the Sailfish project as the shared overview. Fork issues and Actions are
disabled to avoid extra trackers and unapproved builds. No upstream PR has been
submitted. Any upstream submission needs approval of the exact branch/revision.

The native packaging repository materializes prototype source inputs from the
pinned fork commits instead of tracking copied C++ trees. Source locks preserve
the same input and output bytes.

For local work, clone the repositories into sibling directories named workspace,
gnupg-runtime, password-store and sailfish-secrets. Set upstream to the original
project in each fork; origin points to the fork. The pinentry materializer also
accepts an explicit checkout path.
