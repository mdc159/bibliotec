# Fact-Source Map

What to audit, and the source of truth for each claim category. Used by drift audits: a documented claim is checked against its source below; mismatches are reported as findings with patches, never silently worked around.

## Docs under audit

- Vault cluster: `03-Resources/Agentic Terminal Stack/*.md` (documentation — must not contradict live reality or present retired procedure as current)
- This repo's own `SKILL.md`, `playbook/`, `cookbook/`, `agents/`, `library.yaml`

## Sources of truth by claim category

| Claim category | Source of truth | How to check |
|---|---|---|
| herdr CLI syntax, subcommands, version | The installed binary | `herdr --version`; run the command group help |
| Live fleet composition, pane IDs, agent states | The running session | `herdr agent list`, `herdr pane list` |
| Pi providers and models available | The installed Pi config | `pi` provider/model listing on the machine |
| Repo locations, names, visibility, remotes | git and GitHub | `git remote -v`; `gh repo view <repo>` |
| File and directory paths | The filesystem that owns the path | `test -e <path>` |
| Operational conventions (launch, routing, roles) | `playbook/SKILL.md` in this repo | Read it; vault notes must defer to it, not restate stale versions |
| Retired conventions and their reasons | `playbook/lessons.md` | Read it |
| Verifier status and evidence | `herdr-verifier` repo: `runs/*.jsonl`, tests | Read run logs; `just test` |
| Upstream patterns (what Dan's code does) | `~/Projects/IDD/repos/` clones | Read the cited file |

## Finding format

```
- <path>:<line> — <category>
  Claim: <quoted text from the doc>
  Actual: <verified value>
  Verified via: <command or file path>
  Patch:
    <<< <old text>
    >>> <new text>
```

One blank line between findings. No preamble or summary prose — findings only, so reports collate mechanically.
