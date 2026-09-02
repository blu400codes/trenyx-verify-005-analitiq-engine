# Disclosure draft — public GitHub issue on analitiq-ai/analitiq-engine
**Status:** DRAFT — not ready until Reviews block below records an independent pass.
**Channel rationale:** benign test-gap recommendations, no security consequence → public-first
justified (ledgerly precedent). No exploit content.

---
**Title:** Six test gaps found by a pre-registered adversarial audit (all recommendation-in-tests; shipped code looks correct)

Hi — I run independent verification of AI-built systems (pre-registered blind audits;
attack plan hashed and anchored before reading a line of the implementation). I put
analitiq-engine @ `1eac312d` through one: baseline your suite green (3627/3627), then
planted 20 real defects one at a time into the invariant-bearing paths and measured what
your suite catches.

**The good news, measured: 14/20 caught — including everything in the hot data path.**
A failed batch advancing the checkpoint, a no-ack batch reported delivered, a lost DLQ
record reported stored, a key-order-dependent dedup digest, Decimal→float narrowing,
tz-drop on the cursor — your suite kills all of it. I found **no security or data-loss
bug in the shipped code**; the checkpoint/ack/DLQ discipline is unusually careful.

**The six escapes share one shape: the component is fenced, the wiring isn't.**

1. **Issue #307 can silently regress.** `TestFullRefreshCheckpoint.test_get_cursor_never_resumes`
   pins the checkpoint *view* (with a mocked inner) — but nothing pins the *dispatch* in
   `stream_processor` that selects it for truncate_insert. Remove that `if` and the suite
   stays green, which re-opens the exact data-loss #307 fixed.
2. **The issue #234 guard is untested.** No test sends a handshake without
   `ack_timeout_seconds`; neuter the guard and everything passes.
3. The **batch-level** DLQ loss summary ("N of M records lost permanently") can be removed
   green — the single-record critical *is* asserted, the batch path isn't.
4. `compute_max_cursor` tie-breakers: no case where a record is missing the tie-breaker
   field (None ordering).
5. `_compare_values`: no mixed-offset datetime-string comparison (the ISO-parse fallback
   path is unexercised).
6. `endpoint_document_id`'s None-guard has no test (defense-in-depth; lowest priority).

Each is ~one small test. Happy to share the full matrix (plant sites + per-plant suite
results) — the engagement repo with the pre-registration hash chain (OpenTimestamps +
issue timestamp) publishes alongside this so you can verify the method end to end.

No action needed beyond the tests; shipped behavior looked correct everywhere I probed.

— SK, Trenyx (independent verification; this audit was unsolicited and free, no strings)

---
**Reviews:** (required before Status: SENT)
- [ ] independent agent pass on this text
- [ ] operator voice pass
