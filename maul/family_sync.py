#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Sirac Ozmen
"""Keeps the Maul family's shared files identical in every Maul library.

The canonical copies live beside this script: files/ is copied as it is,
renamed/ is copied with @P@, @PP@, @OPT@ and @LIB@ replaced by the
library's API, macro and option prefixes and its name, and removed.txt
lists files a library must no longer carry. libraries.txt names the
libraries and the renamed files each one uses.

usage: family_sync.py --check [--root DIR] [--ref REF] [--migrated] [library ...]
       family_sync.py --write [--root DIR] [--ref REF] library [library ...]

--root is the folder holding one checkout per library, named after it
(default: the workspace's maul/ folder). --migrated checks only the
libraries that have moved to the repository standard (they have an
AGENTS.md). With no library named, --check checks every library found.
--ref takes the family as this repository holds it at a tag or commit
instead of as the checkout holds it, so a library checks against the
release it pins (`--ref v0.0.58`) whatever this checkout has moved on to.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "maul")


class Source:
    """The family's files: from the working tree, or from git at a ref."""

    def __init__(self, ref=None):
        self.ref = ref
        self.tree = {}
        if ref is None:
            self.modes = recorded_modes(HERE)
            return
        listing = self._git("ls-tree", "-r", "-z", "--full-tree", ref, "--", "maul").decode("utf-8")
        for entry in listing.split("\0"):
            if not entry:
                continue
            meta, path = entry.split("\t", 1)
            mode, kind, blob = meta.split()
            if kind == "blob":
                self.tree[path[len("maul/"):]] = (blob, mode == "100755")

    def _git(self, *args):
        try:
            return subprocess.run(["git", "-C", HERE, *args], check=True, capture_output=True).stdout
        except subprocess.CalledProcessError as error:
            sys.exit(f"git {' '.join(args)}: {error.stderr.decode('utf-8', 'replace').strip()}")

    def read(self, rel):
        """(bytes, executable) of maul/<rel>."""
        if self.ref is None:
            path = os.path.join(HERE, rel)
            with open(path, "rb") as f:
                content = f.read()
            return content, self.modes.get(rel, executable(path))
        if rel not in self.tree:
            sys.exit(f"{rel} is not in {self.ref}")
        blob, runs = self.tree[rel]
        return self._git("cat-file", "blob", blob), runs

    def text(self, rel):
        return self.read(rel)[0].decode("utf-8")

    def walk(self, folder):
        """The files under maul/<folder>, relative to it, sorted."""
        if self.ref is None:
            base = os.path.join(HERE, folder)
            for parent, dirs, files in os.walk(base):
                dirs[:] = sorted(d for d in dirs if d != "__pycache__")
                for name in sorted(files):
                    yield os.path.relpath(os.path.join(parent, name), base).replace(os.sep, "/")
            return
        prefix = folder + "/"
        for path in sorted(self.tree):
            if path.startswith(prefix) and "/__pycache__/" not in "/" + path:
                yield path[len(prefix):]


def libraries(source):
    result = {}
    for number, line in enumerate(source.text("libraries.txt").splitlines(), 1):
        fields = line.split("#", 1)[0].split()
        if not fields:
            continue
        if len(fields) < 4:
            sys.exit(f"libraries.txt:{number}: expected 'directory api macro option [renamed ...]'")
        result[fields[0]] = {"P": fields[1], "PP": fields[2], "OPT": fields[3], "renamed": fields[4:]}
    return result


def removed(source):
    lines = source.text("removed.txt").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def executable(path):
    return bool(os.stat(path).st_mode & 0o111)


def recorded_modes(directory):
    """{path: executable} as git's index records them in the repository at
    directory, paths relative to it; empty when it is no repository. Git's
    mode is the one a commit carries, and on Windows the file system has
    none to read."""
    try:
        listing = subprocess.run(["git", "-C", directory, "ls-files", "-s", "-z"],
                                 check=True, capture_output=True).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError):
        return {}
    modes = {}
    for entry in listing.split("\0"):
        if entry:
            meta, path = entry.split("\t", 1)
            modes[path] = meta.split()[0] == "100755"
    return modes


def expected(source, library, info):
    """(relative path, bytes, executable) for every file the library must carry."""
    for rel in source.walk("files"):
        content, runs = source.read("files/" + rel)
        yield rel, content, runs
    for rel in info["renamed"]:
        content, runs = source.read("renamed/" + rel)
        text = content.decode("utf-8")
        text = (text.replace("@OPT@", info["OPT"]).replace("@LIB@", library)
                .replace("@PP@", info["PP"]).replace("@P@", info["P"]))
        yield rel, text.encode("utf-8"), runs


def sync(source, library, info, base, write):
    differences = 0
    modes = recorded_modes(base)
    for rel, content, runs in expected(source, library, info):
        path = os.path.join(base, rel)
        current = None
        if os.path.exists(path):
            with open(path, "rb") as f:
                current = f.read()
        # A script that loses its executable bit fails where it is run, so
        # the mode is part of the copy.
        if current == content and modes.get(rel, current is not None and executable(path)) == runs:
            continue
        if write:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            os.chmod(path, 0o755 if runs else 0o644)
            print(f"{library}/{rel}: written")
        elif current is None:
            print(f"{library}/{rel}: missing")
            differences += 1
        else:
            print(f"{library}/{rel}: {'differs' if current != content else 'mode differs'}")
            differences += 1
    for rel in removed(source):
        path = os.path.join(base, rel)
        if not os.path.lexists(path):
            continue
        if write:
            os.remove(path)
            print(f"{library}/{rel}: removed")
        else:
            print(f"{library}/{rel}: no longer part of the family")
            differences += 1
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--ref")
    parser.add_argument("--migrated", action="store_true")
    parser.add_argument("library", nargs="*")
    args = parser.parse_args()

    source = Source(args.ref)
    known = libraries(source)
    if args.write and not args.library:
        sys.exit("--write needs the libraries to write")
    for name in args.library:
        if name not in known:
            sys.exit(f"{name} is not in libraries.txt")
    targets = args.library or [n for n in known if os.path.isdir(os.path.join(args.root, n))]
    if args.migrated:
        targets = [n for n in targets if os.path.exists(os.path.join(args.root, n, "AGENTS.md"))]

    differences = 0
    for library in targets:
        base = os.path.join(args.root, library)
        if not os.path.isdir(base):
            print(f"{library}: not checked out in {args.root}")
            differences += 1
            continue
        differences += sync(source, library, known[library], base, args.write)
    if args.check:
        plural = "y" if len(targets) == 1 else "ies"
        print(f"family sync: {differences} difference(s) in {len(targets)} librar{plural}")
        return 1 if differences else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
