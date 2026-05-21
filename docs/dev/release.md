# Release

Releases are driven by [release-please](https://github.com/googleapis/release-please).

## How it works

1. Merge Conventional Commits to `main`. release-please opens (and continuously
   updates) a **release PR** that bumps `project.version` in `pyproject.toml`,
   updates `.release-please-manifest.json`, and appends to `CHANGELOG.md`.
2. When you are ready to ship, merge the release PR. release-please tags
   the commit (`X.Y.Z`, no `v` prefix) and creates a GitHub release.
3. The `build-and-publish` job in `.github/workflows/release-please.yml`
   builds the wheel + sdist, generates sha256 sums, and uploads everything
   to the GitHub release.
4. (Optional) Uncomment the `pypa/gh-action-pypi-publish` step to publish
   to PyPI via [Trusted Publishing](https://docs.pypi.org/trusted-publishers/).
   No long-lived token needed — configure the trusted publisher on PyPI
   pointing at `release-please.yml`.

## Bump rules (pre-1.0)

Configured in `.release-please-config.json`:

- `bump-minor-pre-major: true` — `feat` bumps the minor (0.1.0 → 0.2.0).
- `bump-patch-for-minor-pre-major: true` — `fix` bumps the patch.

Switch both to `false` once you ship `1.0.0`.

## Manual sanity checks

- `scripts/check_version_tag.py` validates the tag matches `project.version`
  during the release workflow — catches the "tag exists but pyproject is
  stale" failure mode.
- The `build-wheel` job in CI (`main.yml`) runs on every PR, so a broken
  build is caught long before release time.
