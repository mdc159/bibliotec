# Contribute — publish a skill, agent, or prompt to the fleet

For any fleet agent (Hermes, Claude, Pi workers, …) that has built something worth sharing. The catalog is the index, not the warehouse: your asset's bytes live in a git-reachable repo; bibliotec points at them.

## Steps

1. **Host the bytes.** Commit the asset to a GitHub repo the fleet can reach:
   - House-doctrine-grade assets (broadly useful, fleet-identity) may live inside bibliotec itself (`gauntlet/`, `agents/`, `prompts/` set the pattern) — added via the same PR as the catalog entry.
   - Everything else stays in its own repo (your machine's agent repo, a tool repo) — the catalog references it by URL, per the index-not-warehouse rule. A skill's `source` points at its `SKILL.md`; the `use` flow pulls the whole parent directory, so keep scripts/references beside it.
2. **Write it portable.** Description verified where written, execution verified where run: note any platform or harness assumptions in the asset itself so consuming agents can port and verify locally. Role definitions keep `model: inherit`.
3. **Catalog it.** Follow `cookbook/add.md` for the entry shape (name, description, source, optional `requires`), but land the `library.yaml` change **by pull request** — main is locked. Branch, add the entry (plus in-repo bytes if house-grade), open the PR.
4. **Reviews per the playbook**: CodeRabbit/Codex fire automatically; the merge practice applies. The PR description says what the asset does and where it came from ("Done means: cataloged and pullable by name").
5. **Verify from anywhere.** After merge, on any node: `library use <name>` — confirm the asset arrives intact. That pull is the publication test.

Same procedure for all three types — skills, agents (role/persona definitions), prompts. An agent that cannot open PRs hands steps 3–4 to its orchestrator with the entry fields prepared.
