# Contribute — publish a skill, agent, or prompt to the fleet

For any fleet agent (Hermes, Claude, Pi workers, …) that has built something worth sharing. The catalog is the index, not the warehouse: your asset's bytes live in a git-reachable repo; bibliotec points at them.

## Steps

1. **Host the bytes.** Commit the asset to a GitHub repo the fleet can reach:
   - Place every asset in the repository it serves; bibliotec is the catalog and records the reference in the same PR or a follow-up catalog PR.
   - Everything else stays in its own repo (your machine's agent repo, a tool repo) — the catalog references it by URL, per the index-not-warehouse rule. A skill's `source` points at its `SKILL.md`; the `use` flow pulls the whole parent directory, so keep scripts/references beside it.
2. **Write it portable.** Description verified where written, execution verified where run: note any platform or harness assumptions in the asset itself so consuming agents can port and verify locally. Role definitions keep `model: inherit`.
3. **Catalog it.** Follow `cookbook/add.md` for the entry shape (name, description, source, optional `requires`), but land the `library.yaml` change **by pull request** — main is locked. Branch, add the entry (plus in-repo bytes if house-grade), open the PR.
4. **Reviews per the playbook**: CodeRabbit/Codex fire automatically; the merge practice applies. The PR description says what the asset does and where it came from ("Done means: cataloged and pullable by name").
5. **Verify from anywhere.** After merge, on any node: `library use <name>` — confirm the asset arrives intact. That pull is the publication test.

Same procedure for all three types — skills, agents (role/persona definitions), prompts. An agent that cannot open PRs hands steps 3–4 to its orchestrator with the entry fields prepared.

## Porting another harness's asset

Found a cataloged skill written for a different harness (a Hermes skill you want on Claude, or vice versa)? Adapt it locally and verify the port works — then decide:

- **Differences small** (paths, tool names, phrasing): push portability back into the ORIGINAL asset — neutral core plus inline harness notes — so one entry serves every harness. Prefer this; forks are pre-ordered drift.
- **Differences structural** (the harness's internals genuinely diverge): publish the port as its own entry, suffixed by harness (`<name>-claude`), with provenance in the description pointing at the origin entry so lineage is tracked and improvements can propagate.

The curator loop periodically reviews the catalog for fork drift and proposes merges.

## Catalog a source-owned skill

A **source-owned** skill keeps its bytes in the repository it serves; bibliotec holds only the catalog entry pointing at it. This is the preferred shape for any skill tightly bound to one tool's repo — the skill and the tool move together, so improvements can't drift apart.

Recipe:

1. **Bytes stay put.** The skill's `SKILL.md` (plus scripts/references beside it) lives in the serving repo, e.g. `skills/youtube-distill/` inside the `youtube-transcripts` repo. Do **not** copy the bytes into bibliotec — bibliotec is the catalog, not the warehouse (step 1 above).
2. **Use the serving repo's real default branch in the URL.** Branches differ per repo — `youtube-transcripts` is on `master`, `bibliotec` is on `main`, `the-fleet` is on `main`. A wrong branch 404s the `use` clone. Confirm before writing the entry:
   ```bash
   gh api repos/mdc159/youtube-transcripts --jq .default_branch   # -> master
   gh api repos/mdc159/bibliotec      --jq .default_branch   # -> main
   ```
   Then point `source` at `https://github.com/<org>/<repo>/blob/<default-branch>/skills/<name>/SKILL.md`.
3. **Match the entry description to the asset.** Once the bytes are committed, copy the skill's frontmatter `description` (or a faithful summary) into the catalog entry so the index and the asset agree. If the entry lands before the bytes (catalog-first), revisit the description when the skill ships.
4. **Follow the entry schema exactly** — `name`, `description`, `source`, optional `requires` (see `cookbook/add.md`). Skills point at `.../<name>/SKILL.md`; the `use` flow pulls the whole parent directory.
5. **Land by PR** (main is locked). The bytes may land in the same cycle in the serving repo or already exist; `library use <name>` is the publication test once both are merged.

Reference example in this catalog: [`youtube-distill`](../library.yaml) — bytes source-owned in `mdc159/youtube-transcripts` (`master`), entry in bibliotec (`main`).
