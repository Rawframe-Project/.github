#!/usr/bin/env python3
"""Check a repository against the documentation rules of the repository standard.

Usage: docs_check.py [--exclude PATH ...] [--strict]

Run from the repository root. Reads the tracked files from git. Prints one line
per problem and exits 1 if there is any. Without --strict, a repository that has
no AGENTS.md yet (not migrated) is only checked for the em dash.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

EM_DASH = "—"

# Markdown allowed at the root; everything else must live under these folders.
ROOT_MARKDOWN = {
    "README.md", "AGENTS.md", "CLAUDE.md", "CHANGELOG.md",
    "CONTRIBUTING.md", "SECURITY.md", "AI_POLICY.md", "CODE_OF_CONDUCT.md",
}
MARKDOWN_FOLDERS = ("docs/", ".agents/", ".github/")

LIMITS = {"AGENTS.md": 200}
PAGE_LIMIT = 400
SKILL_LIMIT = 500

# Journal residue that never belongs in documentation.
FORBIDDEN = [
    (re.compile(r"\b[DFQW]\d{2,4}\b(?![.\d])"), "internal decision or work number"),
    (re.compile(r"\b20\d\d-\d\d-\d\d\b"), "a date (history belongs in git and the changelog)"),
    (re.compile(r"(?i)\b(worklog|work log|state\.md|decisions\.md|questions\.md)\b"), "a reference to a work journal"),
]

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TEXT_SUFFIXES = {
    ".md", ".txt", ".c", ".h", ".cpp", ".hpp", ".cc", ".inl", ".py", ".sh", ".cmake",
    ".yml", ".yaml", ".toml", ".json", ".kest", ".js", ".ts", ".rs", ".java", ".kt",
    ".m", ".mm", ".swift", ".glsl", ".hlsl", ".wgsl", ".slang", ".html", ".css",
}
TEXT_NAMES = {"CMakeLists.txt", "Makefile", "LICENSE"}


def tracked(excludes):
    out = subprocess.run(["git", "ls-files", "-z"], check=True, capture_output=True).stdout
    files = [f for f in out.decode().split("\0") if f]
    return [f for f in files if not any(f == e or f.startswith(e.rstrip("/") + "/") for e in excludes)]


def is_text(path):
    p = Path(path)
    return p.suffix in TEXT_SUFFIXES or p.name in TEXT_NAMES


def strip_code(text):
    """Drop fenced code blocks and inline code, where identifiers and dates are legitimate."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude", action="append", default=[], help="a path prefix to skip, such as third_party")
    parser.add_argument("--strict", action="store_true", help="check the full standard even before AGENTS.md exists")
    args = parser.parse_args()

    files = tracked(args.exclude)
    migrated = args.strict or "AGENTS.md" in files
    problems = []

    for f in files:
        if not is_text(f):
            continue
        try:
            text = Path(f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if EM_DASH in line:
                problems.append(f"{f}:{n}: em dash")

    if not migrated:
        return report(problems)

    if "CLAUDE.md" not in files or Path("CLAUDE.md").read_text(encoding="utf-8").strip() != "@AGENTS.md":
        problems.append("CLAUDE.md: must contain exactly @AGENTS.md")

    for f in files:
        if not f.endswith(".md"):
            continue
        if "/" not in f and f not in ROOT_MARKDOWN:
            problems.append(f"{f}: Markdown file not allowed at the root")
            continue
        if "/" in f and not f.startswith(MARKDOWN_FOLDERS):
            problems.append(f"{f}: Markdown belongs in docs/, .agents/ or .github/")
            continue

        text = Path(f).read_text(encoding="utf-8")
        lines = text.count("\n") + 1
        limit = LIMITS.get(f, SKILL_LIMIT if f.endswith("SKILL.md") else PAGE_LIMIT)
        if f != "CHANGELOG.md" and lines > limit:
            problems.append(f"{f}: {lines} lines, over the limit of {limit}")

        if f not in ("CHANGELOG.md",):
            prose = strip_code(text)
            for n, line in enumerate(prose.splitlines(), 1):
                for pattern, why in FORBIDDEN:
                    if pattern.search(line):
                        problems.append(f"{f}: {why}: {line.strip()[:80]}")

        for target in LINK.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = (Path(f).parent / target.split("#")[0]).resolve()
            if not path.exists():
                problems.append(f"{f}: broken link {target}")

    return report(problems)


def report(problems):
    for p in problems[:200]:
        print(p)
    if len(problems) > 200:
        print(f"... and {len(problems) - 200} more")
    if problems:
        print(f"docs check: {len(problems)} problem(s)")
        return 1
    print("docs check: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
