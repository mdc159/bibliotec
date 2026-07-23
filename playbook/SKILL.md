---
name: orchestration-playbook
description: Use when the user describes a project, mission, or goal to build, or asks for multi-agent orchestration — assume or recruit the orchestrator role and follow these procedures (worker launch, routing tiers, verification, PR discipline, Done-means finish lines). Do NOT load for quick one-off tasks that need no fleet.
---

# Orchestration Playbook

This is the correct way to run the fleet. Procedures enter this document only after being verified against the installed tools (currently herdr 0.7.5, Pi 0.81.1). When reality and this document disagree, verify against the tool, then overwrite this document. Retired conventions and the mistakes that retired them live in [lessons.md](lessons.md) — consult it when something here seems to contradict older material.

What this repo guarantees is accurate description — layout, procedure, decisions, and their reasons, kept true. The fleet spans Mac, Windows, and Linux; assets are written platform-neutral where possible, and the consuming agent on each machine ports them to its native system and verifies its own port there. Description is verified where written; execution is verified where run.

Authority for any convention question: IndyDevDan's repos (`~/Projects/IDD/repos/`) are the rules — we are cloning his practice, and what his code does is what we do. The user, and only the user, may overrule Dan; an overrule is recorded at the scope stated. Where his repos are silent, verified local experience fills the gap, then orchestrator extrapolation — always labeled as such, and never overriding either authority above it. Substrate substitutions (herdr for cmux/tmux, our model subscriptions for his defaults) follow his pattern on our tools and are recorded deliberately.

## Roles and model routing

The orchestrator is a role, not a particular agent — any capable agent (Claude, Hermes, or another) holds it by loading this playbook. The orchestrator writes briefs, plans, reviews results, and maintains this playbook. Every mission brief and issue states its finish line up front — "Done means: X" — written when the purpose is stated; completing the mission means doing X, checked against that line, never re-asked at the end. Before asking the user anything, check whether an existing decision already answers it. Workers do everything else. Everything operational lives in bibliotec: if a procedure exists only in some agent's private memory, it is in the wrong place — move it here. Any herdr-integrated agent kind is a valid worker. GPT models run through Pi's `openai-codex` provider (Codex OAuth billing) rather than the Codex CLI. For scripted automation, prefer Pi-hosted workers where equivalent — Pi's herdr integration carries lifecycle authority, instant prompt delivery, and observability.

| Need | Route (current resolution) |
|---|---|
| Briefs, planning, final review | The orchestrator role (strongest available model; currently Claude Fable, Hermes-capable) |
| Default substantial implementation | Pi → `openai-codex/...` (GPT models on Codex OAuth billing) |
| Hardest tasks and verification | Pi → `kimi-coding/k3` (1M context) |
| Bulk work and cheap iteration | Pi → `zai/glm-5.2` (per-node subscription) |
| Offline / private | Pi → local models via Ollama |
| Exotic / new models | Pi → `openrouter/...` |

Definitions reference tiers (columns 1) so they stay portable across devices; each device resolves a tier to whatever subscription it holds.

## Worker launch

Use this sequence for every worker.

Name workers `<role>-<model>-<provider>` so a glance at the sidebar answers what it does, what it runs, and who bills the inference: `bld-glm52-zai`, `wrk-k3-kimi`, `scr-gpt56-codex`, `bld-qwen9b-hf`. Role prefixes: `bld` build, `wrk` bulk/research, `scr` docs, `ver` verify, `cal` gauntlet candidate. When Pi resolves a model by pattern, read the provider back from the start response or session before assuming who pays.

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

**Worker beside the orchestrator.** Run the worker launch in the current tab; keep your own focus. Read the artifact after the worker settles to `idle`/`done`.

**Model panel.** Fan one brief to two or three workers on different tiers, each with its own artifact path; compare the artifact files and synthesize.

**Isolated parallel work.** `herdr worktree create --branch <name>`, then the worker launch inside the new workspace — one fresh agent per worktree. Review diff and artifact, then `herdr worktree remove --workspace <id>` for workspaces you created.

**Long-running shell job.** Split and shell-wait as above, then:

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

## The Check-out Gauntlet

