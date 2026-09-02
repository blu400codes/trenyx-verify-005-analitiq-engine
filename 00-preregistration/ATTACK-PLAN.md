# Attack plan — verify-005 (pre-registered, BLIND)

**Target:** `analitiq-ai/analitiq-engine` (also referred to upstream as `analitiq-core`)
**Pin:** commit `1eac312d733b6db7f3e60fd47bae67016d74985e` (default branch `main`, committer date 2026-09-02T12:15:38Z)
**License:** Apache-2.0 · **What it is:** AI-managed data synchronization engine (extract → transform → load; incremental cursors, resume-on-interrupt, failed-record capture, gRPC source→destination, idempotent destination writes). Runs in Docker.
**AI-authorship signal:** 27 of the last 30 commits carry a `Co-Authored-By: Claude Opus 5` trailer (strongly Claude-built).
**Domain:** pipelines · **Catalogue:** faults v2 · **Pre-registered:** 2026-09-02
**Method:** blind — this plan is written from the PUBLIC README and repository metadata ONLY, before any implementation file is read. It is hashed (SHA-256), the hash is anchored to two independent clocks (OpenTimestamps → Bitcoin; and GitHub Issue #1 server timestamp on the private engagement repo), and only then is the target's source read.

---

## 0. Contamination boundary (honest disclosure — this is anchored, on purpose)

This pre-registration is blind **except** for a narrow, inadvertent exposure I am recording verbatim so a reader can see exactly what I knew before writing the plan:

While counting AI-authorship trailers via the commits API, commit-message **bodies** printed to my terminal (they should have been counted, not rendered). Six lines were visible, referencing internal mechanics around incremental pagination:

> "…keyset cursor reaches the next page", "Narrowing an integral Decimal to int is what lets a keyset cursor satisfy…", "`cursor_mapping_for`'s docstring still described the full-replication…", "an incremental stream whose cursor field no mapping names…", "a cursor sitting exactly on a declared…", "…checking it where the cursor…"

**Consequence, stated up front:** any finding whose mechanism is **keyset-cursor pagination, `Decimal→int` narrowing on a cursor, or the `cursor_mapping_for` mapping** is **hint-exposed, NOT blind-derived**, and will be labelled as such in the findings. Planted defects **N01** (cursor-boundary drop), **N03** (numeric narrowing), and — by adjacency — **N04** (datetime/cursor) fall inside this boundary and are flagged below.

Mitigating fact (not an excuse): incremental-cursor correctness ("only sync what changed") and type fidelity ("numbers stay numbers") are the two most README-obvious targets for any sync engine, so they would appear in any blind plan regardless. The honest resolution is not to drop them but to **credit them at a discount** and let this anchored note prove what was known when.

---

## 1. The public claims under test (quoted from the README)

The README makes these falsifiable promises. Each maps to an invariant below.

- **"Only sync what changed** — after the first run, the engine only picks up new and updated records."
- **"Never lose data** — if a sync is interrupted (network issue, server restart, anything), it picks up exactly where it left off. Failed records are saved for review, not silently dropped."
- **"Data arrives correctly** — field types, formats, and mappings are handled automatically. Your dates stay dates, your numbers stay numbers."
- Architecture: engine **"streams batches to the destination over gRPC"**; destination **"writes idempotently (database upsert, file manifest, API POST)"**; **"State is checkpointed so interrupted runs resume where they left off."**

## 2. Invariants

Target-specific (from the claims):

- **T1 — Incremental completeness & non-duplication ("only sync what changed").** After the first run, every new/updated source record is synced exactly once; no record is missed at the cursor boundary and none is re-emitted. A record whose cursor value equals the stored high-water mark must not be silently skipped on the next run.
- **T2 — Resume safety ("picks up exactly where it left off").** An interruption at any point resumes with no lost and no duplicated records. The checkpoint/high-water mark advances **only after** the corresponding data is durably committed at the destination — never before.
- **T3 — Failed-record capture ("saved for review, not silently dropped").** A record that fails to write is durably captured to the failed-records store; the run never reports success while losing it. The capture path's own failure is not swallowed.
- **T4 — Type fidelity ("dates stay dates, your numbers stay numbers").** Types survive extract→transform→load without silent coercion or truncation — in particular numeric precision (no `Decimal`→float/int narrowing) and datetime timezone-awareness.
- **T5 — Idempotent destination writes ("writes idempotently").** A retried or duplicated batch does not create duplicates (upsert / manifest / POST idempotency), including a batch replayed after a mid-batch interruption.
- **T6 — Config rejection (catalogue I7).** Invalid or contradictory pipeline/connector/stream configuration is rejected, not silently defaulted or partially applied.

Catalogue invariants engaged: **I5 safe boundary** (idempotent under retry; errors surface, never success-shaped) → T2/T3/T5; **I6 determinism** → T1; **I7 config rejection** → T6.

## 3. Detection method (kill matrix)

1. **Baseline.** Establish the target's own suite green as shipped (record any pre-existing failures; do not `--ignore`).
2. **Blind tests (`02-blind-tests/`).** Before inspecting the target's suite, author independent tests asserting T1–T6 against the real code. Any invariant the shipped code already violates is a **NATIVE** finding.
3. **Planted-defect matrix.** Plant each defect below one at a time, re-run **the target's OWN suite**, record **CAUGHT** (suite fails) or **ESCAPED** (suite still green). A build break is a planter error, not a result (per the runner rules). Kill count = caught / plantable.
4. **Refuter + buyer's check** on every candidate finding and on the repo before any publication.

## 4. Planted-defect set

### 4a. From the catalogue (that fit a sync engine)

| id | defect | invariant | how to plant | escape rate so far |
|---|---|---|---|---|
| F-RETRY-NOIDEMPOTENCY | retry resubmits a side-effecting destination write without an idempotency key | T5 | remove the idempotency key / upsert key on the retried write | 50% (2) |
| F-BOUNDARY-DOUBLE | last batch/page element processed twice | T1/T2 | append the last page to the loop list | 100% (1) |
| F-AUDIT-SILENT-LOSS | failed-write error swallowed with no log or counter | T3 | drop the error log/counter on the deferred/failed write | 100% (1) |
| F-EXCEPTION-SWALLOWED | failure swallowed into a success-shaped return | T3 | replace `raise` with `return None` in the write except block | 0% (3) |
| F-CONFIG-PARTIAL-ACCEPT | invalid config entry skipped with a warning; rest applied | T6 | replace the validation-error return with `continue` | 0% (2) |
| F-FABRICATED-DATA | missing source field silently replaced by a synthetic default | T4 | (usually native) test for it | 100% (1) |

### 4b. NOVEL — sync-engine-specific (≥4 required; 6 declared)

| id | defect | invariant | how to plant | blind? |
|---|---|---|---|---|
| N01 | cursor-boundary drop: incremental filter uses strict `>` against the stored high-water mark, so a record whose cursor value **equals** the mark is skipped on the next run | T1 | flip a `>=` to `>` (or drop tie-handling) on the incremental cursor comparison | **HINT-EXPOSED** (contamination §0) |
| N02 | checkpoint-before-durable-write: the resume checkpoint / high-water mark is advanced **before** the destination durably acks the batch | T2 | move the checkpoint-commit call above the destination-write/ack | blind |
| N03 | numeric narrowing: a `Decimal`/numeric field is coerced to `float`/`int` in transform, losing precision or truncating | T4 | insert an `int(...)`/`float(...)` narrowing in the type-mapping path | **HINT-EXPOSED** (contamination §0) |
| N04 | datetime tz-drop: an aware timestamp is coerced to naive (or shifted) in transform/cursor compare | T4 (and T1 drift) | strip `tzinfo` / apply a local-tz conversion in the datetime mapping | hint-adjacent (flagged) |
| N05 | failed-record safety-net fails silently: the failed-records **capture** write itself errors and is swallowed | T3 | make the capture-store write raise, swallow it in its except | blind |
| N06 | partial-batch ack: the destination acks a gRPC batch before all rows in it are durably written, so the checkpoint advances past unwritten rows | T2/T5 | ack/return success after a partial write of the batch | blind |

## 5. Disclosure plan

Private-first. Check for `SECURITY.md` / GitHub private advisory on the repo; if absent, contact the maintainer (org `analitiq-ai`, which also runs `analitiq-app.com` / `analitiq.ai`) directly and offer the private report before any public write-up. A data-loss or silent-corruption finding in a "never lose data" engine is a real-consequence finding: disclose privately, agree a timeline, publish only after a fix or the agreed window. If published, re-pin a fresh commit and state plainly this was a pre-registered blind engagement.

## 6. Environment

Python + Docker (single image, `RUN_MODE` toggles engine/destination; gRPC source→destination). Target's own test runner TBD from its packaging (pip/poetry/uv). Local host is Python 3.9 — run the suite in the target's own toolchain (Docker or a pinned venv), never the host interpreter. Blind tests run against the real code, no network to any live source/destination.

## 7. Timebox

One engagement session for baseline + blind tests + matrix; disclosure and any publication follow the runbook gates (refuter, buyer's check, publish-gate, disclosure-gate) in a separate, non-tired block.

---

**Pre-registration statement.** This plan was authored from public claims and metadata only, at the pin commit above, before reading any implementation file (subject to the contamination boundary in §0). Its SHA-256 is recorded in `../ANCHORS`, stamped to Bitcoin via OpenTimestamps, and posted as Issue #1 on the private engagement repo. The plan is frozen at hash time; later files are separate, ordered commits.
