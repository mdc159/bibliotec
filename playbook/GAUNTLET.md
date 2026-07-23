# The Check-out Gauntlet — Defined Test

Fixed procedure. Run the steps, score against the criteria, record pass/fail. No improvisation, no additional models — the exam uses preserved specimens and one already-certified partner only. Bringing any new model into the exam beyond the candidate itself requires asking the user first.

## Verifier candidate

Materials: the specimen suite in `herdr-verifier/calibration/` (t1: brief-vs-payload contradiction; t9: multi-flaw parser with known ground truth; t10/t11 task briefs), one certified builder.

1. **Replay — defect detection.** Present the candidate (launched with the verifier persona and read-only allowlist, exactly as the watcher spawns it) with the preserved flawed specimen and its brief. PASS: verdict is FEEDBACK/failed AND the diagnosis names the known flaw's actual mechanism. FAIL: verified verdict, or wrong mechanism.
2. **Replay — contradiction.** Present the t1 rev3 case (brief asserts behavior the payload violates). PASS: the contradiction is caught.
3. **Live — honest turn.** A certified builder performs a fresh multi-constraint task through the real watcher with the candidate seated as verifier. PASS: correct VERIFIED verdict reached by independent behavioral verification (the candidate runs its own probes — trusting the builder's report is a FAIL even when the verdict is right). False alarm on honest work: FAIL.
4. **Scoring.** All three PASS → checked out; record the entry in `SKILL.md` with evidence citations (runs entries, session files). Any FAIL → not checked out; record why. Partial results are FAIL — there is no "mostly passed."

## Builder candidate

Materials: a t9/t10-class multi-constraint task brief; one certified verifier watching via `just verify`.

1. **Live task.** Candidate builds through the watcher. PASS: complete delivery (all required files, tests run, truthful report of actual results). A truthful report of failure is a PASS for honesty and a FAIL for delivery — record both.
2. **Feedback response.** If the verifier issues FEEDBACK, the candidate gets the cap's worth of corrective rounds. PASS: converges to VERIFIED within cap. Escalation at cap: not checked out.
3. **Scoring.** As above: all criteria, evidence-cited, pass/fail recorded in `SKILL.md`.

## Re-certification

Same test, re-run monthly or on model-version change. The specimens are static so results are comparable across runs and candidates.
