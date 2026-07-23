# Kickoff — start any new project

From any herdr pane, any agent that carries the fleet bootstrap stanza (see `prompts/fleet-bootstrap.md`) can do this itself when you describe the goal. The manual sequence it follows:

1. `herdr workspace create --label "<project>"` — one workspace per mission. New repo if needed: `gh repo create`; apply the PR-only ruleset to main if wanted; then check the review panel — CodeRabbit covers new public repos automatically; Codex needs up to TWO user-side flips in the ChatGPT/Codex app: (a) the code-review switch (enables automatic reviews on PR open / draft-ready), and (b) a Codex Cloud environment for the repo (required for any `@codex` comment summons, including `@codex review` — confirmed empirically 2026-07-23). The Claude on-demand workflow (`@claude-review`) travels in `.github/workflows/` and needs no per-repo setup once the Claude GitHub App covers the account.
2. Stamp the documentation contract into the project's agent file (`CLAUDE.md` / `AGENTS.md`): a pointer to `playbook/documentation.md` plus this node's destination resolutions. Every worker spawned with its cwd in the project inherits what-goes-where from that file, whatever its harness.
3. Seat an orchestrator in the workspace via the playbook's worker launch; it becomes the orchestrator by reading `playbook/SKILL.md`.
4. Brief it in three sentences: the goal, **"Done means: X"** (which always includes the record existing per the documentation contract), and where the plan lives (Linear project + issues).
5. Walk away. Workers route per tier; verification via `just verify` in herdr-verifier when receipts are wanted; PRs to locked mains; escalations arrive as notifications; everything is recorded.

New model in the mix? Ask the user whether it runs the gauntlet, and talk it through.
