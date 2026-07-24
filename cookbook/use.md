# Use a Skill from the Library

## Context
Pull a skill, agent, or prompt from the catalog into the local environment. If already installed locally, overwrite with the latest from the source (refresh).

## Input
The user provides a skill name or description.

## Steps

### 1. Sync the Library Repo
Pull the latest catalog before reading:
```bash
cd <LIBRARY_SKILL_DIR>
git pull
```

### 2. Find the Entry
- Read `library.yaml`
- Search across `library.skills`, `library.agents`, and `library.prompts`
- Match by name (exact) or description (fuzzy/keyword match)
- If multiple matches, show them and ask the user to pick one
- If no match, tell the user and suggest `/library search`

### 3. Resolve Dependencies
If the entry has a `requires` field:
- For each typed reference (`skill:name`, `agent:name`, `prompt:name`):
  - Look it up in `library.yaml`
  - If found, recursively run the `use` workflow for that dependency first
  - If not found, warn the user: "Dependency <ref> not found in library catalog"
- Process all dependencies before the requested item

### 4. Determine Target Directory

First resolve the **harness** (the agent that will consume the installed skill), then its skills root.

**4a. Resolve the harness** (first match wins):

1. User passed `--harness <name>` on the command (e.g. `library use foo --harness hermes`) → use `<name>`.
2. Environment variable `HERMES_HOME` is set → harness is **Hermes Agent**.
3. Otherwise → harness is **Claude Code** (the catalog default).

**4b. Resolve the target root for the harness/type:**

| Harness | Type | Target root |
| --- | --- | --- |
| Hermes | skills | The active profile's **configured** skills root: if the fleet bootstrap ran (`cookbook/bootstrap.md` §4), it pointed Hermes at `$SKILLS_ROOT` (default `~/.claude/skills`) — use that. Otherwise `$HERMES_HOME/skills/` — if `HERMES_HOME` unset: `$LOCALAPPDATA/hermes/skills/` on Windows, else `~/.hermes/skills/`. When unsure, read the profile config before installing. |
| Hermes | agents / prompts | follow Hermes's own conventions; when unknown fall back to the Claude row and tell the user |
| Claude | skills / agents / prompts | `library.yaml` `default_dirs` — `global` if user said "global", a custom path if given, else `default` |
| any other `--harness <name>` | any | no catalog-known root — ask the user for the target root, or fall back to the Claude row and say so explicitly |

On Windows, `$HERMES_HOME` resolves to `C:\Users\<user>\AppData\Local\hermes` by default, so the Hermes skills root is `C:/Users/<user>/AppData/Local/hermes/skills/`. Verify the actual value before relying on it: `echo "${HERMES_HOME:-<unset>}"`.

For a **skill**, the install target is `<root>/<name>/` (the whole parent directory is copied in, per step 5).

### 5. Fetch from Source

**If source is a local path** (starts with `/` or `~`):
- Resolve `~` to the home directory
- Get the parent directory of the referenced file
- For skills: copy the entire parent directory to the target:
  ```bash
  cp -R <parent_directory>/ <target_directory>/<name>/
  ```
- For agents: copy just the agent file to the target:
  ```bash
  cp <agent_file> <target_directory>/<agent_name>.md
  ```
- For prompts: copy just the prompt file to the target:
  ```bash
  cp <prompt_file> <target_directory>/<prompt_name>.md
  ```
- If the agent or prompt is nested in a subdirectory under the `agents/` or `commands/` directories, copy the subdirectory to the target as well, creating the subdir if it doesn't exist. This is useful because it keeps the agents or commands grouped together.

**If source is a GitHub URL**:
- Parse the URL to extract: `org`, `repo`, `branch`, `file_path`
  - Browser URL pattern: `https://github.com/<org>/<repo>/blob/<branch>/<path>`
  - Raw URL pattern: `https://raw.githubusercontent.com/<org>/<repo>/<branch>/<path>`
- Determine the clone URL: `https://github.com/<org>/<repo>.git`
- Determine the parent directory path within the repo (everything before the filename)
- Clone into a temporary directory:
  ```bash
  tmp_dir=$(mktemp -d)
  git clone --depth 1 --branch <branch> https://github.com/<org>/<repo>.git "$tmp_dir"
  ```
- Copy the parent directory of the file to the target:
  ```bash
  cp -R "$tmp_dir/<parent_path>/" <target_directory>/<name>/
  ```
- Clean up:
  ```bash
  rm -rf "$tmp_dir"
  ```

**If clone fails (private repo)**, try SSH:
  ```bash
  git clone --depth 1 --branch <branch> git@github.com:<org>/<repo>.git "$tmp_dir"
  ```

### 6. Verify Installation
- Confirm the target directory exists
- Confirm the main file (SKILL.md, AGENT.md, or prompt file) exists in it
- **Hermes only** — confirm the harness can see it: reuse the **exact root resolved in step 4** (do not re-derive it here — a second derivation can pick a different path than the install used). Quick check (bash):
  ```bash
  ls "<root-from-step-4>/<name>/SKILL.md"   # should print the path, not 'No such file'
  ```
  Hermes loads skills from this root on the next session, so a successful `ls` is the publication signal.
- Report success with the installed path

### 7. Confirm
Tell the user:
- What was installed and where
- Any dependencies that were also installed
- If this was a refresh (overwrite), mention that
