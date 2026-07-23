# Lessons Register

History, not procedure. The playbook states only the correct way; this register records where we came from and why conventions changed, so confusion has a lookup path. Newest first.

## 2026-07-22 — GPT models launch via Pi's `openai-codex` provider; direct `--kind codex` retired

GPT models route through Pi (`--kind pi --model openai-codex/...`) on Codex OAuth billing. Direct Codex launches were retired because the Codex TUI runs on the terminal alternate screen (output unreadable via pane scrollback), resumed sessions swallowed the first prompt, and it required per-kind exceptions (`--dangerously-bypass-approvals-and-sandbox`, blank `OPENAI_API_KEY` in the pane env to protect OAuth billing). Scope note: this decision covers only the GPT/Codex path — other herdr-integrated kinds remain valid workers, with Pi preferred (not mandated) for scripted automation. A same-day playbook draft overstated this as "all workers are Pi agents"; the user corrected it within hours — an argument for keeping decisions narrow and quoting them, not paraphrasing them.

## 2026-07-22 — Vault demoted from canon to documentation

Early docs treated the Obsidian vault as the operational source of truth. The playbook drifted (it still taught codex-direct after the Pi-hosted decision). Canon now lives only in bibliotec; vaults hold reports, research, and narrative. A claim's presence in a vault note proves nothing about current procedure.

## 2026-07-22 — Verify commands against the installed binary before canonizing

`herdr pane wait-output` was documented while the installed herdr 0.7.3 lacked it; the command became real in a later release (verified present in 0.7.5). Rule now embedded in the playbook header: procedures enter canon only after running against the installed tool.

## 2026-07-22 — Repo naming: `mdc159/the-library` is the upstream fork

Publishing the library failed on a name collision: `mdc159/the-library` is the user's public fork of disler/the-library (upstream reference — keep). The private catalog repo is `mdc159/bibliotec`.

## 2026-07-22 — herdr 0.7.5 quirks

Same-tab `pane move` no-ops; restructure via split → `pane swap` → close placeholder. Reads from alternate-screen agents return nothing useful — use artifact files or session JSONLs.

## 2026-07-22 — Seeded-flaw live demo could not fool GLM-5.2 + K3

Attempting to demo the verifier's FAIL path by asking GLM-5.2 to build flawed artifacts failed: the model stayed correct and honest. Escalation path proven by unit tests only; live calibration (orchestrator-authored flaws) planned.
