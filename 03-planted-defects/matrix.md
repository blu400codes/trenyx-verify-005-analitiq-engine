# Planted-defect matrix — verify-005 (analitiq-engine @ 1eac312d)

Baseline as shipped: **3627 passed, 5 skipped, 0 failed** (3632 collected).
Each plant applied one at a time to the real code, target's OWN suite re-run
(`pytest -x -q`), then reverted (`git checkout`). Tree verified clean after.

| id | invariant | defect planted | site | result |
|----|-----------|----------------|------|--------|
| P1 | T2 | failed batch WITH a committed_cursor now advances the checkpoint (`not success` → `False`) | `src/grpc/client.py` | **CAUGHT** (1 failed / 2597 passed) |
| P2 | T3 | a permanently-lost DLQ record reports as stored (`return False` → `return True`) | `src/state/dead_letter_queue.py:161` | **CAUGHT** (1 / 442) |
| P3 | T4* | lossy narrowing/overflow silently truncates (`safe=True` → `safe=False`) [HINT-EXPOSED — §0/E2] | `src/engine/mapping.py:1210` | **CAUGHT** (1 / 706) |
| P4 | T4* | cursor datetime loses tz (aware→naive) across the resume round-trip [HINT-EXPOSED — §0/E2] | `src/state/store.py:168` | **CAUGHT** (1 / 2841) |
| P5 | T1* | equal cursor value bypasses tie-breaker selection (`> 0` → `>= 0`) | `src/grpc/cursor.py:147` | **CAUGHT** (1 / 3157) |
| P6 | T3 | phantom record: DLQ count incremented even when the write failed | `src/state/dead_letter_queue.py:369` | **CAUGHT** (1 / 443) |

**Matrix pass 1: 6 / 6 caught.** (See pass 2 below — combined: **14 / 20**.)

- **P5 is HINT-EXPOSED** (contamination boundary, plan §0): it sits in the keyset-cursor
  area glimpsed during the authorship check. It is reported with that discount; the code
  there was already sound on the native read, so the plant measures suite coverage, not a
  found bug.
- P3 and P6 anchors matched twice; the first occurrence (the line noted) was planted —
  deterministic, and CAUGHT either way.

## Honesty note on matrix size
This is a **6-plant** matrix, smaller than prior engagements (trading-bot 11, kontext 11,
ledgerly 16, payload-reserve 13). 6/6 is a 100% catch RATE but on a thinner sample, and it
does not yet exercise T5 (idempotent dedup) or T6 (config rejection) with a plant. A second
pass (T5/T6 + F-BOUNDARY-DOUBLE + an exception-swallow) should bring it to ~11 before this is
published as EXEMPLARY, to match the rigor of the earlier public audits.

## Matrix pass 2 (14 additional plants — operator-requested expansion)

| id | inv | defect planted | site (file · exact anchor) | result |
|----|-----|----------------|------|--------|
| P7 | T2 | send that reached NO ack reported successful (batch silently dropped) | `src/grpc/client.py` · `return BatchResult(` | **CAUGHT** |
| P8 | T1* | record MISSING the tie-breaker field wins the boundary [HINT-EXPOSED] | `src/grpc/cursor.py` · `if a_val is None:` | **ESCAPED** |
| P9 | T4 | malformed tagged cursor passes through instead of failing to clean re-scan | `src/state/store.py` · `if not isinstance(raw, str):` | **CAUGHT** |
| P10 | T5 | row digest key-order-dependent → keyless dedup misses → duplicates on replay | `cdk/cdk/record_identity.py` · `canonical = json.dumps(basis, sort_keys=True, default=str)` | **CAUGHT** |
| P11 | T2 | truncate_insert resumes from persisted cursor (**their own issue #307, replanted**) | `src/engine/stream_processor.py` · `if self._is_truncate_insert():` | **ESCAPED** |
| P12 | T6 | archive without pipelines/manifest.json hydrates and runs | `src/runtime_archive.py` · `REQUIRED_FILES = ("pipelines/manifest.json",)` | **CAUGHT** |
| P13 | T3 | partial DLQ batch loss no longer logged critical | `src/state/dead_letter_queue.py` · `if written_count < len(batch):` | **ESCAPED** |
| P14 | T6 | endpoint ref with no endpoint_id accepted (engine reads None.json) | `src/config/endpoint_resolver.py` · `if ref.endpoint_id is None:` | **ESCAPED** |
| P15 | T1* | datetime-string cursors compared lexically [HINT-EXPOSED] | `src/grpc/cursor.py` · `if isinstance(a, str) and isinstance(b, str):` | **ESCAPED** |
| P16 | T4 | DLQ forensic record narrows Decimal to float | `src/state/dead_letter_queue.py` · `if isinstance(obj, Decimal):` | **CAUGHT** |
| P17 | T4* | Decimal cursor flattened to float (precision lost in resume bind) [HINT-EXPOSED — §0/E2] | `src/state/store.py` · `if isinstance(value, Decimal):` | **CAUGHT** |
| P18 | T6 | handshake without ack budget accepted (statements unbounded; the issue #234 guard) | `src/destination/server.py` · `if not schema_msg.ack_timeout_seconds:` | **ESCAPED** |
| P19 | T3 | DLQ review filter inverted (your failed records hidden) | `src/state/dead_letter_queue.py` · `and record.get("pipeline_id") != pipeline_id` | **CAUGHT** |
| P20 | T5 | not-ready sink no longer rejects | `cdk/cdk/base_handler.py` · `reason = self.not_ready_reason(stream_id)  # skipcq: PYL-E` | **CAUGHT** |

**Combined kill count: 14 / 20 (70%).** Zero plant errors; tree verified clean after each pass.

**Exact mutations:** `run_matrix.py` / `run_matrix2.py` beside this file hold every plant's full `old`→`new` text (reconstructed 2026-09-03 from the session record after the working copies were lost with a session; edits identical to those run 2026-09-02). A retest re-applies the same edit against the fixed tree.

## The six escapes — what they actually say (pre-refuter read)

The suite catches every plant in the **hot data path** (checkpoint advance, ack contracts,
dedup digest, type fidelity, DLQ write honesty). Every escape sits in a **guard or comparison
edge** the happy path never exercises:

1. **P11 + P18 are the headline: two of the project's own hardest-won fixes are not pinned by a
   regression test.** Issue #307 (truncate_insert must ignore a persisted resume cursor) and the
   issue #234 guard (reject a handshake without an ack budget) both ship green when re-broken.
   The exact class ledgerly's finding was — a fix without a fence.
2. **P13/P14**: defense-in-depth guards ("can't happen" per the contract) with no test feeding
   the can't-happen input — the critical-loss log line and the None-endpoint_id guard.
3. **P8/P15** [both HINT-EXPOSED, discounted per plan §0]: tie-breaker None-ordering and the
   ISO-parse fallback in cursor comparison are untested edges.

**No shipped-code defect found** — every escape is a TEST gap; the code itself behaved
correctly on the native reads. Escape-verification (fixture check per the harness lesson —
confirm each escaped branch is live) + independent refuter still owed before any of this is a
claimed finding.
