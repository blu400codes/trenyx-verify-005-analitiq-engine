# trenyx-verify-005 — analitiq-engine (pre-registered blind engagement)

Independent adversarial verification of `analitiq-ai/analitiq-engine` @
`1eac312d733b6db7f3e60fd47bae67016d74985e` (Apache-2.0, AI-built data sync engine).

**Pre-registered blind.** The attack plan in `00-preregistration/ATTACK-PLAN.md` was
written from the public README + metadata only, hashed, and anchored to two independent
clocks BEFORE any implementation file was read:
- **Bitcoin** via OpenTimestamps (`00-preregistration/ATTACK-PLAN.md.ots`)
- **GitHub Issue #1** server timestamp (link in `ANCHORS`)

Verify end to end: `shasum -a 256 00-preregistration/ATTACK-PLAN.md` must equal
`plan_sha256` in `ANCHORS`; `ots verify 00-preregistration/ATTACK-PLAN.md.ots`.

A contamination boundary (a narrow inadvertent exposure during the authorship check) is
disclosed in §0 of the plan — on purpose, inside the anchored document.

Status: PRE-REGISTERED. Baseline, blind tests, planted-defect matrix, and findings follow
as separate, ordered commits. Repo is PRIVATE until the publish-gate clears it.
