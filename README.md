# Rawframe Project organization defaults

Shared files for every repository of the Rawframe Project organization.

- `profile/README.md` is the organization's GitHub profile.
- `CONTRIBUTING.md`, `SECURITY.md` and `AI_POLICY.md`, the issue templates and the pull request template apply to every repository that has none of its own.
- Reusable workflows each repository calls from its own CI, with their usage in the comment at the top of each file:
  - `pr-title.yml`: the conventional pull request title.
  - `docs-check.yml`: the documentation check, superseded by the action below.
  - `cpp.yml`: builds and tests one CMake preset, on Linux inside the CI image, with ccache and the Mesa shader cache warmed from `main`.
  - `changes.yml`: tells CI whether a pull request changes anything beyond documentation.
  - `zizmor.yml`: audits the repository's workflows.
  - `pr-gate.yml`: closes a pull request from outside the organization that does not close an `accepted` issue.
- `maul/` holds the Maul family's shared files and `family_sync.py`, which writes them into a library; `.github/workflows/maul-family.yml` checks every migrated library against them. See `maul/README.md`.
- `ci/cpp/` is the CI image for C and C++, published by `.github/workflows/ci-image.yml` as `ghcr.io/rawframe-project/ci-cpp:<VERSION>`.
- `.github/actions/docs-check/` is the documentation check as an action. A repository calls it from its own job after checking itself out, pinned like a reusable workflow, and the action runs `scripts/docs_check.py` from that same commit.
- `scripts/docs_check.py` is the documentation check the action runs. Run it locally from a repository root with `python3 <path>/scripts/docs_check.py`.
- `workflow-templates/` holds the Scorecard and release workflows each repository copies into its own `.github/workflows/` (replace `$default-branch` with `main`). They are templates rather than reusable workflows because Scorecard must run from the repository it grades and release builds differ per repository.
- Every action is pinned by commit SHA, with the version in a comment; Dependabot keeps the pins current.
- Releases: when a reusable workflow, a template or the CI image changes, the manager tags a release (`v0.0.1`, `v0.0.2`, ...). Repositories pin the reusable workflows by a release's commit with its tag in a comment (`@<sha> # v0.0.1`), so zizmor can check the pin and Dependabot can move it. A pin commented with a branch name fails zizmor as soon as the branch moves.
- `docs/repository-standard.md` is the standard every repository follows: layout, documentation, tests, work, changes, security and releases.
