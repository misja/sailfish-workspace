# Start on another machine

For documentation, planning and source changes, install Git and Python 3.9 or
later. Public repositories can be cloned over HTTPS without a GitHub account.
A GitHub account with suitable repository access is needed to push changes;
GitHub CLI is optional. Configure your own Git author identity.

~~~sh
mkdir -p ~/code/sailfish
cd ~/code/sailfish
git clone https://github.com/misja/sailfish-workspace.git
python3 sailfish-workspace/tools/workspace.py clone --dry-run
python3 sailfish-workspace/tools/workspace.py clone
python3 sailfish-workspace/tools/workspace.py status
python3 sailfish-workspace/tools/packaging-patches.py
~~~

During review, the new workspace tools are on PR #3, not main. To try them
before merge, clone with --branch chore/upstream-forks. The helper still
clones the other own repositories on main; use their migration branches to
review runtime PR #6 and password-store PR #3 before running patch verification:

~~~sh
git -C sailfish-gnupg-runtime switch chore/upstream-forks
git -C sailfish-password-store switch chore/upstream-forks
~~~

These review instructions can be removed once all three migration PRs are merged.

[manifest.yml](../../manifest.yml) is JSON-formatted YAML so the helper needs
no third-party Python modules. It declares six sibling directories matching
their GitHub names. New own repositories start on main. New fork checkouts
start at the pinned adaptation commit, detached; create a branch before editing.
The helper adds upstream remotes for forks. Existing checkouts are checked and
reported without pulling, changing their branch or modifying their worktree.
Origin mismatches and repository symlinks stop the operation during preflight.
Rerunning the helper is safe for an existing working directory.

Read [working agreements](workflow.md), [architecture](../adr/0001-workspace.md)
and the responsible repository's CONTRIBUTING.md and STATUS.md. Issues and the
[project board](https://github.com/users/misja/projects/2) hold current work;
STATUS is a concise handoff. Existing package work belongs in its own repository.
For a new Sailfish component, first decide its boundary in a workspace issue,
then add the approved repository to the manifest. Do not copy the workspace
into each component.

For substantial changes, keep a spec, plan and tasks with the responsible
component. [Templates](../../infrastructure/templates/features/spec.md) and
[Spec Kit provenance](spec-kit.md) are available; neither an AI tool nor Spec Kit
is required. The workspace bootstrap's [design record](../../specs/001-workspace-bootstrap/spec.md)
explains the initial organization.

## SDK and package work

This checkout setup is not SDK provisioning. The existing helpers in
infrastructure/sdk/ describe a particular LXD/Docker-based experiment, not a
portable automatic installer. They require host-specific review before use;
inspect-host.sh includes sudo inventory queries. Do not run those scripts as
a general workstation setup.

Package tools still include fixed /home/ubuntu SDK paths and historical source
verification/evidence prerequisites. Those paths are inside the SDK environment,
not the host checkout layout. See each package's docs/EXPORT_SCOPE.md.
A fresh public clone is sufficient for ordinary source/planning work, but a
clean-checkout package build, SDK installation and device acceptance remain
separate unfinished work. Do not copy private evidence or real stores to fill
missing inputs. [Release targets](release-targets.md) distinguish historical
results from current target acceptance.

Track the remaining SDK/public source setup in
[workspace issue #5](https://github.com/misja/sailfish-workspace/issues/5).
Bootstrap validation is recorded [separately](bootstrap-validation-20261014.md).
