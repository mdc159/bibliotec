---
name: hermes-onboarding
description: Use when installing, refreshing, verifying, or troubleshooting bibliotec integration for a Hermes Agent profile. Runs the idempotent Hermes onboarding helper, preserves existing profile instructions, configures external skill discovery through the Hermes CLI, and can execute the Herdr/Pi workhorse smoke test.
version: 1.0.0
author: bibliotec fleet
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, onboarding, bibliotec, herdr, pi]
    related_skills: [library, orchestration-playbook, herdr]
---

# Hermes onboarding

## Overview

This skill ports bibliotec's machine bootstrap into a Hermes profile. The helper at `scripts/hermes_onboard.py` keeps bibliotec as the source of truth: it clones or fast-forwards the checkout, points Hermes at that checkout instead of copying skills, installs one managed fleet-bootstrap block in `SOUL.md`, validates discovery, and optionally proves worker launch through Herdr and Pi.

The helper uses public `hermes`, `git`, and `herdr` CLI surfaces. It does not read `.env` files, print credentials, change model-provider logins, or edit another Hermes profile unless the caller explicitly passes its path.

## When to use

Load this skill when the user asks to:

- onboard a new Hermes machine into the bibliotec fleet;
- automate or repeat the manual steps in `cookbook/bootstrap.md`;
- refresh or verify an existing Hermes/bibliotec integration;
- install the fleet bootstrap into a specific Hermes profile;
- run the prescribed Hermes/Herdr integration smoke test.

For general catalog use after onboarding, load `library`. For project orchestration, load `orchestration-playbook`.

## Standard workflow

### 1. Confirm scope

Resolve the target profile before making changes:

- Default profile: `${HERMES_HOME:-~/.hermes}`
- Explicit profile: pass its absolute profile directory with `--hermes-home`

Do not infer another profile merely because it exists. Completion criterion: the report's `hermes_home` is the profile the user intended.

### 2. Preview

From this skill directory, run:

```bash
python3 scripts/hermes_onboard.py --dry-run --json
```

Optional locations:

```bash
python3 scripts/hermes_onboard.py \
  --checkout ~/.claude/skills/library \
  --hermes-home ~/.hermes \
  --dry-run --json
```

The preview checks command availability and reports intended checkout, config, and bootstrap actions without writing. Completion criterion: the preview names no unintended profile or checkout.

### 3. Apply and verify

```bash
python3 scripts/hermes_onboard.py --json
```

The helper performs this sequence:

1. Clone bibliotec when absent, or fast-forward a clean `main` checkout.
2. Refuse to update dirty, detached, or non-`main` checkouts rather than switching or discarding work.
3. Read `skills.external_dirs` with `hermes config get`.
4. Keep an existing matching path, append to an existing YAML list by index, or use Hermes's supported scalar form for the first path.
5. Refuse to overwrite a different scalar path because the CLI cannot safely convert that scalar into a list.
6. Install or refresh one marker-delimited bootstrap block in `SOUL.md`, migrating the older unmarked bibliotec stanza when present.
7. Run `hermes config check` and confirm Hermes lists `library` and `orchestration-playbook`.

Completion criterion: JSON returns `"ok": true` and `skills_verified` includes both required skills.

### 4. Run the worker smoke test

From a Herdr-managed pane (`HERDR_ENV=1`):

```bash
python3 scripts/hermes_onboard.py \
  --smoke-test \
  --smoke-model <playbook cheap/iteration-tier provider/model> \
  --json
```

The helper creates a sibling pane with `--no-focus`, starts a fresh Pi workhorse, asks it to read bibliotec's `agents/workhorse.md`, requires a durable artifact and exact `DONE` receipt, and closes the created pane in a `finally` path. The artifact is retained under `<hermes-home>/artifacts/` as the receipt.

Pass the playbook's cheap/iteration-tier provider/model for this node explicitly, and override `--smoke-model` when that tier resolves differently on another machine; provider login remains Pi's responsibility. Completion criterion: `smoke_artifact` points to a readable artifact containing the expected receipt and no disposable worker pane remains.

### 5. Activate global instructions

Hermes reads `SOUL.md` when a session starts. Existing sessions retain their cached prompt. Tell the user to start a fresh session or run `/reset` after successful onboarding; no gateway restart is needed solely for this file change.

Completion criterion: a fresh session can load `orchestration-playbook` without manually opening bibliotec files.

## Other modes

Verify without changing anything:

```bash
python3 scripts/hermes_onboard.py --verify-only --json
```

Develop or test from a bibliotec feature branch without invoking the clean-`main` updater:

```bash
python3 scripts/hermes_onboard.py --skip-update --json
```

The latter is for development only. Normal onboarding pulls clean `main` before relying on fleet instructions.

## Common pitfalls

1. **Passing a JSON-looking array to `hermes config set`.** The CLI stores it as a scalar string. The helper uses a scalar for the first directory and indexed updates for an existing list.
2. **Running against the wrong profile.** Pass `--hermes-home` explicitly when the target is not the active profile.
3. **Expecting current-session prompt replacement.** Skill discovery refreshes through config, but `SOUL.md` takes effect in a new/reset session.
4. **Running the smoke test outside Herdr.** The helper stops before pane control unless `HERDR_ENV=1`.
5. **Using a work-in-progress checkout as fleet truth.** The updater refuses dirty and non-`main` checkouts; use `--skip-update` only while developing this workflow.
6. **Treating optional tools as fatal.** `git` and `hermes` are required. `gh`, `herdr`, `pi`, `uv`, and `just` are reported when absent; `herdr` and `pi` become required only for `--smoke-test`.

## Verification checklist

- [ ] Intended Hermes profile path appears in the report
- [ ] Bibliotec checkout is clean `main` or was cloned successfully
- [ ] `skills.external_dirs` resolves to the checkout without clobbering another path
- [ ] `SOUL.md` contains exactly one managed bibliotec block
- [ ] `hermes config check` passes
- [ ] `library` and `orchestration-playbook` are discovered
- [ ] Optional Herdr/Pi smoke artifact contains the expected `DONE` receipt
- [ ] Created worker pane was closed
- [ ] User knows `/reset` or a new session activates the global bootstrap
