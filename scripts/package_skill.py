#!/usr/bin/env python3
"""Build the serpzilla-seo-guest-posting ZIP archives for GitHub Releases.

    python3 scripts/package_skill.py               # build into dist/
    python3 scripts/package_skill.py --output DIR  # build into DIR
    python3 scripts/package_skill.py --version     # only print the version

Before building it checks:
- the version matches in SKILL.md, .claude-plugin/plugin.json and .claude-plugin/marketplace.json;
- description in SKILL.md is at most 1024 characters (Agent Skills standard);
- the short description for claude.ai (packaging/claude-web-description.txt) is at most 200 characters.

Builds two payloads, with the skill folder as the archive root:
- serpzilla-seo-guest-posting-<version>.zip            — the source skill, for Claude Code, Cursor, Codex, etc.
- serpzilla-seo-guest-posting-claude-web-<version>.zip — the same, but with the short description for claude.ai
and copies without the version in the name (serpzilla-seo-guest-posting.zip,
serpzilla-seo-guest-posting-claude-web.zip) for the releases/latest/download/... links in the README.
"""
import argparse
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = "serpzilla-seo-guest-posting"
SKILL_DIR = ROOT / "skills" / SKILL
WEB_DESC_FILE = ROOT / "packaging" / "claude-web-description.txt"
MAX_DESC = 1024
MAX_WEB_DESC = 200
# Fixed file date in archives: the same source produces the same archive.
ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def fail(msg):
    sys.exit(f"error: {msg}")


def read_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"{SKILL_DIR / 'SKILL.md'}: no frontmatter")
    return m


def fm_field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None


def check_versions(skill_text):
    fm = read_frontmatter(skill_text).group(1)
    versions = {f"skills/{SKILL}/SKILL.md": fm_field(fm, "version")}
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    versions[".claude-plugin/plugin.json"] = plugin.get("version")
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entry = next((p for p in market.get("plugins", []) if p.get("name") == SKILL), None)
    if entry is None:
        fail(f".claude-plugin/marketplace.json: no plugin {SKILL}")
    versions[".claude-plugin/marketplace.json"] = entry.get("version")
    if len(set(versions.values())) != 1 or None in versions.values():
        lines = "\n".join(f"  {path}: {v}" for path, v in versions.items())
        fail(f"versions do not match — bump them identically in all three files:\n{lines}")
    return versions[".claude-plugin/plugin.json"]


def web_skill_text(skill_text):
    desc = WEB_DESC_FILE.read_text(encoding="utf-8").strip()
    if "\n" in desc:
        fail(f"{WEB_DESC_FILE.relative_to(ROOT)}: description must be a single line")
    if not 1 <= len(desc) <= MAX_WEB_DESC:
        fail(f"{WEB_DESC_FILE.relative_to(ROOT)}: {len(desc)} characters, claude.ai allows at most {MAX_WEB_DESC}")
    quoted = '"' + desc.replace("\\", "\\\\").replace('"', '\\"') + '"'
    m = read_frontmatter(skill_text)
    fm, n = re.subn(r"^description:.*$", lambda _: f"description: {quoted}", m.group(1), count=1, flags=re.M)
    if n != 1:
        fail("SKILL.md frontmatter has no description line")
    return f"---\n{fm}\n---\n" + skill_text[m.end():]


def validate_skill(skill_text):
    """All pre-build checks. Returns (version, skill text for claude.ai)."""
    version = check_versions(skill_text)
    desc = fm_field(read_frontmatter(skill_text).group(1), "description") or ""
    if not 1 <= len(desc) <= MAX_DESC:
        fail(f"SKILL.md description is {len(desc)} characters, allowed 1–{MAX_DESC}")
    web_text = web_skill_text(skill_text)
    return version, web_text


def skill_files():
    for path in sorted(SKILL_DIR.rglob("*")):
        rel = path.relative_to(SKILL_DIR)
        if path.is_file() and not any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
            yield path, rel


def write_zip(target, skill_md_text):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, rel in skill_files():
            info = zipfile.ZipInfo(f"{SKILL}/{rel.as_posix()}", ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            data = skill_md_text.encode("utf-8") if rel.as_posix() == "SKILL.md" else path.read_bytes()
            zf.writestr(info, data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", default=str(ROOT / "dist"), help="directory for archives (dist/ by default)")
    ap.add_argument("--version", action="store_true", help="validate and print the version without building")
    args = ap.parse_args()

    # Normalize line endings to LF: on Windows git may hand over a CRLF file.
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    version, web_text = validate_skill(skill_text)

    if args.version:
        print(version)
        return

    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    builds = {
        f"{SKILL}-{version}.zip": skill_text,
        f"{SKILL}.zip": skill_text,
        f"{SKILL}-claude-web-{version}.zip": web_text,
        f"{SKILL}-claude-web.zip": web_text,
    }
    for name, text in builds.items():
        write_zip(out / name, text)
        print(f"built {out / name}")
    print(f"version {version}")


if __name__ == "__main__":
    main()
