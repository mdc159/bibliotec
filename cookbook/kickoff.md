# Kickoff — start any new project

From any herdr pane, any agent that carries the fleet bootstrap stanza (see `prompts/fleet-bootstrap.md`) can do this itself when you describe the goal. The manual sequence it follows:

1. `herdr workspace create --label "<project>"` — one workspace per mission. New repo if needed: `gh repo create`; apply the PR-only ruleset to main if wanted; then check the review panel — CodeRabbit covers new public repos automatically, but Codex has needed a manual per-repo switch in the Codex app (user-side; verify on the first PR whether it showed up, and record here once known whether the manual step is always required).
2. Seat an orchestrator in the workspace via the playbook's worker launch; it becomes the orchestrator by reading `playbook/SKILL.md`.
3. Brief it in three sentences: the goal, **"Done means: X"**, and where the plan lives (Linear project + issues).
4. Walk away. Workers route per tier; verification via `just verify` in herdr-verifier when receipts are wanted; PRs to locked mains; escalations arrive as notifications; everything is recorded.

New model in the mix? Ask the user whether it runs the gauntlet, and talk it through.
