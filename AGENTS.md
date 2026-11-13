# AGENTS.md

Rules for AI agents working in this repository.

## Repository overview

This repository contains **Agent Skills** — portable skill packages that follow the open
[Agent Skills](https://agentskills.io) standard. It currently holds a single skill,
`serpzilla-seo-guest-posting`: buying SEO guest posts and link insertions on donor sites
through the [Serpzilla](https://serpzilla.com) platform.

The repository doubles as a **Claude plugin marketplace** (`.claude-plugin/`), so it has two
audiences: agents that install the skill from a ZIP archive, and Claude Code, which installs
the plugin.

- **Name**: Serpzilla SEO Guest Posting
- **GitHub**: [SerpzillaOfficial/agent-skills](https://github.com/SerpzillaOfficial/agent-skills)
- **Owner**: Serpzilla LTD ([serpzilla.com](https://serpzilla.com))
- **License**: there is no `LICENSE` file in the repository, while `plugin.json` declares
  `MIT`. Do not invent a license and do not add a `LICENSE` file without an explicit request;
  aligning the two is a separate decision.
- **Language**: the skill, documentation and release notes are English; commits are English.

## Repository structure

```
agent-skills/
├── AGENTS.md                              # this file: rules for AI agents
├── CLAUDE.md                              # wrapper importing @AGENTS.md for Claude Code
├── README.md                              # repository documentation (not part of the skill package)
├── VERSIONS.md                            # skill version and release notes
├── .mcp.json                              # Serpzilla MCP connection shipped with the plugin
├── .claude-plugin/
│   ├── marketplace.json                   # Claude plugin catalog (marketplace "serpzilla")
│   ├── plugin.json                        # manifest of the serpzilla-seo-guest-posting plugin
│   └── icon.png                           # plugin icon
├── .github/workflows/
│   ├── release.yml                        # tag vX.Y.Z, build archives, GitHub Release
│   └── check-versions.yml                 # PR checks: versions, descriptions, version bump
├── packaging/
│   └── claude-web-description.txt         # short description for claude.ai (≤ 200 characters)
├── scripts/
│   ├── package_skill.py                   # checks and ZIP archive build
│   └── check_versions.py                  # PR checks
└── skills/serpzilla-seo-guest-posting/
    ├── SKILL.md                           # metadata and workflow instructions
    └── references/
        └── placement_actions.md           # placement actions and statuses
```

## Checks and builds

There are no tests, linters or a separate build: the scripts use the Python standard library
only, and CI runs Python 3.12. Every automated check is one of these commands:

```bash
python3 scripts/package_skill.py --version            # verify versions and print the version
python3 scripts/package_skill.py                      # build 4 ZIP archives into dist/
python3 scripts/package_skill.py --output /tmp/out    # build into another directory
python3 scripts/check_versions.py --base origin/main  # the same check as on a PR
```

`package_skill.py` verifies that the version matches in `SKILL.md`, `.claude-plugin/plugin.json`
and `.claude-plugin/marketplace.json`, that `description` in `SKILL.md` is at most 1024
characters, and that `packaging/claude-web-description.txt` is a single line of at most 200
characters.

`check_versions.py` additionally requires the table row and the `### X.Y.Z (date)` section in
`VERSIONS.md` to match the current version, and requires a PR that changes `skills/**` or
`packaging/**` to bump the version relative to base.

Checks that are not automated and are done by eye:

- JSON in `.claude-plugin/` is valid — `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"`
  (and the same for `marketplace.json`).
- Workflow YAML is not validated anywhere: after editing `.github/workflows/`, do a trial run
  (a PR or `workflow_dispatch`).
- Every file in `references/` is linked from `SKILL.md` — otherwise the agent will not read it.
  `references/placement_actions.md` is currently linked from "5. Manage placements".

## Versioning

The repository has a single version, which is also the skill version. It is stored in four
places and must match everywhere:

| Place | Field |
|---|---|
| `skills/serpzilla-seo-guest-posting/SKILL.md` | `version` in the frontmatter |
| `.claude-plugin/plugin.json` | `version` |
| `.claude-plugin/marketplace.json` | `version` of the `serpzilla-seo-guest-posting` plugin |
| `VERSIONS.md` | the skill row in the table |

Semver rules for this repository:

- **x (major)** — a breaking change to the skill contract: renaming or removing tools, changing
  mandatory workflow steps or placement formats in a way that is incompatible with previous
  instructions.
- **y (minor)** — a new capability: a new scenario, a new placement format, a noticeable
  extension of search filters, or a new installation path (for example, packaging as a Claude
  plugin).
- **z (patch)** — fixes, wording clarifications, formatting, link updates.

Hard rules:

1. The version is bumped **in the same PR** as the skill or packaging change. A separate
   "catch-up" PR is not allowed.
2. The source of truth is `plugin.json`; the script compares the other three places against it.
3. Tags are created **only** by the release workflow. Do not create tags manually (`git tag`,
   `git push --tags`) and do not move existing ones: archives are built from the tag commit, so
   a moved tag would release the wrong code.
4. `VERSIONS.md` is public text: write it for users of the skill, without internal names or
   service details. The first line of a section becomes the release title, so it must read as a
   complete sentence.

## Release pipeline

`release.yml` runs on a push to `main` when one of these paths changes:
`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skills/**`, `packaging/**`,
`VERSIONS.md`. It can also be started manually with `workflow_dispatch`, for example to rebuild
archives.

Step order:

1. **Check unreleased changes.** If the tag for the current version already exists but
   `skills/` or `packaging/` changed after it, the run fails with the list of forgotten files.
   This means the version was not bumped and users of releases will not receive the changes.
2. **Determine the version.** The version is read from `plugin.json`.
3. **Tag.** If the `vX.Y.Z` tag does not exist, it is created on the current commit. If it does
   exist, the tag is not moved and archives are built from the tag commit.
4. **Notes and title.** Taken from the `### X.Y.Z (date)` section in `VERSIONS.md` at the release
   commit. The title is `vX.Y.Z — <first line of the section>` truncated to 100 characters. If
   the section is missing, the release body falls back to `Release X.Y.Z` — a degradation, not
   an error.
5. **Archives and publication.** 4 ZIP files are built from the release commit, the release is
   created (if missing) and the archives are uploaded with `--clobber`, so a repeated run is safe
   and replaces the assets.

`check-versions.yml` runs on PRs (except drafts and `dependabot`) and never publishes: it runs
`check_versions.py` and builds the archives as a dry run.

Changes reach `main` only through pull requests. Required status checks are not enabled: the
workflow is path-filtered, and a PR without skill changes would not report a status. The PR
check is therefore a mandatory process step, not a merge blocker. If a direct push does happen,
the only safety net is step 1 of the release workflow.

## Agent Skills standard

The skill follows the [Agent Skills specification](https://agentskills.io/specification).

### Required frontmatter

```yaml
---
name: serpzilla-seo-guest-posting
version: 1.1.0
description: What the skill does and when to load it.
---
```

| Field | Required | Limits in this repository |
|---|---|---|
| `name` | yes | 1–64 characters, `a-z`, digits and hyphens, matches the directory name |
| `description` | yes | 1–1024 characters (standard), must explain **when** to use the skill |
| `version` | yes | `X.Y.Z`; a repository extension, the standard does not require it |

`name` rules: lowercase only, digits and hyphens; must not start or end with a hyphen; no `--`;
must match the parent directory name.

Valid: `serpzilla-seo-guest-posting`. Invalid: `Serpzilla-SEO`, `-serpzilla`, `serpzilla--seo`.

### Optional skill directories

```
skills/serpzilla-seo-guest-posting/
├── SKILL.md        # required: frontmatter + instructions
├── references/     # detailed references, read on demand
├── scripts/        # executable code (none at the moment)
└── assets/         # templates and data (none at the moment)
```

Keep `SKILL.md` compact: move details, status tables and long lists into `references/` and link
the file from the body of `SKILL.md`. `SKILL.md` is currently about 280 lines; reducing it is
acceptable only together with moving the content into `references/` without losing any rules.

## Writing rules

- The skill and documentation are in **English**; commits are in English.
- Tone: direct and to the point, imperative for instructions to the agent ("call", "check"),
  second person for text about the user.
- Tables for comparisons, statuses and tool arguments. Lists for steps.
- Amounts: use the currency of the user's account (`userWmPriorityCurrency`) and never assume a
  specific one. Placement prices are one-time charges for guest posts and link insertions.
- Tool and field names go in backticks, in their bare form: `get_user_info`, not
  `mcp__serpzilla__get_user_info` (the prefix depends on the host agent).
- The `❌` / `✅` pair is allowed in anti-patterns. Do not use other emoji.
- Do not add promises the API does not make: if behaviour is unknown, verify it or word it more
  carefully.

### About `description`

`description` is the main discovery mechanism for the skill. It must state what the skill does,
when to load it (in the user's words, not a list of synonyms) and, if there is one, the hard rule
that must apply before the body is read.

When changing `description` in `SKILL.md`, also update
`packaging/claude-web-description.txt` — the short description for claude.ai (≤ 200 characters,
a single line). It replaces `description` in the `serpzilla-seo-guest-posting-claude-web.zip`
archive.

## MCP and financial guardrails

All platform interaction goes through the Serpzilla MCP — a hosted streamable HTTP server at
`https://mcp.serpzilla.com/mcp`. Authentication uses OAuth on the first call; the `authorize`
tool is invoked by the server automatically and must not be called by hand. The connection is
declared in `.mcp.json` (plugin) and in the README (manual installation).

**Absolute prohibitions for agents working in this repository:**

- Do not call `purchase_placement` or `perform_placement_action` in tests, checks or "to verify
  the pipeline" — that is the user's real money.
- Do not commit tokens, cookies, logins, project IDs or any account data: the repository is
  public. The skill text must not contain examples with real identifiers.
- Do not try to top up the balance programmatically. Top-ups happen only at
  <https://passport.serpzilla.com/deposit/>, performed by the user by hand.

Rules the skill must follow and that must not be weakened when editing: before any purchase or
money-moving action the agent shows the price, the current balance and the remaining balance
after the purchase, and asks for explicit confirmation. For placement actions it also explains
the consequence (a live backlink can be removed, money can be forfeited). This is the core of
the skill, not decoration.

## Claude Code plugin

The repository is a plugin marketplace: `.claude-plugin/marketplace.json` (name `serpzilla`)
describes the `serpzilla-seo-guest-posting` plugin whose `source` is the repository root.
`.mcp.json` connects the MCP server together with the plugin.

```bash
/plugin marketplace add SerpzillaOfficial/agent-skills
/plugin install serpzilla-seo-guest-posting@serpzilla
```

Plugins from third-party marketplaces do not update automatically — update manually via
`/plugin` → **Update now** or `claude plugin update serpzilla-seo-guest-posting@serpzilla`.

Important for documentation: on claude.ai and in Claude Desktop, installing the plugin does
**not** connect the MCP server automatically. The connector appears in the "Not added" state and
has to be added and connected on the **Connectors** tab of the plugin card. In Claude Code, OAuth
starts on the first tool call.

## Packaging and archives

`package_skill.py` builds 4 archives — two payloads under two names each:

| Archive | Contents |
|---|---|
| `serpzilla-seo-guest-posting-<version>.zip` | the source skill unchanged |
| `serpzilla-seo-guest-posting.zip` | the same, for the permanent `releases/latest/download/...` link |
| `serpzilla-seo-guest-posting-claude-web-<version>.zip` | the same, but with the short `description` from `packaging/` |
| `serpzilla-seo-guest-posting-claude-web.zip` | the same, for the permanent link |

Archive requirements: the skill folder is the **root** of the archive (as the standard requires),
file dates are fixed (the same source produces the same archive), `dist/` is in `.gitignore` and
never lands in the repository. Archives are built only from
`skills/serpzilla-seo-guest-posting/`, so edits to README, AGENTS.md and the scripts do not
change the release contents.

## Git process

Branch names:

- `feat/<what>` — a new skill capability;
- `fix/<what>` — a fix;
- `docs/<what>` — documentation;
- `chore/<what>` — infrastructure, workflows, scripts.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) in English:
`feat: add favorites lists`, `fix: correct placement statuses`, `docs: add AGENTS.md`,
`chore: bump actions to v6`.

Checklist before a PR:

- [ ] The version is bumped identically in `SKILL.md`, `plugin.json`, `marketplace.json` and
      `VERSIONS.md` (if `skills/**` or `packaging/**` changed)
- [ ] `VERSIONS.md` has a `### X.Y.Z (date)` section whose first line works as a title
- [ ] The short description for claude.ai is updated if `description` changed
- [ ] JSON in `.claude-plugin/` is valid
- [ ] Every file in `references/` is linked from `SKILL.md`
- [ ] No secrets, tokens or real account identifiers
- [ ] `python3 scripts/check_versions.py --base origin/main` passes

## Checking for updates

`VERSIONS.md` is the public version checkpoint: agents can compare the version listed there with
their local copy of the skill. If you add update instructions to the skill or README, use this
file rather than `plugin.json`:

```bash
curl -fsSL https://raw.githubusercontent.com/SerpzillaOfficial/agent-skills/main/VERSIONS.md
```

Updates are performed by the user: `git pull` (if the repository is cloned) or re-installing the
archive/plugin. Do not promise auto-updates — third-party marketplaces do not have them.

## Claude Code only

Claude Code supports dynamic command substitution via `` !`command` `` in `SKILL.md`. **Do not
use this syntax in the skill**: other agents will see the literal string instead of the result
and the instruction becomes garbage. If such substitution is needed, use it only in local
project overrides, never in files of this repository.

`CLAUDE.md` at the root is a thin wrapper: an `@AGENTS.md` import and three notes about Claude
Code. It holds no rules of its own, so the instructions cannot contradict `AGENTS.md`.
