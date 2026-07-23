# Documentation Contract

The one binding rule for anything that adopts this library. Everything else in bibliotec is an offer — use it, adapt it, or skip it. This page is the requirement: work that happens gets recorded, the same way, in the same place, by every agent, every harness. "Done means: X" always includes "and the record exists per this contract" — it is part of the definition of finished, never a separate ask.

The toll is deliberately small: a frontmatter block and an index line. Low enough to never hinder a contribution; enough that every record is traceable (who produced it, under what mission, from what evidence) and findable (index-first).

## Where records go

Destinations are symbolic names; each node resolves them (same idiom as the model-routing tiers). Every kind of record has exactly one home.

| Record | Destination | Current resolution |
|---|---|---|
| Convention changes | playbook | bibliotec `playbook/lessons.md`, by PR |
| Certification status (current state) | playbook | bibliotec `playbook/SKILL.md` gauntlet section, by PR |
| Certification records (full exam evidence) | vault | idd-research `certifications/`, by PR |
| Narrative reports, analyses, research | vault | idd-research `reports/` / `research/`, by PR |
| Orchestrator handoffs | vault | idd-research `handoffs/`, by PR |
| Verification evidence | runs | herdr-verifier `runs/*.jsonl` |
| Mission work (code) | project repo | by PR on locked mains |
| Worker output | artifacts | `.artifacts/` in the project, path named in the launch prompt |
| Task tracking | tracker | Linear |

## The vault

Current resolution: `https://github.com/mdc159/idd-research` — interim until the vault finds its VPS home; when it moves, this resolution line changes and nothing else does.

The vault is index-first: `INDEX.md` at its root is the register — one line per record (date, type, worker, one-sentence hook, link). A record isn't in the vault until its index line is. Every record opens with the frontmatter block:

```yaml
---
date: 2026-07-23
worker: ver-gpt56-codex   # role-model-provider per the naming convention; or orchestrator, or user
type: report              # report | handoff | research | certification
mission: ""               # Linear ID or brief path, when one exists
source: ""                # repo, PR, or session that produced this, when one exists
---
```

Writes land by branch + PR. The vault's CI gate checks exactly the toll — frontmatter present, file in its typed directory, index line added — and nothing more. Format compliance lives in the server rule, not in any agent's memory.

## How the contract travels

1. **Bootstrap stanza** (`prompts/fleet-bootstrap.md`) — the orchestrator carries the contract from the first prompt of any session.
2. **Kickoff** (`cookbook/kickoff.md`) — stamps the contract pointer and this node's destination resolutions into the project's agent file (`CLAUDE.md` / `AGENTS.md`); every worker spawned with its cwd in the project inherits what-goes-where, whatever its harness.
3. **Worker launch step 4** (`playbook/SKILL.md`) — every first prompt names the artifact path the output lands at.
