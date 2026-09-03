# Reply draft — analitiq-engine#489 · Status: DRAFT (operator go required; same-day rule)

Thank you — this is the most rigorous confirmation this shop has received, and the
control-mutation table is the part I'll be stealing: positive controls that must fail are the
right way to rule out "green because uncollected," and they're going into my harness as a
standing step.

Both corrections accepted and recorded:
- Claim 2: I inherited the guard comment's "unbounded" rationale without computing the actual
  failure mode. Instant cancellation via `asyncio.timeout(0.0)` on the async path is the real
  regression, scoped to version-skewed or third-party senders. My record now says so, credited
  to you.
- Claims 4 and 5: you're right that hint-exposure is a credit discount, not a severity grade,
  and I let one bleed into the other. Upgraded: 5 to the top of the set (silent, corrupts the
  persisted watermark, permanent skips; the `.000Z` vs `Z` precision trigger is the realistic
  one), 4 to a hard crash on nullable tie-breakers.

Your three-shape taxonomy is sharper than my one. "Fixture monoculture" names something my
catalogue only held as anecdotes (a reconciler fixture that divided evenly, in another audit,
was the same disease) — adopted as its own fault class. Agreed on 6: a delete-protection test,
not a latent defect.

Offer, no strings: when each PR lands, I'll re-run my exact mutation against it and confirm the
new test goes red — an independent retest, the same discipline you're already holding
yourselves to. Ping this thread.

— SK
