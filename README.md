# Rawframe Project organization defaults

Shared files for every repository of the Rawframe Project organization.

- `profile/README.md` is the organization's GitHub profile.
- `CONTRIBUTING.md`, `SECURITY.md` and `AI_POLICY.md`, the issue templates and the pull request template apply to every repository that has none of its own.
- `.github/workflows/docs-check.yml` and `.github/workflows/pr-title.yml` are reusable workflows each repository calls from its own CI. Their usage is in the comment at the top of each file.
- `scripts/docs_check.py` is the documentation check the workflow runs. Run it locally from a repository root with `python3 <path>/scripts/docs_check.py`.
