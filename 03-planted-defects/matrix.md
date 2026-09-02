# Planted-defect matrix — verify-005 (analitiq-engine @ 1eac312d)

Baseline as shipped: **3627 passed, 5 skipped, 0 failed** (3632 collected).
Each plant applied one at a time to the real code, target's OWN suite re-run
(`pytest -x -q`), then reverted (`git checkout`). Tree verified clean after.

| id | invariant | defect planted | site | result |
|----|-----------|----------------|------|--------|
| P1 | T2 | failed batch WITH a committed_cursor now advances the checkpoint (`not success` → `False`) | `src/grpc/client.py` | **CAUGHT** (1 failed / 2597 passed) |
| P2 | T3 | a permanently-lost DLQ record reports as stored (`return False` → `return True`) | `src/state/dead_letter_queue.py:161` | **CAUGHT** (1 / 442) |
| P3 | T4 | lossy narrowing/overflow silently truncates (`safe=True` → `safe=False`) | `src/engine/mapping.py:1210` | **CAUGHT** (1 / 706) |
| P4 | T4 | cursor datetime loses tz (aware→naive) across the resume round-trip | `src/state/store.py:168` | **CAUGHT** (1 / 2841) |
| P5 | T1* | equal cursor value bypasses tie-breaker selection (`> 0` → `>= 0`) | `src/grpc/cursor.py:147` | **CAUGHT** (1 / 3157) |
| P6 | T3 | phantom record: DLQ count incremented even when the write failed | `src/state/dead_letter_queue.py:369` | **CAUGHT** (1 / 443) |

**Kill count: 6 / 6 caught.**

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
