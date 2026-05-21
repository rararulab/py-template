# __PROJECT_NAME__ — Agent Index

> This file is the entry point for AI coding agents (Claude Code, Codex,
> Cursor) working on this repo. Read it before editing.

## 1. Style anchors

[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html);
type-driven design (mypy strict + pyright strict — make invalid states
unrepresentable); Zen of Python.

## 2. Ground truth

- `just check` (ruff + mypy --strict + pyright) is the lint/type gate.
- `just test` (pytest + per-module coverage gates) is the test gate.
- CI is the final word — `gh pr checks --watch` green before reporting done.

## 3. Constraints

- Python 3.12+, `uv` for envs, `just` for tasks.
- English only in code, comments, commits, docs.
- Conventional Commits. Never `--no-verify`.
- Every public module/class/function has a Google-style docstring
  explaining **why**, not **what**. Inline comments mark non-obvious
  invariants only.
- Source under `src/__pkg__/`. Tests under `tests/`. Stdlib-only scripts
  under `scripts/`.

## 4. Workflow

No edits on `main`. Use issue → branch (or worktree) → PR. One-liners
included. Required PR labels: type (`bug|enhancement|refactor|chore|docs`)
+ component.

## 5. Anti-sycophancy

Push back on wrong asks; cite the rule. Disagree with broken code or
tests directly — no softening.

## 6. Layout

```
src/__pkg__/    # library + CLI
tests/          # pytest
scripts/        # stdlib-only helpers (coverage gate, version-tag check)
docs/           # mkdocs-material site (auto-deployed on push to main)
.github/        # CI + release-please + dependabot + PR templates
```

## 7. Releases

Driven by release-please. Conventional Commit messages on `main` →
release PR → merge → tagged release → wheel + sdist attached. Never edit
`CHANGELOG.md` or `.release-please-manifest.json` by hand; they are
machine-managed. See [docs/dev/release.md](docs/dev/release.md).

## 8. Publishing setup

GitHub Pages and PyPI Trusted Publishing require one-time GitHub-side
configuration. Use the bundled skill `.claude/skills/publish-setup/SKILL.md`
— it walks through both end-to-end with verification signals. Invoke
when the user asks to "enable pages", "publish docs", "set up pypi", or
similar.
