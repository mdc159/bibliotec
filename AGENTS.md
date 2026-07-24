# AGENTS.md — bibliotec

## For PR reviewers (Codex): the house rubric

End every review with `Score: N/5` — one point per criterion met, naming the criterion lost for any missing point:

1. **Truthful** — descriptions and claims match what the change actually does; nothing asserted without support.
2. **Receipts** — factual claims cite their source (file, log, upstream repo); no vibes.
3. **Minimal & positive** — the smallest change that does the job, stated as how-to procedure; no rule-creep, no mandates, no "never/don't" doctrine, no blanket rules the user didn't make.
4. **Portable** — platform-neutral: no machine-specific absolute paths, hostnames, or hard-coded model IDs where a routing tier belongs.
5. **Consistent** — agrees with the `orchestration-playbook` catalog source; reintroduces nothing retired in its lessons register; the word "canonical"/"canon" is banned.

Catalog entries for fleet practice must point to the-fleet; verification practice must point to herdr-verifier. Flag mandate language, uncited claims, and contradictions with the playbook lessons register. Role definitions sourced from the-fleet must keep `model: inherit`. Be terse and evidence-first; fewer, higher-signal comments.

## For all other agents

Operating procedure lives in the `orchestration-playbook` catalog source; start a new machine at `cookbook/bootstrap.md`. This file's rubric section is for PR review only.
