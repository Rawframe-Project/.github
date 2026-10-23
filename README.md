# Rawframe Project organization defaults

Shared files for every repository of the Rawframe Project organization.

- `profile/README.md` is the organization's GitHub profile.
- `CONTRIBUTING.md`, `SECURITY.md` and `AI_POLICY.md`, the issue templates and the pull request template apply to every repository that has none of its own.
- Reusable workflows each repository calls from its own CI, with their usage in the comment at the top of each file:
  - `docs-check.yml` and `pr-title.yml`: the documentation check and the conventional pull request title.
  - `cpp.yml`: builds and tests one CMake preset, on Linux inside the CI image, with ccache and the Mesa shader cache warmed from `main`.
  - `changes.yml`: tells CI whether a pull request changes anything beyond documentation.
  - `zizmor.yml`: audits the repository's workflows.
  - `pr-gate.yml`: closes a pull request from outside the organization that does not close an `accepted` issue.
- `ci/cpp/` is the CI image for C and C++, published by `.github/workflows/ci-image.yml` as `ghcr.io/rawframe-project/ci-cpp:<VERSION>`.
- `scripts/docs_check.py` is the documentation check the workflow runs. Run it locally from a repository root with `python3 <path>/scripts/docs_check.py`.
- `workflow-templates/` holds the Scorecard and release workflows each repository copies into its own `.github/workflows/` (replace `$default-branch` with `main`). They are templates rather than reusable workflows because Scorecard must run from the repository it grades and release builds differ per repository.
- Every action is pinned by commit SHA, with the version in a comment; Dependabot keeps the pins current.
- `docs/repository-standard.md` is the standard every repository follows: layout, documentation, tests, work, changes, security and releases.
