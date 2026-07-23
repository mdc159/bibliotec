# bibliotec

![bibliotec — one catalog feeding the fleet](images/bibliotec_banner.svg)

The fleet's source of truth: one catalog of skills, agents, and prompts that every machine and every agent harness pulls from. House doctrine lives in this repo; working tools live in their own repos and are referenced by URL — the `use` flow pulls either the same way. Nothing is copied until asked for; freshness is built into the act of using (`use` pulls first).

## Start here

**New agent or new machine → [`cookbook/bootstrap.md`](cookbook/bootstrap.md)** — prerequisites, clone, model providers, smoke test. Then:

| Read | For |
|---|---|
| [`playbook/SKILL.md`](playbook/SKILL.md) | How the fleet operates: orchestrator role, worker launch, routing tiers, verification, PR discipline |
| [`playbook/documentation.md`](playbook/documentation.md) | The documentation contract — the one binding rule: what gets recorded, where, in what form |
| [`playbook/lessons.md`](playbook/lessons.md) | Retired conventions and the mistakes that retired them |
| [`gauntlet/SKILL.md`](gauntlet/SKILL.md) | The defined exam a model passes to hold a fleet role |
| [`cookbook/kickoff.md`](cookbook/kickoff.md) | Starting a new project from any pane |
| [`library.yaml`](library.yaml) | The catalog itself |

## How it works

![The ring of watchers — builders verified, verifiers certified, the user overrules everything](images/ring_of_watchers.svg)

The library is a pure agent application — no scripts, no CLI: `SKILL.md` plus the [`cookbook/`](cookbook/) recipes teach any harness that reads skill files (Claude Code, Pi, Hermes, …) how to `use`, `sync`, `push`, and manage the catalog. Sources are GitHub URLs or local paths; fetching an asset pulls its whole parent directory so scripts and references travel with it.

Principles this repo runs on: accurate description is the guarantee (docs verified where written, execution verified where run); positive procedure only, history in the lessons register; changes land by pull request on the locked main.

## Credit

Built on [IndyDevDan's **the-library**](https://github.com/disler/the-library) — his reference-catalog design (catalog-not-vendor, agentic cookbook, agent-as-runtime) is the foundation, and his broader practice is this fleet's reference implementation (see the playbook's authority section). Adaptations here: house doctrine vendored into the repo (playbook, gauntlet, roles, prompts), fleet bootstrap and kickoff recipes, and a PR-locked main. Upstream license retained in [`LICENSE`](LICENSE).
