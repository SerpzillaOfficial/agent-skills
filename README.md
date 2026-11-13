# Agents skill: Serpzilla SEO Guest Posting

A vendor-neutral home for **Agent Skills** — portable skill packages that follow the open
[Agent Skills](https://agentskills.io) standard. Each skill is a folder containing a `SKILL.md`
file (with `name` + `description` metadata) plus optional `references/`, `scripts/`, and
`assets/`. Any compatible agent can load them: Claude, OpenCode, Cursor, OpenAI Codex,
Gemini CLI, and many others.

## Skills

| Skill | Description |
|-------|-------------|
| [`serpzilla-seo-guest-posting`](skills/serpzilla-seo-guest-posting) | Buy SEO guest posts and link insertions on trusted donor sites via the Serpzilla platform. |

---

## Serpzilla SEO Guest Posting

This skill enables an agent to automate backlink acquisition through
[Serpzilla](https://serpzilla.com): create projects, search and filter donor sites by
DR / traffic / price / language, upload articles, purchase placements, and manage the
placement lifecycle. It requires the **Serpzilla MCP server** to be connected to the agent.

### Features

- Create projects for promoted websites
- Search and filter donor sites (price, DR, traffic, language, Majestic/Moz/Ahrefs/Semrush metrics, …)
- Upload articles for moderation (`news` format)
- Buy four placement types: `news`, `review`, `link`, `archive`
- Manage purchased placements (approve, cancel, terminate, …) with built-in financial guardrails

### Quick install in Claude (plugin)

The repository also serves as a Claude plugin marketplace. The
`serpzilla-seo-guest-posting` plugin ships both the skill and the Serpzilla MCP connection.

- **claude.ai / Claude Desktop:** *Customize → Plugins → Add → Add marketplace*, paste
  `https://github.com/SerpzillaOfficial/agent-skills` and add the
  `serpzilla-seo-guest-posting` plugin. Then open the plugin → **Connectors** tab → add and
  connect `serpzilla` (OAuth sign-in) — without it the skill is installed but Serpzilla tools
  are unavailable.

- **Claude Code (CLI, desktop app, VS Code):**

```
/plugin marketplace add SerpzillaOfficial/agent-skills
/plugin install serpzilla-seo-guest-posting@serpzilla
```

  The second command opens the plugin card — choose the installation scope (user / project /
  local). OAuth starts on the first call to a Serpzilla tool.

Plugins from third-party marketplaces do not update automatically — update via `/plugin` →
**Update now** or `claude plugin update serpzilla-seo-guest-posting@serpzilla`.

If the Serpzilla MCP is already connected manually, disable one of the two to avoid duplicate
tools.

For other agents and for claude.ai (uploading the skill as an archive), use the manual
installation below.

### 1. Connect the Serpzilla MCP

The Serpzilla MCP is a hosted **streamable HTTP** server. Connect it using only the URL —
authentication is handled by a built-in OAuth flow, so no API token needs to be pasted into
the agent config.

```
https://mcp.serpzilla.com/mcp
```

How you add it depends on your agent. For example, in **Claude Desktop** open
*Settings → Developer → Edit Config* and add it to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "serpzilla": {
      "type": "http",
      "url": "https://mcp.serpzilla.com/mcp"
    }
  }
}
```

> On older clients that predate streamable HTTP, use `"type": "sse"` instead of `"http"`.
> On claude.ai, add it under *Settings → Connectors* using the same URL.

### 2. Install the skill

Ready-made archives are published in
[Releases](https://github.com/SerpzillaOfficial/agent-skills/releases/latest). You do not need
to package anything yourself — download the one you need:

| Where you install it | Archive |
|---|---|
| **claude.ai / Claude Desktop** (*Customize → Skills → Upload a skill*) | [`serpzilla-seo-guest-posting-claude-web.zip`](https://github.com/SerpzillaOfficial/agent-skills/releases/latest/download/serpzilla-seo-guest-posting-claude-web.zip) — with a short description that fits the claude.ai limit (200 characters) |
| **Other agents** following the [Agent Skills](https://agentskills.io) standard (Cursor, Codex, Gemini CLI, …) | [`serpzilla-seo-guest-posting.zip`](https://github.com/SerpzillaOfficial/agent-skills/releases/latest/download/serpzilla-seo-guest-posting.zip) — the source skill unchanged |

Every release also contains archives with the version in the name (for example
`serpzilla-seo-guest-posting-1.1.0.zip`) if you need a specific version. For Claude Code it is
easier to install the plugin — see “Quick install” above.

Build the archive yourself

```bash
python3 scripts/package_skill.py --output dist
```

The script checks version consistency and description limits, then builds all four ZIP archives
with the skill folder as the archive root (as the standard requires). Only Python 3 with the
standard library is needed.

### 3. Use it

Ask the agent in natural language, e.g. *"Find donor sites with DR 30+ for my site
example.com and buy a guest post under $50."* The skill guides the agent through the workflow
and enforces confirmation before any purchase or money-moving action.

You still need a Serpzilla **advertiser** account; get an API token in
[Passport → Security](https://passport.serpzilla.com/security/token/). Top up your balance at
<https://passport.serpzilla.com/deposit/>.

## Repository contents

```
agent-skills/
├── README.md                              # this file (repo-level, not part of the skill package)
├── AGENTS.md                              # rules for AI agents working in this repository
├── CLAUDE.md                              # pointer to AGENTS.md for Claude Code (@AGENTS.md import)
├── VERSIONS.md                            # skill versions and release notes
├── .gitignore
├── .mcp.json                              # Serpzilla MCP connection shipped with the plugin
├── .claude-plugin/
│   ├── marketplace.json                   # Claude plugin catalog (marketplace "serpzilla")
│   ├── plugin.json                        # manifest of the serpzilla-seo-guest-posting plugin
│   └── icon.png
├── .github/workflows/
│   ├── release.yml                        # tag vX.Y.Z, build archives and publish a release (push to main)
│   └── check-versions.yml                 # version and description checks (PR)
├── packaging/
│   └── claude-web-description.txt         # short skill description for claude.ai (≤ 200 characters)
├── scripts/
│   ├── package_skill.py                   # version checks and ZIP archive build
│   └── check_versions.py                  # PR checks: versions, VERSIONS.md, description limits
└── skills/serpzilla-seo-guest-posting/    # the skill package
    ├── SKILL.md                           # metadata + workflow instructions
    └── references/
        └── placement_actions.md           # placement actions & statuses reference
