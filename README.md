# py-template

Opinionated Python project template extracted from
[rararulab/yaya](https://github.com/rararulab/yaya). Drop-in starter for a
**CLI + library** Python project with the same quality bar:

- `uv` for env + lockfile, `just` for tasks.
- `ruff` lint + format (broad rule selection).
- `mypy --strict` **and** `pyright --strict` (Pylance parity — no "green CI / red IDE" gap).
- `pytest` + `pytest-cov` with global ≥90% coverage gate, ratchetable per-module gates.
- `pre-commit` (ruff, uv-lock, basic hygiene).
- GitHub Actions matrix CI: Ubuntu/macOS/Windows × Python 3.12 / 3.13, plus wheel/sdist build.
- **release-please** for automated versioning + `CHANGELOG.md` + GitHub releases
  with wheel/sdist + sha256 attached. Optional PyPI publish via Trusted Publishing.
- **mkdocs-material** docs site with `mkdocstrings` API reference, auto-deployed
  to GitHub Pages on push to `main`.
- PR title checker (Conventional Commits), dependabot (uv + actions), PR template.
- `typer` + `rich` CLI scaffold, single `greet()` library function as a placeholder.

Source layout: `src/<pkg>/` + `tests/` + `scripts/` (stdlib-only helpers).

## Use this template

**Option A — GitHub "Use this template" button** (recommended once this repo
is pushed and marked as a template in Settings → General):

1. Click "Use this template" on GitHub, create your new repo, clone it.
2. Run `./setup-template.sh <project> <pkg> "<desc>" "<author>" "<email>" "<org>"`.
3. `just install && just check && just test`.

**Option B — manual copy**:

```bash
gh repo clone rararulab/py-template my-new-project
cd my-new-project
rm -rf .git && git init
./setup-template.sh my-new-project my_new_project \
    "A tiny tool that does X." \
    "Ada Lovelace" "ada@example.com" "myorg"
just install
```

## What the script does

`setup-template.sh` renames `src/__pkg__/` to `src/<your-package>/` and
substitutes the placeholder tokens across `pyproject.toml`, `justfile`,
`README.md`, `AGENT.md`, `CLAUDE.md`, and the seed source/test files:

| Placeholder                  | Replaced with               |
|------------------------------|-----------------------------|
| `__PROJECT_NAME__`           | distribution name (kebab OK) |
| `__pkg__` / `__PKG__`        | import name (snake_case)     |
| `__PROJECT_DESCRIPTION__`    | one-line description         |
| `__AUTHOR_NAME__`            | author display name          |
| `__AUTHOR_EMAIL__`           | author email                 |
| `__GITHUB_ORG__`             | GitHub org/user              |

The script deletes itself when done.

## After bootstrap

```bash
just                # list recipes
just install        # uv sync + pre-commit install
just check          # ruff + ruff-format --check + mypy --strict + pyright
just test           # pytest + coverage gates
just fmt            # ruff format + ruff check --fix
just run hello      # invoke the CLI
just build          # wheel + sdist
just docs           # serve docs at http://127.0.0.1:8000
just docs-test      # build docs strict (CI parity)
```

## Layout

```
.
├── pyproject.toml          # deps, mypy/pyright strict, ruff, coverage
├── justfile                # task runner
├── .pre-commit-config.yaml # ruff + uv-lock + hygiene hooks
├── .release-please-config.json     # release-please bump + changelog config
├── .release-please-manifest.json   # current version (managed by release-please)
├── CHANGELOG.md                    # written by release-please, do not edit
├── mkdocs.yml                      # docs site config (material + mkdocstrings)
├── .github/
│   ├── actions/setup-python-env/   # composite: install uv + python + uv sync
│   ├── dependabot.yml              # weekly uv + actions bumps
│   ├── pr-title-checker-config.json
│   ├── pull_request_template.md
│   └── workflows/
│       ├── main.yml                # check → tests (matrix) → build-wheel
│       ├── pr-title-checker.yml    # enforce Conventional Commit titles
│       ├── release-please.yml      # tag → release → wheel/sdist (+ optional PyPI)
│       └── docs.yml                # mkdocs gh-deploy on push to main
├── scripts/
│   ├── check_coverage.py           # per-module coverage gate (stdlib only)
│   └── check_version_tag.py        # tag ↔ pyproject.version consistency
├── docs/
│   ├── index.md  api.md
│   ├── guide/{install,usage}.md
│   └── dev/{contributing,release}.md
├── src/__pkg__/
│   ├── __init__.py                 # exports + __version__
│   ├── core.py                     # library API
│   └── cli.py                      # typer entry point
└── tests/
    ├── test_core.py
    └── test_cli.py
```

## Customising

- **Coverage gates**: edit `scripts/check_coverage.py:MODULE_GATES` once you
  have real modules. Follow the ratchet policy in the module docstring.
- **Python versions**: bump `requires-python`, `tool.mypy.python_version`,
  `tool.ruff.target-version`, `.python-version`, and the CI matrix together.
- **Lint rules**: `[tool.ruff.lint].select` is intentionally broad —
  remove categories per project if noise outweighs signal.
- **Strict typing**: weakening any `tool.mypy` / `tool.pyright` setting
  belongs in the same PR as the rationale.

## Post-clone setup (Pages + PyPI)

GitHub Pages and PyPI Trusted Publishing need one-time GitHub-side
configuration that the template can't do for you. A Claude Code skill
lives at `.claude/skills/publish-setup/SKILL.md` and walks an agent
through it end-to-end.

Trigger it by asking Claude (in a clone of your new repo):

> "set up github pages and pypi publishing"

Or invoke directly: `/publish-setup`. The skill verifies prerequisites,
runs the `gh` API calls it can run itself, and tells you exactly what to
paste into PyPI's web form (the one thing it can't automate).

## Release flow

```text
PR merged → release-please opens / updates a release PR
release PR merged → tag X.Y.Z → GitHub release → wheel + sdist attached
                                              ↘ (optional) PyPI Trusted Publish
push to main → mkdocs gh-deploy → https://<org>.github.io/<project>/
```

See [`docs/dev/release.md`](docs/dev/release.md) for the full walkthrough,
including how to enable PyPI publishing.

## What this template deliberately leaves out

To keep the surface honest:

- No BDD / agent-spec / banned-frameworks checks — those were yaya-specific.
- No PyInstaller binary builds. Uncomment in the release workflow if you need
  single-file binaries.
- No Docker, no devcontainer. Add when CI parity demands it.

## License

Apache-2.0.
