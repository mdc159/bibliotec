# Codex review, summoned locally

Get a rubric'd Codex review of any branch without dashboard setup — runs on the node's Codex OAuth, reads the repo's `AGENTS.md`.

```bash
cd <repo checkout> && git checkout <branch>
codex review "Review this branch relative to origin/main. Apply the house rubric from AGENTS.md exactly: end with 'Score: N/5', one point per criterion, naming any criterion lost."
```

Post the result to the PR with `gh pr comment <n> --body-file <saved-output>`. GitHub-comment summons (`@codex review`) additionally need a per-repo Codex Cloud environment created in the ChatGPT app; automatic reviews on PR open need the per-repo review switch. This local path needs neither.
