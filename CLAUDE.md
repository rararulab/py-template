# CLAUDE.md — __PROJECT_NAME__

Claude Code entry point. Read order:
1. [AGENT.md](AGENT.md) — canonical agent spec.

## Communication

- 用中文与用户交流。代码、注释、commit、文档全部英文。

## Anchors

@AGENT.md

## Claude-specific

- Before any code edit: confirm you are on a feature branch, not `main`.
- Before reporting done: run `just check && just test` locally, then
  `gh pr checks {PR} --watch` and paste the green summary.
- Use subagents for independent issues in parallel.
