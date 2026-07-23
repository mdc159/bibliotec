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

## 3. Configure model providers

Pi resolves the routing tiers in `playbook/SKILL.md` to whatever subscriptions this machine holds. Configure the providers you have (zai, kimi-coding, openai-codex, openrouter, ollama); keys and OAuth logins are per-machine and never live in this repo.

## 4. Pull the playbook and roles

Using the library skill (`/library use <name>`), or manually per `cookbook/use.md`:

- `orchestration-playbook` — the fleet procedure; whoever orchestrates loads this
- `scribe`, `builder`, `workhorse`, `verifier-herdr` — role definitions, as needed

## 5. Smoke test

Inside a herdr-managed pane (`HERDR_ENV=1`), run the playbook's canonical worker launch once with a cheap-tier model and confirm the worker reaches `working`, writes its artifact, and settles. The machine is in the fleet when that passes.