```

## Releasing a new version

1. Bump the version **identically in three places**: `version` in
   `skills/serpzilla-seo-guest-posting/SKILL.md`, in `.claude-plugin/plugin.json` and in the
   plugin entry of `.claude-plugin/marketplace.json`.
2. Update `VERSIONS.md`: the version and date in the table, and add a `### X.Y.Z (date)` section
   on top. Its first line becomes the release title (`vX.Y.Z — …`), the rest — the release
   description. It is public: write for users, no internal names.
3. If the skill `description` changed, update the short description in
   `packaging/claude-web-description.txt` — that is what claude.ai sees.
4. Merge the PR into `main`. GitHub Actions tags `vX.Y.Z`, builds the archives from the tag
   commit and creates the release; notes come from `VERSIONS.md`.

On every PR the *Check Versions* workflow verifies without publishing: versions match across all
files, the row and section in `VERSIONS.md` exist, description limits (1024 characters in
`SKILL.md` and 200 in the claude.ai short description) hold, and a PR changing skill or packaging
files (`skills/`, `packaging/`) bumps the version. Changes without a new version do not create a
release: if `skills/` or `packaging/` changed after the current version tag and the version was
not bumped, the release workflow fails. Re-running the release workflow never moves an existing
tag — it only rebuilds and replaces the ZIP archives.

## See also

- [Agent Skills standard](https://agentskills.io) — the open format these skills follow
- [How to create custom skills (Claude Help Center)](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Serpzilla API documentation](https://serpzilla.com/api/)
- [MCP server source (Docker/stdio variant)](https://github.com/stanislav-reshetnev/serpzilla-mcp-server)