Bringing a new model into use? **Ask the user whether it runs the gauntlet, and talk it through.** The gauntlet itself = live calibration cycles through the verifier loop (`~/Projects/herdr-verifier/calibration/`); results are recorded here. Re-check roughly monthly or when a model version changes.

- Checked out (2026-07-23): **GLM-5.2** as builder (refused seeded-flaw delivery three ways, disclosed honestly); **Kimi K3** as verifier (7/7 correct live verdicts, including a 3-round FEEDBACK catch and behavioral verification).
- Not checked out: **Qwen3.5-9B** (malformed tool calls, incomplete delivery, repeated red suites).
- Work from a checked-out builder, verified by a checked-out verifier, ships on `VERIFIED` alone — the orchestrator sees only escalations. Escalation machinery proven live 2026-07-23 (evidence: `herdr-verifier/runs/`, `calibration/scorecard.md`).

## Verification loop

Independent verification of worker turns runs from `~/Projects/herdr-verifier`:

```bash
just verify <builder-name>        # continuous watcher, K3 verifier
just demo <builder-name>          # watch exactly one live turn
```

The watcher records evidence to `runs/YYYY-MM-DD.jsonl`; verdicts are `VERIFIED` or `FEEDBACK`, with human escalation after the configured consecutive-feedback cap.

## E2B sandbox execution (capability on the shelf)

Optional isolation, engaged when the orchestrator or user chooses it — for example unattended Gauntlet runs or genuinely untrusted external code. Not a default and not a mandate: this is an R&D rig and the user sets the risk posture. Verified live 2026-07-23 (Linear 121-62; evidence in `herdr-verifier/runs/`).

- **One-off command in a microVM** (from `~/Projects/herdr-verifier`):

  ```bash
  uv run sandbox/run_in_e2b.py --file <path> [--file ...] [--pip <pkg> ...] -- <command...>
  ```

  Boots a fresh E2B sandbox, uploads each file to `/home/user/work/`, installs `--pip` packages, runs the command there, streams output, prints `SANDBOX_ID:` and `EXIT_CODE:`, propagates the exit code, and always kills the sandbox. `E2B_API_KEY` comes from the environment or the repo-root `.env` (gitignored, orchestrator-placed).

- **Verification cycles with in-sandbox execution**: `just verify-e2b <builder>` / `just demo-e2b <builder>`. Same watcher, but the per-turn template `prompts/verify_on_stop_e2b.md` has the verifier run all candidate code inside the microVM and cite the `SANDBOX_ID:`/`EXIT_CODE:` lines as evidence; host bash stays read-only for the duration of that run by the template's design. (That containment applies only while E2B mode is selected — plain `just verify`/`demo` are unchanged.)

- Reference implementation: `~/Projects/IDD/repos/agent-sandboxes` (re-fetch from disler upstream on a new node).

## Pull requests

Changes to locked mains land by PR — one PR per coherent unit of work, not per commit; let small fixes ride with the next real PR. Self-merging your own PR is allowed **after** two reviews are in: CodeRabbit's automated review, and one independent opinion — another checked-out model reviewing the diff, or the user. (CodeRabbit is installed account-wide; the free tier rate-limits reviews, so a PR may need `@coderabbitai review` re-triggered or a short wait during high-volume stretches.)

## Fleet hygiene

Workers start fresh and end released: spawn a new agent per mission, release its pane when the work is delivered (artifacts and repos hold the results; pane context is disposable runtime state). This is the upstream pattern — cmux teams boot "a fresh 5-agent team as a new workspace" and their roster files are "regenerated on every spawn" (`learning-cmux-with-agents`: `.claude/commands/spawn-fs-team.md`, `.team/README.md`). Persistent staff (a verifier, a scribe) is the deliberate exception, restarted fresh at mission boundaries.


- Parse IDs from JSON responses.
- Close only panes, tabs, and workspaces you created.
- After `herdr update`, run `herdr integration status --outdated-only` and reinstall anything flagged.
- Restructure layouts with split → `pane swap --source-pane/--target-pane` → close your placeholder.
- Record every convention change in this playbook the session it is decided, and move the retired convention to [lessons.md](lessons.md).
