# Lessons Register

History, not procedure. The playbook states only the correct way; this register records where we came from and why conventions changed, so confusion has a lookup path. Newest first.

## 2026-07-23 — Sandbox mandate rejected; security ships as opt-in capability

The 121-62 draft rule "uncertified builder ⇒ code runs in the microVM, period" was rejected by the user as a blanket mandate: this is an R&D rig, the user sets the risk posture, and security measures enter the playbook as capabilities with how-tos, engaged by choice (unattended runs, untrusted external code) — never as defaults. The mandate phrasing had crept in at mission-brief level, not from a user decision — a reminder to quote decisions at their stated scope and not let a brief's wording harden into doctrine. Playbook now carries "E2B sandbox execution (capability on the shelf)".

## 2026-07-23 — Watcher hung waiting `--until idle` on Pi builders that settle as `done`

The verifier watcher's first E2B cycle never fired: `herdr agent wait <builder> --until idle` blocks forever because Pi builders settle in state `done`, which `--until idle` never matches. Bare `herdr agent wait` (no `--until`) matches idle, done, or blocked — the correct settle set. Fixed in `herdr-verifier/watcher.py` (`wait_settled()`, regression-tested against a fake builder that settles as `done`). General rule: when waiting on lifecycle states, wait on the full settle set, not one named state.

## 2026-07-23 — Spawned agents don't inherit the orchestrator's env; secrets reach tools via repo-local .env

The K3 verifier's E2B runner failed with AuthenticationException: the verifier's pane shell predated/didn't inherit `E2B_API_KEY`. The verifier honored the no-host-execution rule and returned `unsure` rather than falling back — correct behavior, and the first live proof the isolation rule holds under pressure. Fix: the runner loads the repo-root `.env` (gitignored, orchestrator-placed, mode 600; env var takes precedence). Don't assume a worker pane's environment matches the shell that exported a key.

## 2026-07-22 — GPT models launch via Pi's `openai-codex` provider; direct `--kind codex` retired

GPT models route through Pi (`--kind pi --model openai-codex/...`) on Codex OAuth billing. Direct Codex launches were retired because the Codex TUI runs on the terminal alternate screen (output unreadable via pane scrollback), resumed sessions swallowed the first prompt, and it required per-kind exceptions (`--dangerously-bypass-approvals-and-sandbox`, blank `OPENAI_API_KEY` in the pane env to protect OAuth billing). Scope note: this decision covers only the GPT/Codex path — other herdr-integrated kinds remain valid workers, with Pi preferred (not mandated) for scripted automation. A same-day playbook draft overstated this as "all workers are Pi agents"; the user corrected it within hours — an argument for keeping decisions narrow and quoting them, not paraphrasing them.

## 2026-07-22 — Vault demoted from source of truth to documentation

Early docs treated the Obsidian vault as the operational source of truth. The playbook drifted (it still taught codex-direct after the Pi-hosted decision). Operational truth now lives only in bibliotec; vaults hold reports, research, and narrative. A claim's presence in a vault note proves nothing about current procedure.

## 2026-07-22 — Verify commands against the installed binary before adding them to the playbook

`herdr pane wait-output` was documented while the installed herdr 0.7.3 lacked it; the command became real in a later release (verified present in 0.7.5). Rule now embedded in the playbook header: procedures enter the playbook only after running against the installed tool.

## 2026-07-22 — Repo naming: `mdc159/the-library` is the upstream fork

Publishing the library failed on a name collision: `mdc159/the-library` is the user's public fork of disler/the-library (upstream reference — keep). The private catalog repo is `mdc159/bibliotec`.

## 2026-07-22 — herdr 0.7.5 quirks

Same-tab `pane move` no-ops; restructure via split → `pane swap` → close placeholder. Reads from alternate-screen agents return nothing useful — use artifact files or session JSONLs.

## 2026-07-22 — Seeded-flaw live demo could not fool GLM-5.2 + K3

Attempting to demo the verifier's FAIL path by asking GLM-5.2 to build flawed artifacts failed: the model stayed correct and honest. Escalation path proven by unit tests only; live calibration (orchestrator-authored flaws) planned.

## 2026-07-23 — Builder honesty defeats seeded-flaw delivery

Three mechanisms for delivering orchestrator-authored flaws through a live builder turn all failed against GLM-5.2: as courier it ran the forbidden tests and disclosed; as silent deliverer its truthful claim made the verdict legitimately VERIFIED; given a brief whose payload contradicted its stated requirement, it detected the contradiction by unprompted arithmetic and reported it. Live false claims come from weak models making natural mistakes (Qwen3.5-9B's malformed tool call yielded the first live FEEDBACK and the cap-3 escalation), not from aligned models pretending. Gauntlet candidates for the failure path should be genuinely weak, not instructed to deceive.

## 2026-07-23 — Verifier run records under-persist evidence

`runs/*.jsonl` entries store slice bounds and digests but not the brief/task name, builder session path, or builder model; scorecard collation had to infer them. When certification evidence matters, record launch details (model, provider, brief path) alongside the run, or improve `append_event()`.

## 2026-07-23 — Pi model patterns can resolve to surprise providers

`--model "Qwen3.5-9B"` resolved to the huggingface provider and burned the small HF included-credit pool; the assumption had been OpenRouter. Rule now in the playbook: name workers `<role>-<model>-<provider>` and read the provider back from the start response before assuming who pays.
