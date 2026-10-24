# Scheduled runs

The organization's repositories share one pool of free GitHub-hosted runners, about 20 jobs at a time. Scheduled workflows that start at the same minute queue behind each other and behind the pull requests of that hour, so each repository has its own slot. Times are UTC; a repository's scheduled workflows use exactly these cron lines.

| Repository | Nightly `ci` | Weekly `codeql` | Weekly `scorecard` |
|---|---|---|---|
| maul-unicode | `7 1 * * *` | `11 8 * * 1` | `17 9 * * 0` |
| maul-window | `37 1 * * *` | `41 8 * * 1` | `22 9 * * 0` |
| maul-rhi | `7 2 * * *` | `11 8 * * 2` | `27 9 * * 0` |
| maul-locale | `37 2 * * *` | `41 8 * * 2` | `32 9 * * 0` |
| maul-vfx | `7 3 * * *` | `11 8 * * 3` | `37 9 * * 0` |
| maul-ui | `37 3 * * *` | `41 8 * * 3` | `42 9 * * 0` |
| maul2d | `7 4 * * *` | `11 8 * * 4` | `47 9 * * 0` |
| maul3d | `37 4 * * *` | `41 8 * * 4` | `52 9 * * 0` |
| maul-audio | `7 5 * * *` | `11 8 * * 5` | `57 9 * * 0` |
| maul-nav | `37 5 * * *` | `41 8 * * 5` | `2 10 * * 0` |
| maul-anim | `7 6 * * *` | `11 8 * * 6` | `7 10 * * 0` |
| maul-tween | `37 6 * * *` | `41 8 * * 6` | `12 10 * * 0` |
| kest | `7 0 * * *` | `11 8 * * 0` | `17 10 * * 0` |
| rawframe-engine | `37 0 * * *` | `41 8 * * 0` | `22 10 * * 0` |

A repository's other scheduled workflows (screen readers, differentials, extended device suites) run inside its nightly slot as jobs of `ci`, or start 15 minutes after it. In `.github`, `maul-family` runs at `13 7 * * *`, after every nightly, and `ci-image` at `23 3 * * 1`.
