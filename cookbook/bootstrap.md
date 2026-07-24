# Bootstrap — bring a fresh machine into the fleet

Agentic install: an agent on the new machine executes this; a human can follow it by hand. The fleet spans Mac, Windows, and Linux — where a step is platform-specific, port it to the native system and verify your port there (description is verified where written; execution is verified where run).

## 1. Prerequisites

Confirm each is on `PATH`, installing with the platform's package manager where missing:

- `git` and `gh` (authenticate: `gh auth status`, else `gh auth login`) — needed for the private repos
- `herdr` — terminal multiplexer, from https://github.com/ogulcancelik/herdr (everybody runs herdr)
- `pi` — multi-model runner: `npm install -g @earendil-works/pi-coding-agent`
- `uv` and `just`

## 2. Install bibliotec

```bash
git clone https://github.com/mdc159/bibliotec ~/.claude/skills/library
```

(Windows: the equivalent user-profile skills path; adapt and verify.) Confirm `SKILL.md` and `library.yaml` exist and `LIBRARY_REPO_URL` in `SKILL.md` reads `https://github.com/mdc159/bibliotec`.

## 3. Hermes automated integration

After the clone, a Hermes agent can apply and verify its harness-specific port in one command:

```bash
python3 ~/.claude/skills/library/hermes-onboarding/scripts/hermes_onboard.py --json
```

From a Herdr-managed pane, include the live worker receipt:

```bash
python3 ~/.claude/skills/library/hermes-onboarding/scripts/hermes_onboard.py \
  --smoke-test --smoke-model <playbook cheap/iteration-tier provider/model> --json
```

The helper points the active Hermes profile at this checkout, installs one managed fleet-bootstrap block, validates the profile, and preserves the smoke artifact. It reads no credential files. Pass `--hermes-home <profile-path>` for a non-default profile, and start a fresh Hermes session after success so the new global instructions load.

Non-Hermes harnesses, and manual Hermes ports, continue with the remaining steps.

## 4. Configure model providers

Pi resolves the routing tiers in the `orchestration-playbook` catalog entry to whatever subscriptions this machine holds. Configure the providers you have (zai, kimi-coding, openai-codex, openrouter, ollama); keys and OAuth logins are per-machine and never live in this repo.

## 5. Pull the playbook and roles

Using the library skill (`/library use <name>`), or manually per `cookbook/use.md`:

- `orchestration-playbook` — the fleet procedure; whoever orchestrates loads this
- `scribe`, `builder`, `workhorse`, `verifier-herdr` — role definitions, as needed

## 6. Smoke test

Inside a herdr-managed pane (`HERDR_ENV=1`), run the playbook's worker launch once with a cheap-tier model and confirm the worker reaches `working`, writes its artifact, and settles. The machine is in the fleet when that passes.
