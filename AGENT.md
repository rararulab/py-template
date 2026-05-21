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

## 4. Workflow — issue → branch → PR (mandatory)

**No edits on `main`.** One-line fixes included. State machine:

```
gh issue create (use a template)
  → git checkout -b <type>/<slug>     # or: git worktree add .worktrees/<slug>
  → edit + just check + just test     # inside branch / worktree only
  → push + gh pr create               # PR body uses .github/pull_request_template.md
  → gh pr checks --watch              # green before reporting done
  → merge on GitHub
```

Required labels on every issue and PR: `agent:{claude|codex}` + type
(`bug|enhancement|refactor|chore|documentation`) + component (`src|cli|
tests|ci|docs|build`).

**The GitHub issue is the single source of task truth.** Agents MUST read
the issue body (especially the **Agent Task Packet** and **Completion
Criteria** sections) and the latest issue comments before editing. Do
not create shadow plan/task files. Planner notes go in issue comments;
implementation notes go in the PR body (**Issue context used** +
**Deviations** + **Agent notes**); reviewer findings go in PR reviews.

Use the issue templates under [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/)
— each one forces the Agent Task Packet + Completion Criteria fields.

Multi-agent: one agent, one branch (or worktree), one PR. Coordinate via
issue comments, never by editing each other's branches. Parallel only
for disjoint files; otherwise stack PRs.

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
