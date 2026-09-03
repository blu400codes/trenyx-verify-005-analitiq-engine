# Maintainer response — analitiq-engine#489 (2026-09-03T06:56:54Z, via the project's Analitiq-Bot account)

**All six escapes independently reproduced and confirmed.** They re-ran our method (neuter the
behaviour, run the full suite) AND added five positive-control mutations on the same regions
that had to fail (13 / 1 / 3 / 2+1 / 12 failures) to rule out "green because uncollected."
Labelled `P2` / `radius/contained` / `bug`. Their baseline: 3628 passed / 4 skipped / 3632
collected (ours: 3627 / 5 — one env skip differs).

## Two corrections to our findings (accepted; record updated)
- **F2 rationale was wrong (gap real).** We inherited the guard comment's "statements
  unbounded." Actual regression: `derive_statement_timeout_seconds(0)` → `0.0` →
  `asyncio.timeout(0.0)` fires immediately on the async-SQLAlchemy path: **every statement
  instantly cancelled**. Only ADBC/sync paths (`generic.py:616` nullcontext) are unbounded.
  Scope: the in-tree sender cannot trip it (settings clamp non-positive → 30; `client.py:1000`
  ignores a falsy budget); defends only against version-skewed / third-party senders.
- **F4 and F5 were UNDER-rated.** Hint-exposure is a credit discount, not a severity grade —
  we let the discount bleed into the severity. On the merits: **F5 is the strongest item in
  the set** (silent, corrupts the persisted watermark, permanently skips records on every later
  incremental sync; realistic trigger is sub-second precision variance — `".000Z"` vs `"Z"`
  compares equal under ISO parse but LESS under lexical since `ord('.') < ord('Z')`). **F4 is a
  reproduced hard `TypeError`** on any nullable tie-breaker column, not an ordering nit.
  Severities upgraded: F5 → MEDIUM-HIGH (top of set), F4 → MEDIUM.

## Their taxonomy is sharper than ours: three shapes, not one
- **Wiring unfenced** — F1 and F3 (F1 is the cleanest instance: view AND predicate each
  fenced, only the joining line bare; control E = 12 failures proves it).
- **Fixture monoculture** — F2, F4, F5: every fixture supplies well-formed homogeneous input
  (always a positive ack budget, always a populated tie-breaker, always same-offset
  same-precision `Z`); no test constructs the input that separates a guard from its happy
  path. Fix = adversarial fixture data. (Ledgerly's evenly-dividing reconciler fixture was
  the same disease — this names it.)
- **Unreachable defensive branch** — F6: `_derive_or_verify_endpoint_id` (`mode="after"`)
  always populates the field, so the guard cannot fire via `parse_endpoint_ref`. A
  delete-protection test, not a latent defect. INFO stands.

## Their fix plan: three PRs, mutation-verified
1. F1 alone (re-fences #307; needs a fake `Readable` capturing the `checkpoint` kwarg).
2. F4 + F5 (same file, same root cause, cheapest tests).
3. F2 + F3 + F6 (three small negative-case tests).
Each PR re-runs its exact mutation and confirms the new test goes red before merge.
Sharper detail on F3: `test_send_batch_emits_actual_written_count` already EXECUTES the
critical-log line every run (patches `open` to fail) but asserts only `emit_dlq_log` kwargs and
never inspects the logger — "the strongest possible form of your point."

Note for the record: they did not visit the engagement repo or act on anything outside the
issue text. The responder is the project's bot account; no human reviewer named yet.
