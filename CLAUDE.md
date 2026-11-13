# CLAUDE.md

The rules for working in this repository live in `AGENTS.md`. It is imported below and loaded
into context in full; nothing is duplicated here.

@AGENTS.md

## Claude Code

- To verify the import: `/context all` → the **Memory files** section must contain `AGENTS.md`.
- This file exists for sessions that do not read `AGENTS.md` directly: Claude Code before
  v2.1.277, the **Project instructions = `claude-md`** mode, and tools that expect `CLAUDE.md`.
  The import and direct reading of `AGENTS.md` do not stack — the file is not loaded twice.
- No rules of our own here: `AGENTS.md` is the single source of truth, otherwise the
  instructions would start to contradict each other.
