# verify-005 findings — analitiq-engine @ 1eac312d (2026-09-02)

**Verdict: STRONG.** Shipped code correct — no security or data-loss defect found. The
3,632-test suite caught **14/20** planted defects, including every plant in the test-exercised
data path (P11's truncate-insert path is production data path too — that is what makes F1 the headline). All six escapes are TEST gaps (recommendation-in-tests, no code change required),
verified live-and-untested individually below.

## Severity note (2026-09-03)
Severities re-graded ON MERITS after the maintainer's reproduction; the hint-exposure discount is
recorded in its own `credit` column and no longer lowers a grade (it never should have). See
MAINTAINER-RESPONSE.md for the two accepted corrections.

## The one pattern behind the escapes (superseded: three shapes — see MAINTAINER-RESPONSE.md)
The suite fences **components** exhaustively and misses **wiring and guard edges**:

| # | escape | what exists | what's missing | sev (merits) | credit |
|---|--------|-------------|----------------|-----|-----|
| F1 | truncate_insert resumes from a persisted cursor (re-break of their fixed **issue #307**) | `TestFullRefreshCheckpoint.test_get_cursor_never_resumes` unit-tests the checkpoint **view** (mocked inner), citing #307 | nothing tests the **dispatch** (`stream_processor` selecting the view for truncate_insert) — remove the wiring, suite stays green | MEDIUM-HIGH: re-opens the #307 data loss silently | blind |
| F2 | handshake without an ack budget accepted → statements unbounded (the **issue #234** guard) | the guard itself, well-commented | no test sends a nonconforming handshake (`ack_timeout_seconds` absent) | MEDIUM: instant cancellation of every statement on the async path (NOT "unbounded" — maintainer-corrected); third-party-sender scope | blind |
| F3 | batch-level DLQ loss no longer logged critical | single-record "record lost permanently" critical IS asserted (`test_dead_letter_queue.py:481`) | the batch summary ("N of M records lost permanently") is not | LOW-MED: aggregate loss alert line silently removable | blind |
| F4 | record missing the tie-breaker field wins the boundary | `test_compute_max_with_tie_breakers` (happy path) | no None-tie-breaker case | MEDIUM: reproduced hard TypeError on any nullable tie-breaker (maintainer-upgraded) | hint-exposed (plan §0) |
| F5 | datetime-string cursors compared lexically | datetime encode/round-trip tests | no mixed-offset string comparison through `_compare_values` | MEDIUM-HIGH: silent persisted-watermark corruption, permanent record skips; '.000Z' vs 'Z' trigger (maintainer: strongest in set) | hint-exposed (plan §0) |
| F6 | endpoint ref with no endpoint_id accepted (`None.json`) | the defense-in-depth guard | no test names `endpoint_document_id` at all | INFO: unreachable defensive branch (validator always populates) — delete-protection test only | blind |

## What the suite is genuinely excellent at (measured, not asserted)
All 14 hot-path plants caught: failed-batch-advances-checkpoint, no-ack-reported-success,
lost-DLQ-record-reported-stored (+ phantom count, + inverted review filter), key-order-dependent
dedup digest, unsafe lossy casts, Decimal→float narrowing (cursor bind AND forensic record — both HINT-EXPOSED plants per plan §0/ERRATA E2; the catches credit the suite, not the auditor),
tz-drop on the cursor, malformed-tag passthrough, manifest-less archive, not-ready-sink write.

## Design notes (refuter-surfaced; not defects, worth one sentence each)
- `DeadLetterQueue.send_batch` returns `None`, so the caller cannot see partial capture loss —
  T3's "capture failure is not swallowed" holds at log level (critical + honest counts), not at
  contract level. A `bool`/count return would close it.
- `store.py` `json.dumps(..., default=str)` silently stringifies any cursor type `encode_value`
  does not tag (e.g. UUID) — speculative, no demonstrated consequence.

## Recommendation (one line)
Fence the wiring, not just the parts: one integration test per fixed issue asserting the
*dispatch* (esp. #307, #234), plus the four edge cases above. ~6 small tests total.
