---
name: orchestration-playbook
description: Canonical procedures for orchestrating the herdr + Pi worker fleet — launching, driving, and verifying agent workers. Load when acting as fleet orchestrator.
---

# Orchestration Playbook

This is the correct way to run the fleet. Procedures enter this document only after being verified against the installed tools (currently herdr 0.7.5, Pi 0.81.1). When reality and this document disagree, verify against the tool, then overwrite this document. Retired conventions and the mistakes that retired them live in [lessons.md](lessons.md) — consult it when something here seems to contradict older material.

Authority for any convention question: IndyDevDan's repos (`~/Projects/IDD/repos/`) are the rules — we are cloning his practice, and what his code does is what we do. The user, and only the user, may overrule Dan; an overrule is recorded at the scope stated. Where his repos are silent, verified local experience fills the gap, then orchestrator extrapolation — always labeled as such, and never overriding either authority above it. Substrate substitutions (herdr for cmux/tmux, our model subscriptions for his defaults) follow his pattern on our tools and are recorded deliberately.

## Roles and model routing

The orchestrator is a role, not a particular agent — any capable agent (Claude, Hermes, or another) holds it by loading this playbook. The orchestrator writes briefs, plans, reviews results, and maintains this playbook. Workers do everything else. Everything operational lives in bibliotec: if a procedure exists only in some agent's private memory, it is in the wrong place — move it here. Any herdr-integrated agent kind is a valid worker. GPT models run through Pi's `openai-codex` provider (Codex OAuth billing) rather than the Codex CLI. For scripted automation, prefer Pi-hosted workers where equivalent — Pi's herdr integration carries lifecycle authority, instant prompt delivery, and observability.

| Need | Route (current resolution) |
|---|---|
| Briefs, planning, final review | The orchestrator role (strongest available model; currently Claude Fable, Hermes-capable) |
| Default substantial implementation | Pi → `openai-codex/...` (GPT models on Codex OAuth billing) |
| Hardest tasks and verification | Pi → `kimi-coding/k3` (1M context) |
| Bulk work and cheap iteration | Pi → `zai/glm-5.2` (flat-rate coding plan) |
| Offline / private | Pi → local models via Ollama |
| Exotic / new models | Pi → `openrouter/...` |

Definitions reference tiers (columns 1) so they stay portable across devices; each device resolves a tier to whatever subscription it holds.

## Canonical worker launch

Use this sequence for every worker.

1. **Split without stealing focus** — capture the pane ID from the JSON response (`.result.pane.pane_id`):

   ```bash
   herdr pane split --current --direction right --cwd "$PWD" --no-focus
   ```

2. **Wait for the shell** before touching the pane:

   ```bash
   herdr pane wait-output <pane-id> --match '<shell-prompt>' --timeout 30000
   ```

3. **Start a fresh agent** of the kind the worker definition calls for:

   ```bash
   herdr agent start <name> --kind <kind> --pane <pane-id> -- <kind-flags>
   # most common: --kind pi -- --model <provider/model>  (routed per tier)
   ```

4. **Submit the first prompt synchronously**, directing output to an artifact file:

   ```bash
   herdr agent prompt <name> "<task>; write the result to <artifact-path>" --wait --timeout 600000
   ```

   Confirm lifecycle state flipped to `working` before backgrounding. For later asynchronous prompts, confirm `status=working` before detaching.

Read results from the artifact file or the agent's session JSONL — these are the durable record of a worker's output.

## Recipes

**Worker beside the orchestrator.** Run the canonical launch in the current tab; keep your own focus. Read the artifact after the worker settles to `idle`/`done`.

**Model panel.** Fan one brief to two or three workers on different tiers, each with its own artifact path; compare the artifact files and synthesize.

**Isolated parallel work.** `herdr worktree create --branch <name>`, then the canonical launch inside the new workspace — one fresh agent per worktree. Review diff and artifact, then `herdr worktree remove --workspace <id>` for workspaces you created.

**Long-running shell job.** Canonical split and shell wait, then:

```bash
herdr pane run <pane-id> "mkdir -p .artifacts; <cmd> > .artifacts/<job>.log 2>&1; echo HERDR-JOB-DONE"
herdr pane wait-output <pane-id> --match 'HERDR-JOB-DONE' --timeout 1800000
herdr notification show "<job> finished — read .artifacts/<job>.log" --sound done
```

Read the log file. Over SSH, set notifications to `terminal` mode.

**Answering a blocked worker.**

```bash
herdr agent wait <name> --until blocked
herdr agent get <name>            # then inspect the worker's artifact / session JSONL
herdr agent prompt <name> "<answer or corrective instruction>" --wait
```

Confirm the lifecycle returns to `working`. For interactive UI controls use `herdr agent send-keys <name> <key>`.

## Verification loop

Independent verification of worker turns runs from `~/Projects/herdr-verifier`:

```bash
just verify <builder-name>        # continuous watcher, K3 verifier
just demo <builder-name>          # watch exactly one live turn
```

The watcher records evidence to `runs/YYYY-MM-DD.jsonl`; verdicts are `VERIFIED` or `FEEDBACK`, with human escalation after the configured consecutive-feedback cap.

## Fleet hygiene

- Parse IDs from JSON responses.
- Close only panes, tabs, and workspaces you created.
- After `herdr update`, run `herdr integration status --outdated-only` and reinstall anything flagged.
- Restructure layouts with split → `pane swap --source-pane/--target-pane` → close your placeholder.
- Record every convention change in this playbook the session it is decided, and move the retired convention to [lessons.md](lessons.md).
