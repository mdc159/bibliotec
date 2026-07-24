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
set -euo pipefail
SKILLS_ROOT="${SKILLS_ROOT:-$HOME/.claude/skills}"
CATALOG_CHECKOUT="${CATALOG_CHECKOUT:-$SKILLS_ROOT/library}"
git clone https://github.com/mdc159/bibliotec "$CATALOG_CHECKOUT"
test -f "$CATALOG_CHECKOUT/SKILL.md"
test -f "$CATALOG_CHECKOUT/library.yaml"
```

## 3. Install the-fleet operational checkout

```bash
set -euo pipefail
FLEET_REPO_URL="https://github.com/mdc159/the-fleet.git"
SKILLS_ROOT="${SKILLS_ROOT:-$HOME/.claude/skills}"
FLEET_CHECKOUT="${FLEET_CHECKOUT:-$SKILLS_ROOT/the-fleet}"
if [ ! -d "$FLEET_CHECKOUT/.git" ]; then
  git clone "$FLEET_REPO_URL" "$FLEET_CHECKOUT"
fi
test -d "$FLEET_CHECKOUT/.git"
```

## 4. Hermes automated integration

Use the helper from the full the-fleet checkout so it can manage and verify both sibling checkouts in place.

```bash
set -euo pipefail
FLEET_REPO_URL="https://github.com/mdc159/the-fleet.git"
SKILLS_ROOT="${SKILLS_ROOT:-$HOME/.claude/skills}"
CATALOG_CHECKOUT="${CATALOG_CHECKOUT:-$SKILLS_ROOT/library}"
FLEET_CHECKOUT="${FLEET_CHECKOUT:-$SKILLS_ROOT/the-fleet}"
if [ ! -d "$FLEET_CHECKOUT/.git" ]; then
  git clone "$FLEET_REPO_URL" "$FLEET_CHECKOUT"
fi
python3 "$FLEET_CHECKOUT/hermes-onboarding/scripts/hermes_onboard.py" \
  --skills-root "$SKILLS_ROOT" \
  --catalog-checkout "$CATALOG_CHECKOUT" \
  --checkout "$FLEET_CHECKOUT" \
  --json
```

The helper points the active Hermes profile at the shared skills root, installs one managed fleet-bootstrap block, validates both sibling checkouts, and keeps the layout split between the catalog and the operational repo. It reads no credential files.

## 5. Configure model providers

Pi resolves the routing tiers in the `orchestration-playbook` catalog entry to whatever subscriptions this machine holds. Configure and log in to the providers you have (zai, kimi-coding, openai-codex, openrouter, ollama); keys and OAuth logins are per-machine and never live in this repo.

## 6. Optional smoke test

After provider setup, and only from a Herdr-managed pane (`HERDR_ENV=1`), run the playbook's worker launch once with a cheap-tier model and confirm the worker reaches `working`, writes its artifact, and settles. The machine is in the fleet when that passes.

```bash
set -euo pipefail
FLEET_REPO_URL="https://github.com/mdc159/the-fleet.git"
SKILLS_ROOT="${SKILLS_ROOT:-$HOME/.claude/skills}"
CATALOG_CHECKOUT="${CATALOG_CHECKOUT:-$SKILLS_ROOT/library}"
FLEET_CHECKOUT="${FLEET_CHECKOUT:-$SKILLS_ROOT/the-fleet}"
if [ ! -d "$FLEET_CHECKOUT/.git" ]; then
  git clone "$FLEET_REPO_URL" "$FLEET_CHECKOUT"
fi
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SMOKE_MODEL="<playbook cheap/iteration-tier provider/model>"
python3 "$FLEET_CHECKOUT/hermes-onboarding/scripts/hermes_onboard.py" \
  --skills-root "$SKILLS_ROOT" \
  --catalog-checkout "$CATALOG_CHECKOUT" \
  --checkout "$FLEET_CHECKOUT" \
  --hermes-home "$HERMES_HOME" \
  --smoke-test \
  --smoke-model "$SMOKE_MODEL" \
  --json
```
