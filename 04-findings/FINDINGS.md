# verify-005 findings — analitiq-engine @ 1eac312d (2026-09-02)

**Verdict: STRONG.** Shipped code correct — no security or data-loss defect found. The
3,632-test suite caught **14/20** planted defects, including every plant in the hot data
path. All six escapes are TEST gaps (recommendation-in-tests, no code change required),
verified live-and-untested individually below.

## The one pattern behind the escapes
The suite fences **components** exhaustively and misses **wiring and guard edges**:

| # | escape | what exists | what's missing | sev |
|---|--------|-------------|----------------|-----|
| F1 | truncate_insert resumes from a persisted cursor (re-break of their fixed **issue #307**) | `TestFullRefreshCheckpoint.test_get_cursor_never_resumes` unit-tests the checkpoint **view** (mocked inner), citing #307 | nothing tests the **dispatch** (`stream_processor` selecting the view for truncate_insert) — remove the wiring, suite stays green | MEDIUM (test-gap on a known data-loss class) |
| F2 | handshake without an ack budget accepted → statements unbounded (the **issue #234** guard) | the guard itself, well-commented | no test sends a nonconforming handshake (`ack_timeout_seconds` absent) | LOW-MED |
| F3 | batch-level DLQ loss no longer logged critical | single-record "record lost permanently" critical IS asserted (`test_dead_letter_queue.py:481`) | the batch summary ("N of M records lost permanently") is not | LOW |
| F4 | record missing the tie-breaker field wins the boundary | `test_compute_max_with_tie_breakers` (happy path) | no None-tie-breaker case | LOW *[HINT-EXPOSED — plan §0]* |
| F5 | datetime-string cursors compared lexically | datetime encode/round-trip tests | no mixed-offset string comparison through `_compare_values` | LOW *[HINT-EXPOSED — plan §0]* |
| F6 | endpoint ref with no endpoint_id accepted (`None.json`) | the defense-in-depth guard | no test names `endpoint_document_id` at all | INFO (contract validator derives the id upstream) |

## What the suite is genuinely excellent at (measured, not asserted)
All 14 hot-path plants caught: failed-batch-advances-checkpoint, no-ack-reported-success,
lost-DLQ-record-reported-stored (+ phantom count, + inverted review filter), key-order-dependent
dedup digest, unsafe lossy casts, Decimal→float narrowing (cursor bind AND forensic record),
tz-drop on the cursor, malformed-tag passthrough, manifest-less archive, not-ready-sink write.

## Recommendation (one line)
Fence the wiring, not just the parts: one integration test per fixed issue asserting the
*dispatch* (esp. #307, #234), plus the four edge cases above. ~6 small tests total.
