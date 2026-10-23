#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Sirac Ozmen
"""Keeps the Maul family's shared files identical in every Maul library.

The canonical copies live beside this script: files/ is copied as it is,
renamed/ is copied with @P@, @PP@, @OPT@ and @LIB@ replaced by the
library's API, macro and option prefixes and its name, and removed.txt
lists files a library must no longer carry. libraries.txt names the
libraries and the renamed files each one uses.

usage: family_sync.py --check [--root DIR] [--migrated] [library ...]
       family_sync.py --write [--root DIR] library [library ...]

--root is the folder holding one checkout per library, named after it
(default: the workspace's maul/ folder). --migrated checks only the
libraries that have moved to the repository standard (they have an
AGENTS.md). With no library named, --check checks every library found.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, "files")
RENAMED = os.path.join(HERE, "renamed")
DEFAULT_ROOT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "maul")


def libraries():
    result = {}
    with open(os.path.join(HERE, "libraries.txt"), encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            fields = line.split("#", 1)[0].split()
            if not fields:
                continue
            if len(fields) < 4:
                sys.exit(f"libraries.txt:{number}: expected 'directory api macro option [renamed ...]'")
            result[fields[0]] = {"P": fields[1], "PP": fields[2], "OPT": fields[3], "renamed": fields[4:]}
    return result


def removed():
    with open(os.path.join(HERE, "removed.txt"), encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def shared_files():
    for folder, dirs, files in os.walk(FILES):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(files):
            yield os.path.relpath(os.path.join(folder, name), FILES)


def expected(library, info):
    """(relative path, bytes) for every file the library must carry."""
    for rel in shared_files():
        with open(os.path.join(FILES, rel), "rb") as f:
            yield rel, f.read()
    for rel in info["renamed"]:
        with open(os.path.join(RENAMED, rel), encoding="utf-8") as f:
            text = f.read()
        text = (text.replace("@OPT@", info["OPT"]).replace("@LIB@", library)
                .replace("@PP@", info["PP"]).replace("@P@", info["P"]))
        yield rel, text.encode("utf-8")


def sync(library, info, base, write):
    differences = 0
    for rel, content in expected(library, info):
        path = os.path.join(base, rel)
        current = None
        if os.path.exists(path):
            with open(path, "rb") as f:
                current = f.read()
        if current == content:
            continue
        if write:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            print(f"{library}/{rel}: written")
        else:
            print(f"{library}/{rel}: {'missing' if current is None else 'differs'}")
            differences += 1
    for rel in removed():
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
    parser.add_argument("--migrated", action="store_true")
    parser.add_argument("library", nargs="*")
    args = parser.parse_args()

    known = libraries()
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
        differences += sync(library, known[library], base, args.write)
    if args.check:
        plural = "y" if len(targets) == 1 else "ies"
        print(f"family sync: {differences} difference(s) in {len(targets)} librar{plural}")
        return 1 if differences else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
