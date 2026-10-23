# Maul family files

The files every Maul library shares, kept here once.

- `files/` is copied into each library as it is: formatting and analysis settings, the CMake modules, the test harness, the checks in `tools/`, and `docs/internals/maul-conventions.md`, the family's rules.
- `renamed/` holds shared sources a library carries under its own prefixes; `@P@`, `@PP@`, `@OPT@` and `@LIB@` become the library's API, macro and option prefixes and its name.
- `libraries.txt` names the libraries, their prefixes and the renamed files each uses.
- `removed.txt` lists files the family no longer shares; a library must not carry them.

A change to a shared file is made here first, then each library takes it in its own pull request:

```sh
python3 /home/rawframe-project/.github/maul/family_sync.py --write maul-window
python3 /home/rawframe-project/.github/maul/family_sync.py --check
```

`.github/workflows/maul-family.yml` checks every library on the repository standard against these files when they change and every night.
