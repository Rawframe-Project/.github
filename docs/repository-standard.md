# Repository standard

How every repository of the Rawframe Project organization is laid out, documented, tested and changed. It applies to all repositories except `rawframe-platform`. A repository that has not been moved to this standard yet keeps its current contract until its migration pull request merges.

The model is [pingdotgg/t3code](https://github.com/pingdotgg/t3code). The rules below come from the research listed under [Sources](#sources).

## Principles

1. **A repository reads like a product, not a diary.** It says what the product is and how it works today. History lives in git, pull requests and the changelog.
2. **Less context is better context.** Agents and people both do worse with long, stale instructions. Every line of guidance must prevent a real mistake.
3. **Rules that must always hold are enforced by a tool.** Prose is advice; a CI check or a hook is a guarantee.
4. **Code is the source of truth.** Documentation explains what the code cannot: intent, constraints and traps.
5. **Tests guard behavior, not structure.** A test that breaks when the implementation is refactored without a behavior change is a defect.

## Files

A repository contains these documentation files and no others. The documentation check fails on any other Markdown file outside `docs/`, `.agents/` and `.github/`, apart from third-party files under a vendor folder.

| Path | Purpose |
|---|---|
| `README.md` | What the product is, why it exists, a quick start, and links. For the public. |
| `AGENTS.md` | The guide for coding agents. See [AGENTS.md](#agentsmd). |
| `CLAUDE.md` | One line: `@AGENTS.md`. |
| `CHANGELOG.md` | User-facing changes per release. See [Releases](#releases). |
| `LICENSE` | The license. |
| `docs/README.md` | Index of the documentation. |
| `docs/user/` | How to use the product. |
| `docs/internals/` | How it works and why. |
| `docs/operations/` | How to develop, test and release it. |
| `.agents/skills/` | Agent skills. `.claude/skills` is a symlink to it. |
| `.github/` | Workflows, and templates only where the organization defaults do not fit. |

`CONTRIBUTING.md`, `SECURITY.md`, `AI_POLICY.md`, `CODE_OF_CONDUCT.md` and the issue and pull request templates come from the organization's public `.github` repository. A repository adds its own copy only to change it.

Never committed: plans, research notes, work logs, state files, decision journals, task lists, session notes, mutation reports, benchmark scratch, screenshots for a single pull request. Working material stays outside the repository; progress lives in the issue.

## AGENTS.md

Hand-written, at most 200 lines. For each line ask whether an agent would make a mistake without it; if not, delete it.

It contains, in this order:

1. **What the product is** in two or three sentences, and the few things it never compromises on.
2. **Commands** an agent cannot guess: build, the changed-files check, the full check, how to run one test.
3. **Ways to hurt yourself:** the actions in this repository that damage state, other sessions or the machine, and what to do instead. Every repository includes: never kill a process found by matching a name or path; kill only a PID you started.
4. **Invariants** that are not visible from one file (determinism, dependency direction, ABI rules, generated files).
5. **Testing rules** specific to the repository, on top of [Tests](#tests).
6. **Documentation rules:** a link to this standard's [Documentation](#documentation) section and anything specific.
7. **Pull requests:** the commit title scopes the repository uses.

It does not contain directory tours, file catalogs, feature lists, API descriptions, history, dates, decision numbers, or anything the code already says. Long procedures that are needed only sometimes become skills.

Preferences of the owner that are not about the product (language of conversation, the no em dash rule) live in the organization's workspace guide and in the documentation check, not in each repository.

## Documentation

### Structure

- `docs/user/` follows the reader's task: install, use, configure, troubleshoot. One page per major feature: what it does, how to start, what is not obvious. No descriptions of every button, field or state.
- `docs/internals/` holds one living page per topic (for example `networking.md`, `determinism.md`, `memory.md`). Each page explains how the part works, why it is built that way, the constraints that span components, and the traps that are hard to see in the source. It links to source instead of copying it. `overview.md` and `glossary.md` are always present.
- `docs/operations/` holds the maintainer's procedures: development setup, checks, release, debugging.
- API reference is generated from the headers or the source where the toolchain allows; it is not written by hand. Generated documentation (API reference, an `llms.txt` digest of the docs) is built into the published site, not committed.

### Rules

- Most code changes need no documentation change. Before adding a paragraph, ask what a maintainer or user would get wrong without it.
- When a documented decision or behavior changes, rewrite or delete the affected text in the same pull request. Never append an amendment, a dated note or a second account. Git keeps the history.
- A new page needs a distinct and lasting reason to exist. Prefer extending an existing page.
- Write in the product's voice, present tense, third person. No first person, no "we decided on", no dates, no names, no internal numbers (`D123`, `F45`, `W30`, `ADR-0012`, `mui-0004`). The same holds for code comments: a comment explains why, it never cites a record.
- A local implementation detail goes in a code comment next to the code. Comments say why, never what.
- Pages stay under 400 lines; reference pages over 100 lines start with a table of contents.

### Decisions

There is no numbered decision log. A decision is recorded by writing its reasoning into the relevant `docs/internals/` page, under the part it governs, and by the pull request that made it. Alternatives that were considered and rejected are kept in one short paragraph only when a future maintainer would otherwise try them again.

## Skills

- Skills live in `.agents/skills/<name>/SKILL.md`, with `.claude/skills` a symlink to `.agents/skills`.
- A skill is written only after the same need has come up more than once. Before writing it, write at least three example tasks it must handle; check a fresh session handles them better with the skill than without.
- `name` is lowercase with hyphens, preferably a gerund (`releasing-a-version`). `description` is third person and says what the skill does and when to use it.
- The body stays under 500 lines and holds steps, examples and edge cases. Longer material goes in files one level below it. Deterministic steps are scripts the skill runs, not prose.
- No dates or time-sensitive statements. Skills follow the same voice rules as documentation.
- A skill that more than one repository needs is kept in the organization's `.github` repository and synced into each repository by its sync tool.

## Shared files

Files that several repositories must keep identical (the Maul family's shared sources, build modules, check tools and conventions page) have one canonical copy in the organization's `.github` repository, under `maul/`. `maul/family_sync.py --write <library>` writes them into a library, and `maul-family.yml` in `.github` checks every migrated library against them when they change and every night; a drift there is fixed like a red `main`. A repository changes a shared file only by changing the canonical copy first.

## Tests

### What gets a test

Tests protect the core of the product: deterministic results, wire and file formats, handling of hostile or malformed input, the public API contract, and the bug classes that have already escaped once.

- **Logic, data, state and protocol bugs:** the fix comes with the fewest tests that fail on the unfixed code for the right reason, added to the existing test file of that module.
- **Visual and cosmetic changes** (spacing, color, alignment, wording, shortcuts, menu entries): no test. The proof is a before and after capture in the pull request.
- **New features:** tests cover the behavior a user or caller relies on, not every input. Add a case only when the code branches differently for it.
- **No test** asserts the current implementation instead of the specification: call order, private state, internal sizes, mocks wired to mirror the code.
- **Golden values** that pin a promised output (determinism hashes, file and wire format bytes) are part of the specification, not change detectors. Keep them few: a handful of golden scenarios, so a deliberate change regenerates a few values, not dozens.

### How a test is written

- It checks observable behavior through the public interface and survives refactoring.
- Every assertion can fail. Prefer the strongest exact check over a weak one.
- It is deterministic and hermetic: no wall clock, no sleeps, no polling, no external network (localhost is fine), no retries. A flaky test is fixed, not retried; a skipped test names its tracking issue on the line above.
- It is fast: a unit test runs in milliseconds, an integration test in about a second. A slow test is a defect.
- When it fails, the message says what broke.
- Test output stays short; details go to a log file.
- **Integration tests** that drive real devices, sound servers, windows, emulators or browsers carry an `integration` label. They may read the clock and use localhost networking, stay out of the changed-files check, and are kept to a few end-to-end scenarios.
- A check that fails intermittently is moved out of the required pull request check into the nightly run, with an issue, until it is fixed. It is never retried.
- Generated sources and test data may be committed when CI cannot regenerate them. `docs/operations/` names the generator and the command, and `AGENTS.md` lists the generated paths. Anything a test needs to regenerate its data, such as oracle generators in an old private repository, moves into the repository's `tools/` before the migration finishes.
- Size and speed budgets the product promises are checked with a stated tolerance, never as exact counts.

### Assertions in code

C and C++ production code asserts its invariants: preconditions, postconditions, and states that must not happen, both what is expected and what is excluded. Untrusted input (files, network data, API arguments) is never handled by an assertion: it is validated and refused with an error in every build. Assertions check internal invariants; they are on in debug, sanitizer and fuzz builds and may be compiled out of release builds where the product's speed requires it. Review checks that new code asserts what it assumes. Assertions catch the bugs that per-case unit tests would otherwise be written for, and they make fuzzing and simulation find more.

### Fuzzing and simulation

- Fuzzing covers code that reads untrusted or complex input: parsers, decoders, network protocols, file formats, compilers and virtual machines, and pairs of implementations that must agree.
- Pull requests that touch fuzzed code run a short fuzzing pass; a nightly run fuzzes longer and grows the corpus. Every crash it finds becomes a regression test.
- Deterministic simulation (a seed reproduces the run) is used where the product is deterministic.
- Mutation testing is not part of the checks. There are no mutation sweeps and no mutation score. A maintainer may run it on one changed module as a review aid; surviving mutants are not a reason to add tests by themselves.

### Budgets

- The changed-files check that agents run before pushing: under 2 minutes.
- The pull request check in CI: under 10 minutes.
- The full check on `main` and nightly: under 20 minutes.
- An extended nightly run (every platform cell, emulators and simulators, long fuzzing) may take longer, at most two hours. It is not a required check.

Over budget, tests are pruned or merged before anything else is added.

## Work

- Work is tracked in GitHub issues. A session opens an issue for every piece of work it starts and closes it through the pull request that finishes it.
- The organization has one GitHub Project board, [Rawframe](https://github.com/orgs/Rawframe-Project/projects/1). Columns: Backlog, Ready, In progress, In review, Done. Milestones group issues toward a release.
- The owner and the manager set milestones. Product sessions split them into issues and order Ready.
- A session takes the top issue of its repository's Ready column, assigns itself, moves it to In progress, and works on that one issue only.
- The issue body is the progress record: a short problem statement and a checklist the session updates. Findings that matter later go into the issue as comments, not into files.
- Labels: `bug`, `feature`, `docs`, `performance`, `security`, `chore`, `blocked`, `accepted` (an outside request a maintainer approved), `duplicate`, `wontfix`. `tools/repo-setup.sh` applies them with the merge settings and the ruleset. Questions for the owner are never written in a public repository; they go to the manager.

## Sessions

Each repository has one agent session, started by the owner and named after the repository.

- A session works when it has work: an issue in its Ready column, a message from the manager, or a review on its pull request. With none of these it stops and waits; it does not poll on a short timer.
- A session that waits on something slow (a CI run, a long fuzz pass) checks back at the pace of that thing, not every few minutes.
- The queue is the repository's Ready column. A session that finishes an issue takes the next one; when Ready is empty it tells the manager and stops.
- Heavy local jobs (full checks, large builds, fuzzing, emulators) run through `tools/heavy.sh` of the workspace, so sessions do not starve each other on the shared machine.

## Changes

- `main` is protected by a ruleset: changes arrive only through pull requests, the required checks must pass, history is linear, force pushes are blocked.
- Branch names are short and hyphenated, without prefixes (`collision-sweep`).
- Pull request titles are conventional commits: `type(scope): summary` in plain, lower-case language, under 72 characters. Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`. Scopes are the repository's areas, listed in its `AGENTS.md`.
- The body follows the template: Problem, Change, Verification (what was run and what it showed). It ends with `Closes #<issue>`.
- Pull requests are squash-merged; the title becomes the commit on `main`. Auto-merge is on; a pull request merges when its checks pass.
- Checks that run on a self-hosted runner run only for branches of the same repository, never for code from a fork. Outside pull requests run on hosted runners or after a maintainer approves the run.
- One issue, one pull request. Unrelated fixes go in separate pull requests.
- Before a pull request merges, the `reviewer` session reviews it in a fresh context: correctness first, then the standard. It comments on the pull request; the author fixes what it finds.
- A red `main` is fixed before any other work.
- Commits and pull requests carry no `Co-Authored-By`, "Generated with", model or session lines.

## Continuous integration

A repository's `ci.yml` lists what to check; the organization's reusable workflows say how. A C or C++ repository builds through CMake presets, so CI and a local build run the same commands.

- **Presets.** `CMakePresets.json` defines, for every CI cell, a configure, a build and a test preset of the same name, with the binary directory `out/<preset>` and the test timeout. `tools/check.sh` runs the same presets locally.
- **Toolchain.** Linux cells run in the organization's CI image, `ghcr.io/rawframe-project/ci-cpp:<YYYY.MM.N>`, built from `.github/ci/cpp`: compilers, build tools and the libraries the families link, with nothing installed during the run. A repository takes a new image with the next pin of the reusable workflow, never all at once. macOS and Windows cells use the runner's own toolchain.
- **Pins.** Reusable workflows are pinned by the commit of a `.github` release, with its tag in a comment (`@<sha> # v0.0.1`). Dependabot moves the pins; the manager tags `.github` whenever a shared workflow, template or the image changes.
- **One workflow per cell.** Each matrix cell calls `cpp.yml` with its preset and runner. Jobs other than builds (format, static analysis, generated files, size reports) stay in the repository's own `ci.yml`, in the same image.
- **Caches.** ccache and the Mesa shader cache are restored for every run and saved only from `main`, so pull requests start warm and never overwrite each other. No job installs packages it could take from the image.
- **Changed files.** The first job calls `changes.yml`; a pull request that changes only documentation skips the builds.
- **One required check.** The last job, `required`, runs `if: always()`, needs every other job, and fails if any needed job failed or was cancelled; a job skipped by `changes` counts as passed. The ruleset requires only `required` and `title / title`, so renaming or adding a cell never touches the ruleset.
- **Concurrency.** A new push to a pull request cancels its running CI. Runs on `main` are never cancelled.
- **New tests repeat.** One sanitizer cell sets `repeat: 3`: on pull requests every test runs up to three times until it fails, so a flaky test fails before it merges.
- **Workflow hygiene.** Every workflow sets `permissions: {}` at the top and grants each job what it needs, sets `defaults.run.shell: bash` (so a failing command anywhere in a pipeline fails the step; `scorecard.yml` is the one exception, since Scorecard rejects top-level defaults), checks out with `persist-credentials: false`, and passes event data to scripts only through `env`. `zizmor.yml` audits every workflow on each pull request.
- **Pull request gate.** `pr-gate.yml` runs on `pull_request_target` and closes a pull request from outside the organization unless it closes an issue labeled `accepted`. It never checks out the pull request's code.
- **Failures.** A failed test cell uploads its ctest logs for a week. A failure on `main` is reported to the manager and fixed before other work.
- **Runners.** GitHub-hosted runners, free for public repositories. A larger or paid runner needs a measurement that the budget cannot be met without it.

## Security and supply chain

- Every action in a workflow is pinned by commit SHA with its version in a comment, and `.github/dependabot.yml` keeps the pins current (the `github-actions` ecosystem, weekly, grouped).
- Workflows declare the least `permissions` they need; the default token is read-only.
- CodeQL scans every pull request and `main`: default setup where it builds the code, otherwise an advanced `.github/workflows/codeql.yml` (the two must not both be on).
- OpenSSF Scorecard runs weekly from `workflow-templates/scorecard.yml`, and the README shows its badge.
- Secret scanning with push protection, Dependabot alerts and private vulnerability reporting are on.

## Releases

- Versions follow Semantic Versioning. Tags are `vX.Y.Z`.
- release-please keeps a release pull request open from the conventional commits. It runs with a token of the organization's Rawframe Release GitHub App (`vars.RELEASE_APP_CLIENT_ID`, `secrets.RELEASE_APP_PRIVATE_KEY`), not `github.token`, because GitHub starts no CI for pull requests `github.token` opens and the release pull request must pass the required checks. Before merging it, the session rewrites its changelog entry into user language: what changed for someone using the product, grouped as Added, Changed, Fixed, Removed, Security. Internal refactors and test changes are left out.
- Merging the release pull request tags the version and publishes the GitHub release with the same notes. Every release carries its files, a `SHA256SUMS` file, an SPDX SBOM and a build provenance attestation (`workflow-templates/release.yml`), so a user can check what they downloaded and where it was built.
- Every repository restarts at `0.0.1` when it migrates. Its old tags and GitHub releases are deleted, its changelog starts fresh with the `0.0.1` entry written in user language, and other repositories that pin it by tag move to the new tag. Git history keeps everything that came before.

## Presentation

- The GitHub repository has a one-line description, topics and, where one exists, a homepage.
- `README.md` opens with the name, one sentence, and badges for CI, license and latest release. Then: what it is and why, a quick start that works when copied, the supported platforms, links to the docs, and the license. No roadmap, no history, no internal process.
- The organization profile lives in the `.github` repository's `profile/README.md`.

## Contributions and AI

- The project is developed with AI agents and says so in its README and `AI_POLICY.md`.
- Questions and ideas go to the repository's Discussions; bugs and agreed work go to issues.
- Outside contributors may open issues. Pull requests are accepted only for an issue a maintainer has approved; others are closed with a pointer to `CONTRIBUTING.md`.
- `rawframe-engine` is source-available and takes issues only; it accepts no outside code. Its own `CONTRIBUTING.md` says so.
- `AI_POLICY.md` asks outside contributors to disclose AI use and to understand every line they submit.

## Enforcement

The organization's `.github` repository provides reusable workflows that every repository calls:

- **Documentation check:** only the files listed under [Files](#files); no em dash; no internal numbers (`D[0-9]+`, `F[0-9]+` and the like) or dated notes in docs; size limits for `AGENTS.md`, pages and skills; links resolve; `CLAUDE.md` is exactly `@AGENTS.md`.
- **Pull request title check:** conventional commit format and a known scope.
- **Test hygiene:** where the language allows, a check that rejects sleeps, wall-clock reads, retries and unexplained skips in tests.

## Migrating a repository

A repository moves to this standard in one pull request, or for a large repository a short ordered series (files and docs, then tests and CI, then source comments), done by its own session:

1. Write `AGENTS.md`, `README.md`, `docs/` and skills from the code. Old documents are read only to recover intent; nothing is copied from them.
2. Remove everything the standard does not allow: journals, notes, old docs, duplicated health files.
3. Prune the tests to the rules above and bring the checks within budget.
4. Add the workflows on the shared CI (see Continuous integration; `maul-unicode`'s `.github/workflows` are the model), release-please (manifest at `0.0.1`), rulesets, labels and repository metadata. End the pull request body with the line `Release-As: 0.0.1`: the squash commit carries it, and it makes release-please open the `0.0.1` release pull request, which it would otherwise skip, because a migration is a `chore` and a manifest alone treats `0.0.1` as already released. Keep the hand-written `0.0.1` changelog entry over the one release-please generates.
5. The manager reviews the pull request against this document's checklist before it merges and runs `tools/repo-setup.sh`. The first release pull request publishes `v0.0.1`. Repositories that pin this one by tag move to `v0.0.1` next. The manager deletes the old tags and releases only when no repository's `main` reaches them, directly or through another repository's old tag (within a family, once the whole family has released `0.0.1`), so no dependent's CI breaks. Repositories migrate in dependency order: a library before the libraries that fetch it.

`maul-unicode` was the pilot. The others follow in rounds of three or four, in dependency order.

## Sources

- Anthropic, [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices): keep CLAUDE.md short, prune what the agent already does right, enforce invariants with hooks, give the agent a check to run.
- Anthropic, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): descriptions, 500-line bodies, one-level references, evaluations before writing.
- Gloaguen et al., ETH Zurich, [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988): generated context files lower success and raise cost; directory overviews do not help.
- [Rethinking the Value of Agent-Generated Tests](https://arxiv.org/html/2602.07900v2): more agent-written tests do not raise resolution rates; they cost tokens.
- Petrovic and Ivankovic, [Practical Mutation Testing at Scale](https://arxiv.org/abs/2102.11378): 85% of surfaced mutants judged unproductive; tests written for them are change detectors.
- Kent Beck, [Test Desiderata](https://testdesiderata.com/): behavioral and structure-insensitive tests.
- TigerBeetle, [TIGER_STYLE](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md): assertion density, testing invalid input, deterministic simulation.
- [OSS-Fuzz](https://google.github.io/oss-fuzz/) and [ClusterFuzzLite](https://google.github.io/clusterfuzzlite/): what to fuzz; short fuzzing on pull requests, long fuzzing in batch.
- Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) and [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler): one task per session, structured progress, startup checks, work split so agents do not collide.
- Repositories read: [t3code](https://github.com/pingdotgg/t3code), [Ghostty](https://github.com/ghostty-org/ghostty) (AGENTS.md, AI_POLICY.md), [Bun](https://github.com/oven-sh/bun) (AGENTS.md, REVIEW.md), [Zed](https://github.com/zed-industries/zed), [opencode](https://github.com/sst/opencode).
- [Diataxis](https://diataxis.fr/) for separating tutorials, how-to guides, reference and explanation.
- CI workflows read: [Ladybird](https://github.com/LadybirdBrowser/ladybird) (a pinned CI image, one reusable workflow per preset, ccache saved from the main branch, repeated new tests), [uv](https://github.com/astral-sh/uv) (a planning job, one aggregate required check, zizmor), [t3code](https://github.com/pingdotgg/t3code) and [Ghostty](https://github.com/ghostty-org/ghostty) (changed-files detection, contributor gates), [Bevy](https://github.com/bevyengine/bevy) (cache warming, safe `workflow_run` comments), [oxc](https://github.com/oxc-project/oxc) and [DuckDB](https://github.com/duckdb/duckdb).
