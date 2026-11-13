# Serpzilla SEO Guest Posting — versions

The current skill version. Agents can compare it with their local copy to check for updates.

A `### X.Y.Z (date)` section from "Latest changes" becomes the title and description of the
GitHub release `vX.Y.Z`. Write for users of the skill: what changed and what they need to do.
Add new versions on top.

| Skill | Version | Updated |
|-------|---------|---------|
| serpzilla-seo-guest-posting | 1.1.0 | 2026-11-13 |

## Latest changes

### 1.1.0 (2026-11-13)

Claude plugin marketplace, ready-to-install release archives and agent documentation.

- Install the skill in Claude Code as a plugin: `/plugin marketplace add SerpzillaOfficial/agent-skills`,
  then `/plugin install serpzilla-seo-guest-posting@serpzilla`. `.mcp.json` connects the
  Serpzilla MCP together with the plugin.
- Every release ships four ZIP archives: `serpzilla-seo-guest-posting.zip` for agents that follow
  the Agent Skills standard and `serpzilla-seo-guest-posting-claude-web.zip` for claude.ai and
  Claude Desktop, plus copies with the version in the name.
- Added `AGENTS.md`, `CLAUDE.md`, `VERSIONS.md` and automated version checks in CI. The skill
  content itself is unchanged.
