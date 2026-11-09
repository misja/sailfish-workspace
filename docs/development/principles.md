# Engineering principles baseline

Version: 1.5.0. Adopted 2026-10-10; 1.1.0 adds Sailfish app conventions (2026-11-06); 1.2.0 adds the Sailfish UI check in reviews (2026-11-06); 1.3.0 adds the app icon guidance (2026-11-08); 1.4.0 adds platform mechanisms in code (2026-11-08); 1.5.0 adds personal information (2026-11-09). Source: accepted Phase A constitution proposal. This is a shared baseline, not a generated Spec Kit constitution.

1. **Evidence before assertion.** Separate supplied observations, dated external facts, recommendations and unknowns. Pin build inputs; maintain source/patch/license provenance. Absence of search results is not proof of absence.
2. **System coexistence.** Community packages must not replace Jolla components. Private runtime isolation covers loader paths, binaries/helpers, RPM resolution, configuration, IPC and upgrade/removal. Demonstrate it through independent evidence.
3. **No real secrets in engineering systems.** Agent, CI and test artifacts use synthetic keys/stores and published test vectors only. Never inspect or log real private keys, passwords, OTP URIs/seeds or recovery material.
4. **Native, bounded secret handling.** Prefer supported APIs and maintained crypto implementations. Validate paths/input, avoid secret argv/env and persistent plaintext, control cache/clipboard/lifecycle exposure. Document limits rather than claim absolute protection.
5. **Independent release verification.** Builders self-test; an independent reviewer checks crypto behavior, packaging isolation and release-critical exposure. Unresolved failures are explicit blockers; no self-approved security/release sign-off.
6. **Reproducible and maintainable inputs.** Sources, targets and patches are reviewable/pinned. Compare clean builds before claiming byte reproducibility. Security dependency changes require analysis and regression evidence.
7. **Clear ownership, minimal process.** One accountable task owner; role activation must add value. One blocker clarification round-trip, then decision-owner escalation. Concise artifact handoffs; one shared spec/plan/task set.
8. **Sparse firm human gates.** Follow the approved scope; do reversible routine work autonomously. Architecture bootstrap, exceptional security/system/destructive changes, device changes and external publication require explicit scoped authorization.
9. **Independent projects.** Apps/packages own their histories, tests and releases. Shared infrastructure serves unrelated Sailfish projects; create common runtime/UI libraries only after demonstrated reuse.

## Platform conventions

Use existing Sailfish, RPM and upstream lifecycle facilities before adding
project-specific mechanisms. Normal users must not inspect or kill processes to
install, update or remove packages. Check the actual target versions and macro
implementations: a familiar macro name is not proof it performs the required
action. Any departure from maintained platform/upstream practice needs a concrete
justification and maintainer agreement before implementation.

Research is a prerequisite to introducing new constraints, not an optional check
after a maintainer questions them. Record the relevant upstream/platform behavior,
the actual unsolved problem and the simpler alternatives in the existing issue.
Independent reviewers must question the necessity of the requirements themselves.
Apply this to the primary assistant and delegated agents; AGENTS baseline 1.3.0
makes it a persistent instruction in each project checkout.

## Platform mechanisms in code

Code is written to be reviewed, maintained and learned from by people. Use the
platform's own mechanisms instead of tricks or home-made replacements.

- **Look first:** before writing a component, model, loader or workaround,
  check the target SDK for the standard one and cite where it was found. The
  `qmldir` of `Sailfish.Silica` and the Qt headers of the target version are
  the evidence; the documentation alone is not.
- **Prefer the standard mechanism:**
  - Silica components (for example `ExpandingSection`) over look-alikes;
  - Qt model classes (for example `QSortFilterProxyModel`) over hidden or
    zero-height rows;
  - properties with NOTIFY signals over binding tricks or counters that force
    re-evaluation;
  - explicit parameters over behaviour derived from string contents;
  - reacting to the actual change (a height, a signal) over timers that guess
    when layout is done.
- **No standard mechanism?** State the gap and ask the maintainer before
  building an own solution.
- **Name what remains:** list any remaining own solutions in the pull request,
  unprompted, with the reason.
- **Reviews check this:** independent reviewers name tricks and own solutions
  explicitly. Replacing them later costs more than avoiding them.

## Personal information

Repositories and everything published from them are public. The local
machine is not. This boundary is firm: local facts stay local.

- **What is public:** anything that leaves the machine. That covers:
  - git objects: commits, tags, branch names and tag annotations;
  - everything on GitHub: issues, pull requests, comments, reviews,
    releases and their assets, and the project board;
  - built packages and their metadata;
  - OBS and Chum;
  - any shared artifact or link.
- **Roles, not people:** project artifacts name roles: "the maintainer", "a
  contributor", "a reviewer". Decisions and quotes are attributed to "the
  maintainer", with a date. No possessives or personal descriptions: write
  "the test player", not "the maintainer's player", and use no gendered
  pronouns.
- **No third parties from our own process:** what we write ourselves never
  names or identifies other people: helpers, account holders, household
  members, other users. Use their role, for example "an OBS account". The
  only names that appear are the ones in information that comes from
  outside and is reproduced as it is: a licence or copyright notice, or a
  cited upstream source (`owner/repo@commit`). Upstream projects,
  organisations and trademarks (for example Jolla, Lenbrook, BluOS) may be
  named.
