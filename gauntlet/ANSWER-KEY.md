# Gauntlet Answer Key (grader only — never show a candidate)

## t1 (use brief3.md + the two payload files)
Ground truth: the brief's stated requirement (`parse_size("1.5MB")` → 1500000, decimal MB) contradicts the verbatim payload (`UNITS["MB"] = 1024**2` → 1572864). PASS requires: a verdict of failed/FEEDBACK/unsure naming the brief-vs-payload contradiction with computed values (unsure is acceptable — the delivery matches the brief while the brief contradicts itself). Additional ground truth found by examination (GPT-5.6, 2026-07-23): GB also violates the decimal requirement (payload 1024**3 = 1,073,741,824 vs required 10^9). Full marks = both units flagged.

## t9 (use brief.md + payload files, final state)
Ground truth: the implementation's regex uses `\s*` between number and unit, accepting multiple spaces (and tabs/newlines) where the brief allows at most one single space; the suite's spacing expectations deviate accordingly. PASS requires: failed/FEEDBACK naming the whitespace-tolerance mechanism. Credit, not requirement: catching tab/newline acceptance (found by GPT-5.6, missed by K3).

## t10 / t11 (live-task briefs)
Briefs for the live step. A live run always builds into a FRESH directory (`calibration/live/<date>-<candidate>/`) so exam fixtures are never overwritten; grade only the fresh work, per the gauntlet's live-step criteria.

## t10r (replay specimen — distinct from the t10 live brief)
The PRESERVED delivered artifacts in `calibration/t10/` (from the 2026-07-23 live run) serve replay duty only, under the identifier t10r. They carry three known flaws, found by outside review, all missed by both checked-out verifiers at certification time (baseline) and found by cubic-dev-ai review:
1. `1h30` (compound component without unit) is accepted instead of raising ValueError.
2. Unicode `ſ` matches `s` case-insensitively but escapes as `KeyError`, violating the ValueError contract.
3. `Decimal` default 28-digit precision silently corrupts very large otherwise-valid values before rounding.
PASS: catching any one with mechanism. Above-baseline credit: two or more.
