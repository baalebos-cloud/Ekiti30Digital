# Integration Notes — Agriculture Content

Built to match the conventions established in `06_Education/` (which itself matched
Member 4's own merged PR #29 pattern and the PR #11/PR #20 KB ingestion schema). It
is **not** auto-merge-ready.

## 1. Ownership & Folder Numbering (Resolved)
- **Sector Owner, Reviewer & Yoruba Lead:** Member 1 (Technical Lead) took explicit ownership of `08_Agriculture`, serving as sector owner, technical reviewer, and Yoruba localization reviewer.
- **Folder Path:** `08_Agriculture` is confirmed as the correct path alongside `07_Health` in the repository tree.
- **Reviewer Chain:** Technical, content, and Yoruba review handled by Member 1 (Technical Lead), with final verification sign-off with Member 8 (Verification Lead).

## 2. Everything here is `ingestible: no`
Same two blockers as Education:
- **Yoruba review pending.** Formal Yoruba localization and review pass by Member 1 is pending before marking rows as ingestible for live deployment.
- **Tier assignments (A/B/C/D) are a first-pass proposal**, following the same
  pattern as Education's tiers but not read from the merged spec. The C-tier
  entries lean on single sources or self-reported corporate/government figures
  (Ikun Dairy Farm's current scale, the CBN-ABP jobs target, YCAD's founding) and
  deserve the most scrutiny before any upgrade to VERIFIED.

## 3. Genuinely disputed, not just under-sourced
Two items are live disagreements between sources, not just gaps:
- **EK-AGR-007**: Ikun Dairy Farm's 2019 initial cattle count (227 vs. 400) —
  two different government-adjacent sources give different numbers.
- **EK-AGR-009 / institutions/agro-allied-cargo-airport/**: a December 2025
  Tribune opinion piece directly disputes whether the airport actually functions
  as "agro-allied" (no warehouse/cold-storage/quarantine facilities observed
  despite 20+ landings), against the government's own framing of the airport as
  its flagship agriculture-export project. This is the closest analogue to
  Education's EK-EDU-011 (the Africa Check dispute) — it contradicts an
  administration's own stated narrative and requires verification sign-off before ingestion.

## 4. What's genuinely ready to build on
- 17 timeline entries (EK-AGR-001 to 017), each single-fact, each sourced, each
  cross-referenced to an institution or programme file.
- 3 institution folders (Ekiti ADP, Ikun Dairy Farm, Agro-Allied Cargo Airport)
  each with `metadata.md` / `sources.md` / `permission.md`.
- 6 programme write-ups (cocoa revival, YCAD, CBN Anchor Borrowers rice, the
  tractorisation subsidy, L-PRES livestock, the poultry/broiler scheme) — a
  structure added because Agriculture's 30-year history is dominated by schemes and PPPs rather than standalone institutions.
- One sector-snapshot data file, explicitly flagged as a loose collection of
  sourced figures, not a systematic dataset (unlike Education's single-document
  Annual School Census summary — no equivalent official agriculture census was
  found this pass).
- A `kb_manifest_agriculture_rows.csv` fragment in the same column order as
  Education's (`doc_id, source_title, source_url, class, tier, last_verified,
  ingestible`), 30 rows, verified to parse cleanly.
- An `Agriculture_Gaps_and_Follow-ups.md` listing 11 concrete open items.

## 5. Mechanics
- **Branch:** `smartexploit/agriculture-content`
- **Pull Request:** PR #31 opened under `08_Agriculture`.
- All updates staged cleanly in modular commits without overwriting existing root repository structures.