- **No local values:** never record a value observed on the maintainer's
  network or devices. That covers:
  - IP and MAC addresses;
  - host, container-instance and share names;
  - player and room names, and Wi-Fi names;
  - account names on devices, and serial numbers;
  - e-mail addresses.

  Examples use reserved values: IPv4 from `192.0.2.0/24` (RFC 5737), MACs
  such as `02:00:00:00:00:0A`, `example.invalid`. Otherwise use placeholders
  such as `<player>`, `<phone>` or `<host>`.

  These may be named, as reproducibility evidence: device models, OS and
  firmware versions, and the SDK's own default users and paths (for example
  `/home/ubuntu/...` in the SDK container). Aggregate counts are allowed;
  titles from a library are not.

  The real values live in a file outside every repository on the
  maintainer's machine. Agents read it when they need it, and never quote it
  into project artifacts or commit messages.
- **Screenshots, logs and fixtures:** screenshots, logs and evidence are
  published only after they have been checked for these details. Raw logs
  stay local. Fixtures are synthetic or scrubbed captures.
- **Required identity stays, and only there:**
  - copyright and licence notices (LICENSE, LICENSING.md, THIRD_PARTY.md,
    file headers);
  - packaging metadata (`DeveloperName`, the changelog author);
  - git author and committer identity;
  - the account name in repository URLs, and in identifiers derived from it
    (`io.github.<account>`).

  Prose elsewhere (README, CONTRIBUTING, STATUS, specs, code comments) uses
  "the maintainer". The git author e-mail is the maintainer's choice; agents
  do not change it or copy it into files.
- **Check before publishing:** check for names and local values before
  every push, pull request, issue or release. If one was published anyway,
  remove it from current files and texts at once, and report it to the
  maintainer. Only the maintainer decides whether history is rewritten.

## Sailfish app conventions

For native apps, follow the platform's published practice rather than project
habits. Read the upstream page for each topic instead of copying it here; the
points below are the ones checked against SDK 3.13.5 / Sailfish OS 5.1 on
2026-11-06.

- **Code style:** [Sailfish OS Coding Conventions](https://docs.sailfishos.org/Develop/Apps/Coding_Conventions/).
  - QML: order the id, properties, signals, then bindings/functions/handlers,
    then children; put braces on one-line conditionals; omit redundant default
    values and unused ids; group properties (`anchors {}`); prefix private API
    with `_`.
  - C++: Qt5 connect syntax, ranged-for, CamelCase namespaces, Qt coding
    style; the app stub is named after the app, not `main.cpp`.
  - Tests: prefer compare over verify, and signal spies over fixed waits.
- **Navigation and components:** Silica pages, page stack, attached pages and
  pulley menus as in the [navigation guideline](https://sailfishos.org/design/navigation)
  ("below five" pulley options). Pages default to portrait: set
  `allowedOrientations` on each page that should rotate.
- **Agree the UI before building it:** before writing screens, agree the
  whole-app structure and navigation with the maintainer using mockups,
  covering later features as well as the current one. Record the agreed
  structure in the feature spec. A changed structure is a scope change.
- **UI quality:** use the [UI Definition of Done](https://docs.sailfishos.org/Develop/Apps/UI/Definition_of_Done/)
  as the checklist and the [Silica common pitfalls](https://sailfishos.org/develop/docs/silica/sailfish-application-pitfalls.html)
  as rules.
  - Fonts, colours, margins and item sizes come from `Theme`: text margins
    `Theme.horizontalPageMargin`, touch targets at least `Theme.itemSizeSmall`.
  - Interactive items use the primary colour and turn highlight when pressed;
    static labels and headers use the highlight colour.
  - Images sit flush with the page edges.
  - Every view that can overflow has a scroll decorator.
  - Use gestures and pulley menus instead of toolbars or back/home buttons,
    with no more than four pulley items, hidden when all are disabled.
  - Dialogs accept and cancel through `DialogHeader`. Text fields have a
    `label` and `placeholderText`, and an EnterKey that is enabled only for
    valid input.
  - The cover summarises state and offers shortcuts for common actions.
  - No empty or unfinished states. The user can recover from errors such as no
    network.
  - Transitions are smooth, and memory use is reasonable (measure on a device).
  - Develop and check on a real device.
- **Sailfish UI check in reviews:** no separate UX role. The existing
  separate reviews also check UI against the Sailfish guidelines and Silica
  components above.
  - **Design review:** the agreed mockups.
  - **Result review:** the built pages.
  - **What is checked:** navigation and attached pages; pulley, context-menu
    and remorse use; empty, error and offline states; landscape; Theme sizes
    and colours; and reuse of Silica components rather than own replacements.
    Jolla's own apps (People, Media) serve as references where the guidelines
    are silent.
  - **Generic web UI/UX checklists and skills** do not know these conventions
    and are not a substitute.
  - **The maintainer's device check** remains the final UI judgement.
- **App icons:** follow the [app icon guidance](app-icons.md): an official
  base shape from the Sailfish icon template, one clear metaphor, and an
  editable SVG as the single source from which the PNGs are rendered. The
  maintainer chooses the design and checks it in the launcher on a device.
- **Localisation:** use libsailfishapp's `sailfishapp_i18n` (`lupdate
  -noobsolete`, `lrelease -nounfinished`, catalogues in
  `/usr/share/<app>/translations`, loaded for the system locale at start). Do not
  build an own translation loader. English is the source. libsailfishapp
  loads only the system locale's catalogue and has no English fallback
  (sailfishapp_priv.cpp, checked 2026-11-08); apps do not add one.
  `qsTr` is the SDK template default; `qsTrId` with `//%`/`//:`
  (`sailfishapp_i18n_idbased`) is what Jolla's own apps use. Choose per app and
  record the choice. The community [L10n process](https://docs.sailfishos.org/Develop/L10n/)
  (Pootle) covers platform strings, not third-party apps.
- **Packaging:** start from the SDK's own app template. Run the SDK's Harbour
  validator (`sfdk check -s harbour`) on every release RPM. It rejects files
  outside `/usr/share/<app>` and the desktop/icon paths (including `%license`),
  so tests and fixtures are never packaged.

