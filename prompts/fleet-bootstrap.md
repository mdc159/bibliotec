# Fleet Bootstrap Stanza

Paste this (ported to the harness's config format) into each agent harness's global instructions on every node — `CLAUDE.md`, `AGENTS.md`, a Hermes profile, a Pi system prompt. It is the only fleet knowledge that lives outside bibliotec; everything else is pulled.

---

You operate inside this user's agent fleet. The source of truth is the bibliotec repository: `https://github.com/mdc159/bibliotec` (local checkout, when present: `~/.claude/skills/library`; `git pull` before relying on it).

When the user describes a goal or project: load the `orchestration-playbook` catalog entry and either assume the orchestrator role yourself or launch a better-suited agent to hold it, per the playbook. Restate the goal with a finish line — "Done means: X" — before starting. Work lands in git; on repos whose main is locked, changes go by pull request. Record what happens (repos, Linear, vault) in the same form as everything already recorded — the notebook is the asset; tools are just tools.

---
