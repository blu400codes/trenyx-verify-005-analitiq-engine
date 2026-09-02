# ERRATA (the pre-registration is hash-anchored and stays byte-frozen; corrections live here)

## E1 — AI-authorship figure (found by the pre-publish buyer's check, 2026-09-02)
The anchored plan and early drafts state "27 of the last 30 commits carry a Co-Authored-By:
Claude Opus 5 trailer." **That is wrong.** The machine record at the pin (`git log -30`):
- **15/30** commits carry a Claude **Opus 5** trailer;
- **25/30** carry *some* Claude co-author trailer;
- **10/30** are Claude **Fable 5**-only.
Correct characterization: **mixed Claude Opus-5 / Fable-5 authored (25/30 any-Claude).**
How the error happened: the pre-reg attribution count matched commits containing *any*
AI-keyword line (including Claude-Session links), then was mislabelled as an Opus-5
trailer count. A trailer-line count must never be relabelled as a per-model commit count
without dedup and per-model matching.

## E2 — HINT-EXPOSED flags on P3/P17 (same check)
Plan §0 declares Decimal-narrowing (N03) inside the contamination boundary and promises it
flagged. Matrix rows P3 and P17 (both Decimal-narrowing plants, both **CAUGHT**) did not
carry the flag. They do now. Direction of the omission was favorable (caught plants earn
the *suite* credit, not the auditor), but the §0 promise is kept regardless.
