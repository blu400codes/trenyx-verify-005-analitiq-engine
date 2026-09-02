# verify-005 — PRELIMINARY verdict (NOT yet published; refuter + buyer's check pending)

**Target:** analitiq-ai/analitiq-engine @ 1eac312d · AI-built data sync engine (mixed Claude
Opus-5/Fable-5 authorship: 25/30 recent commits carry a Claude trailer — see ERRATA E1;
the anchored plan's "27/30 Opus 5" figure was wrong).

**Preliminary (updated after the 20-plant matrix): STRONG — shipped code correct; suite strong at
the core with six mapped test gaps.** Between ledgerly (EXEMPLARY, 14/16) and kontext (7/11): the
combined kill count is **14/20 (70%)**, with every high-stakes data-path plant caught and every
escape in a guard/comparison edge. The two most valuable escapes are regressions of the project's
OWN fixed issues (#307, #234) shipping green — the "fix without a fence" class. Findings are
recommendation-in-tests, ledgerly-style; no security or data-loss bug in shipped code.

1. **Internally correct** — the three highest-stakes native invariants are sound: the incremental
   cursor is inclusive + tie-breakered (no boundary drop); the checkpoint is written only on a
   destination-acked commit and a failed batch is *contractually forbidden* from advancing it
   (`client.py`: "a failed batch must never advance the checkpoint"); the DLQ returns `False` and
   logs `critical` on true loss, and its stubs raise rather than fake success. Type fidelity uses
   `pc.cast(safe=True)` (fails loud on lossy narrowing) and tags Decimal/datetime for lossless
   cursor round-trip.
2. **Evidence supports the claims** — the "never lose data / only sync what changed / data arrives
   correctly" README promises are backed by the code and by a 3632-test suite that caught **6/6**
   planted defects, including the two highest-stakes ones.
3. **No security or data-loss finding in the shipped code.** The one honest *seam* worth naming (not
   a bug): the engine's default retry semantics is AT_LEAST_ONCE unless a handler declares otherwise —
   documented, and consistent with "never lose data" (no loss; exactly-once is per-handler).

**Before publication (owed):** (a) the fuller matrix pass (§ matrix.md honesty note); (b) an
independent REFUTER on this verdict; (c) the pre-publish BUYER'S CHECK on the repo; (d) `ots upgrade`
on the anchor; (e) since this is a clean bill, no private security disclosure is required — publish
as a pre-registered blind EXEMPLARY (like ledgerly), optionally a friendly note to the maintainer.
