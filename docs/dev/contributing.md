# Contributing

## Setup

```bash
git clone https://github.com/__GITHUB_ORG__/__PROJECT_NAME__
cd __PROJECT_NAME__
just install
```

## Daily loop

```bash
just check     # ruff + mypy --strict + pyright
just test      # pytest + coverage gates
just fmt       # auto-format
```

## Commit convention

[Conventional Commits](https://www.conventionalcommits.org/). PR titles must
match `^(feat|fix|test|refactor|chore|style|docs|perf|build|ci|revert)(\(.+\))?:.*`
— enforced by the `PR Title Checker` workflow. release-please consumes the
log to bump the version and write `CHANGELOG.md`.

## Coverage gates

Global floor is 90%. Per-module gates live in `scripts/check_coverage.py` and
follow a ratchet policy: when a module's actual coverage exceeds `gate + 0.5`,
raise the gate to `floor(actual) - 0.5` in the same PR. Gates never retreat
without explicit discussion.
