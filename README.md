# bibliotec

![bibliotec — one catalog feeding the fleet](images/bibliotec_banner.svg)

The fleet's catalog: one index of skills, agents, and prompts that every machine and every agent harness pulls from. Doctrine and working tools live in the repositories they serve and are referenced by URL — the `use` flow pulls either the same way. Nothing is copied until asked for; freshness is built into the act of using (`use` pulls first).

## Start here

**New agent or new machine → [`cookbook/bootstrap.md`](cookbook/bootstrap.md)** — prerequisites, clone, model providers, smoke test. Then:

| Read | For |
|---|---|
| [`orchestration-playbook`](https://github.com/mdc159/the-fleet/blob/main/playbook/SKILL.md) | How the fleet operates: orchestrator role, worker launch, routing tiers, verification, PR discipline |
| [`playbook lessons`](https://github.com/mdc159/the-fleet/blob/main/playbook/lessons.md) | Retired conventions and the mistakes that retired them |
| [`gauntlet`](https://github.com/mdc159/herdr-verifier/blob/main/gauntlet/SKILL.md) | The defined exam a model passes to hold a fleet role |
| [`cookbook/kickoff.md`](cookbook/kickoff.md) | Starting a new project from any pane |
| [`library.yaml`](library.yaml) | The catalog itself |

## How it works

![The ring of watchers — builders verified, verifiers certified, the user overrules everything](images/ring_of_watchers.svg)

The library catalog remains an agent application: `SKILL.md` plus the [`cookbook/`](cookbook/) recipes teach any harness that reads skill files (Claude Code, Pi, Hermes, …) how to `use`, `sync`, `push`, and manage the catalog. Harness adapters may carry a small verified helper beside the skill in the repository it serves when the native configuration surface needs deterministic, idempotent edits; [`hermes-onboarding`](https://github.com/mdc159/the-fleet/blob/main/hermes-onboarding/SKILL.md) is the current example. Sources are GitHub URLs or local paths; fetching an asset pulls its whole parent directory so scripts and references travel with it.

Principles this repo runs on: accurate description is the guarantee (docs verified where written, execution verified where run); positive procedure only, history in the lessons register; changes land by pull request on the locked main.

## Credit

Built on [IndyDevDan's **the-library**](https://github.com/disler/the-library) — his reference-catalog design (catalog-not-vendor, agentic cookbook, agent-as-runtime) is the foundation, and his broader practice is this fleet's reference implementation (see the playbook's authority section). Adaptations here: fleet bootstrap and kickoff recipes, and a PR-locked main. Fleet doctrine, practice, roles, and verification assets remain in their serving repositories and are cataloged by reference. Upstream license retained in [`LICENSE`](LICENSE).
