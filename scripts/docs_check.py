#!/usr/bin/env python3
"""Check a repository against the documentation rules of the repository standard.

Usage: docs_check.py [--root REPO] [--exclude PATH ...] [--strict]

Run from the repository root, or name it with --root. Reads the tracked files from git. Prints one line
per problem and exits 1 if there is any. Without --strict, a repository that has
no AGENTS.md yet (not migrated) is only checked for the em dash.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

EM_DASH = "\u2014"

# Markdown allowed at the root; everything else must live under these folders.
ROOT_MARKDOWN = {
    "README.md", "AGENTS.md", "CLAUDE.md", "CHANGELOG.md",
    "CONTRIBUTING.md", "SECURITY.md", "AI_POLICY.md", "CODE_OF_CONDUCT.md", "TRADEMARK.md",
}
MARKDOWN_FOLDERS = ("docs/", ".agents/", ".github/")

LIMITS = {"AGENTS.md": 200}
PAGE_LIMIT = 400
SKILL_LIMIT = 500

# Journal residue that never belongs in documentation.
FORBIDDEN = [
    (re.compile(r"\b(?:D(?!16\b|24\b|32\b)\d{2,4}|[QW]\d{2,4}|F(?:2[5-9]|[3-9]\d|\d{3,4}))\b(?![.\d])"), "internal decision or work number"),
    (re.compile(r"(?<![-\w])[a-z]{3,5}-\d{4}(?:\b(?!\.\d|-)|-[a-z][\w-]*\.md)"), "an internal record number"),
    (re.compile(r"\([ADFILNQTUVW]\d{1,3}\)"), "an internal item id"),
    (re.compile(r"\b20\d\d-\d\d-\d\d\b"), "a date (history belongs in git and the changelog)"),
    (re.compile(r"(?i)\b(worklog|work log|state\.md|decisions\.md|questions\.md)\b"), "a reference to a work journal"),
]

# Citations of old decision records in source comments. Distinctive forms only,
# so identifiers and literals are not caught.
# A record id stands alone: one inside a hyphenated word (a language tag
# such as sl-rozaj-biske-1994, a unit such as gram-per-1000-meter) is not,
# but a record's file name (mloc-0045-messages.md) is. Nor is a version
# (slang-2026.19).
CODE_FORBIDDEN = re.compile(r"\b(?:ADR|SPEC|STD|RESEARCH)-\d{4}\b|(?<![-\w])[a-z]{3,5}-\d{4}(?:\b(?!\.\d|-)|-[a-z][\w-]*\.md)")
CODE_D_NUMBER = re.compile(r"\bD(?!16\b|24\b|32\b)\d{2,4}\b(?![.\dA-Za-z])")
# A D-number that is not an old record: a code point (U+D800, 0xD800, \uD800)
# or a definition of the Unicode Standard (UAX #15 D114, definition D117).
NOT_A_RECORD = re.compile(r"(?:U\+|0x|\\u|[#/])$|(?i:definition|definitions|UAX\s*#\d+|Unicode)\s*$")
# The CIE standard illuminants D50 and D65, on a line about color.
ILLUMINANT = re.compile(r"(?i)\b(?:white\s*point|illuminant|CIE|daylight|sRGB|XYZ|Lab|color|colour)\b")


def not_a_record(line, m):
    if NOT_A_RECORD.search(line[max(0, m.start() - 24):m.start()]):
        return True
    return m.group(0) in ("D50", "D65") and bool(ILLUMINANT.search(line))


def cites_record(line):
    if CODE_FORBIDDEN.search(line):
        return True
    return any(not not_a_record(line, m) for m in CODE_D_NUMBER.finditer(line))
CODE_SUFFIXES = {".c", ".h", ".cpp", ".hpp", ".cc", ".inl", ".py", ".sh", ".cmake", ".kest",
                 ".js", ".ts", ".java", ".kt", ".m", ".mm", ".swift", ".yml", ".yaml"}

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
    """Drop fenced code blocks and inline code, where identifiers, dates and link-like text are legitimate.

    A fence opens with three or more backticks or tildes and closes with a line of at least as
    many of the same character, as CommonMark has it; an unclosed fence runs to the end."""
    kept = []
    fence = None
    for line in text.split("\n"):
        # A fence may sit inside a quote or a list item.
        stripped = re.sub(r"^\s*(?:(?:>\s?|[-*+]\s+|\d+[.)]\s+)\s*)*", "", line)
        if fence is None:
            m = re.match(r"(`{3,}|~{3,})", stripped)
            if m and not (m.group(1)[0] == "`" and "`" in stripped[len(m.group(1)):]):
                fence = m.group(1)
                continue
            kept.append(line)
        elif re.fullmatch(re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", stripped):
            fence = None
    return re.sub(r"`[^`\n]*`", "", "\n".join(kept))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude", action="append", default=[], help="a path prefix to skip, such as third_party")
    parser.add_argument("--strict", action="store_true", help="check the full standard even before AGENTS.md exists")
    parser.add_argument("--root", default=".", help="the repository to check (default: the current directory)")
    args = parser.parse_args()
    os.chdir(args.root)

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

        prose = strip_code(text)
        for line in prose.splitlines():
            for pattern, why in FORBIDDEN:
                if f == "CHANGELOG.md" and "date" in why:
                    continue
                if "decision or work number" in why and not any(
                        not not_a_record(line, m) for m in pattern.finditer(line)):
                    continue
                if pattern.search(line):
                    problems.append(f"{f}: {why}: {line.strip()[:80]}")

        for target in LINK.findall(prose):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = (Path(f).parent / target.split("#")[0]).resolve()
            if not path.exists():
                problems.append(f"{f}: broken link {target}")

    for f in files:
        p = Path(f)
        if p.suffix not in CODE_SUFFIXES and p.name not in ("CMakeLists.txt", "Makefile"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if cites_record(line):
                problems.append(f"{f}:{n}: cites an old record: {line.strip()[:80]}")

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
