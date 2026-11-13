#!/usr/bin/env python3
"""Pre-release PR checks — the counterpart of check-versions.yml.

    python3 scripts/check_versions.py --base origin/main

Checks:
- the version matches in skills/serpzilla-seo-guest-posting/SKILL.md,
  .claude-plugin/plugin.json and .claude-plugin/marketplace.json, and descriptions are within
  limits (the shared checks in scripts/package_skill.py: 1024 characters in SKILL.md, 200 in
  the short description);
- the table in VERSIONS.md contains the current skill version;
- VERSIONS.md has a `### X.Y.Z (date)` section — the release workflow takes the title and notes
  of release vX.Y.Z from it;
- a PR that changes skill or packaging files (skills/**, packaging/**) bumps the version
  relative to base.

Any mismatch exits with an error, so the PR check fails with a clear message.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import package_skill
from package_skill import ROOT, SKILL, SKILL_DIR, fail


def changed_files(base):
    """Files added, modified or renamed by this PR relative to base."""
    out = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"],
        cwd=ROOT, text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def version_at(ref):
    """Plugin version in .claude-plugin/plugin.json at commit ref (or None)."""
    try:
        text = subprocess.check_output(
            ["git", "show", f"{ref}:.claude-plugin/plugin.json"], cwd=ROOT, text=True)
        return json.loads(text).get("version")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def parse_version(v):
    parts = str(v).split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        fail(f"version {v!r} is not in X.Y.Z format")
    return tuple(int(p) for p in parts)


def check_versions_md(version):
    path = ROOT / "VERSIONS.md"
    if not path.exists():
        fail("VERSIONS.md: file is missing — add a version table and a changelog section")
    text = path.read_text(encoding="utf-8")

    row = re.search(rf"^\|\s*{re.escape(SKILL)}\s*\|\s*([^\s|]+)\s*\|", text, re.M)
    if not row:
        fail(f"VERSIONS.md: the table has no row for the `{SKILL}` skill")
    if row.group(1) != version:
        fail(f"VERSIONS.md: the table says {row.group(1)}, while the skill files say {version}")

    if not re.search(rf"^### {re.escape(version)} \([^)]+\)\s*$", text, re.M):
        fail(f"VERSIONS.md: no '### {version} (date)' section — the release workflow "
             "takes the title and release notes from it")


def check_bump(version, base, changed):
    if not any(p.startswith(("skills/", "packaging/")) for p in changed):
        return
    base_version = version_at(base)
    if base_version and parse_version(version) <= parse_version(base_version):
        fail(
            f"the PR changes skill or packaging files (skills/**, packaging/**) but does not "
            f"bump the version: {base_version} → {version}. Bump the version identically in "
            f"skills/{SKILL}/SKILL.md, .claude-plugin/plugin.json and "
            ".claude-plugin/marketplace.json, and describe the changes in VERSIONS.md."
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main",
                    help="base to compare against — branch or commit (origin/main by default)")
    args = ap.parse_args()

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")

    # Version match in the three files and description limits — same as the archive build.
    version, _ = package_skill.validate_skill(skill_text)

    check_versions_md(version)
    check_bump(version, args.base, changed_files(args.base))

    print(f"ok: version {version} is consistent, VERSIONS.md is up to date")


if __name__ == "__main__":
    main()
