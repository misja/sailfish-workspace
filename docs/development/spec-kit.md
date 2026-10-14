# Spec Kit and the workspace bootstrap

Spec Kit helped bootstrap the initial organization and package feature artifacts.
The recorded tool was github/spec-kit v1.1.3, commit
0282d03eb6fc3091b3deaa3a855d4030dc40cd6c. This is the recorded version,
not a claim that it remains the latest release.

The 2026-10-10 local evaluation installed specify-cli with uv, generated a
Codex integration trial, checked skill discovery and exercised feature/plan/task
scaffold scripts. Feature documents were completed manually. This was not an
end-to-end model-driven workflow or independent security audit.

The public workspace carries the resulting working agreements, staged role
policy, architecture, bootstrap spec/plan/tasks and plain Markdown templates.
The original local trial, raw reports, generated .agents skills and component
.specify state were not in the initial public export. A clone does not recreate
the old machine's CLI installation, assistant skills or active feature state.

## Continue without installing anything

Use the feature templates under infrastructure/templates/features/ in the
responsible repository. Keep one spec/plan/tasks set for a substantial feature;
GitHub issues and PRs remain the work tracker. The public bootstrap record was
written from the accepted organization decisions and dated local integration
record; it is a curated handoff, not a copy of generated Spec Kit state.
AGENTS.md is optional assistant guidance. Human contributors start at
CONTRIBUTING.md.

## Optional pinned Spec Kit setup

Use the [official pinned source](https://github.com/github/spec-kit/tree/0282d03eb6fc3091b3deaa3a855d4030dc40cd6c)
to inspect installation and integration commands. With uv and a compatible
Python already installed, the original exact-source installation was:

~~~sh
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@0282d03eb6fc3091b3deaa3a855d4030dc40cd6c --python /usr/bin/python3 --no-python-downloads
specify version
specify init --help
~~~

This downloads software. The source commit is pinned, but transitive Python
dependencies are not a fully hash-locked environment. Installation is optional
and is not performed by the workspace checkout helper.

Generate integration assets in a disposable new directory first, using the
integration/script flags documented by that pinned version. Review them before
bringing assets into an existing project; preserve its constitution, AGENTS.md,
feature documents and branch. No trial sibling path is required by this repo.
Do not regenerate over an existing project merely to continue its documents.
Follow your assistant's current project-skill discovery instructions if used.

Spec Kit prompts, role names and parallel task markers do not authorize
delegation, software/device changes, upstream submissions or releases.
