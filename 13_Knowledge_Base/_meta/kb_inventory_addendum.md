# Addendum: what "malformed_frontmatter" actually contains

Sampled 3 files across the largest clusters. Finding: **this is not a simple missing-field fix.** At least two content teams built their own complete, internally-consistent front-matter schemas independently of the KB spec, before or without seeing it. Migrating these needs a real per-schema mapping decision, not a bulk find-and-replace.

## Schema A -- 09_Statistics (`sector_snapshot.md`, likely all 20 in this folder)

Uses `doc_id` instead of `id`, no `category`/`doc_type`/`status`/`source_tier`/`source_ids` at all. The body is a narrative "package overview" mixing many distinct facts in prose, not the spec's one-fact-per-bullet-with-[S#] format. It explicitly defers per-fact citations to *other* files ("See individual timeline, institution and dataset files for full citations").

**This surfaces a real risk:** those other files include `09_Statistics/datasets/EK-STAT-DATA-001.md` through `-005.md`, which the earlier inventory flagged as only 80 bytes each. If the snapshot's promised "full source trails" live there, those files may be stubs that were never finished -- worth checking before assuming the citations exist somewhere.

**Also surfaces two new, real, previously untracked conflicts**, stated openly in the document itself:
- **Literacy rate**: 84% (state's own StatCloud portal) vs. 95.79% (national media analysis) -- the document says it "deliberately does not pick a winner."
- **Population post-2006**: no verified figure exists past the 2006 census; the 2016 NPC/NBS projection (3,270,798), the state's own current estimate (~3.2M), and a ~3.5M figure used in the Health package don't reconcile with each other.

These should be added to the Source Inventory's tracked-conflicts list alongside the existing 2006-population and early-administrator conflicts, for the Verification Lead.

## Schema B -- 04_Tourism (`abanijorin-rocks-cave.md`, likely most/all of the 13 in this folder)

A different, more elaborate schema: `title`, `category`, `subcategory`, `lga`, `location`, `source`/`source_url`/`source_type` (singular, not a `source_ids` list), `verification_status` (not `status`), `media_reference`, `media_rights`, `traditional_account`, `notes`. Body sections: "Documented Facts", "Verification Breakdown", "Notes / Uncertainties", "Media / Photo Reference", "Sources".

Content quality here looks genuinely careful -- it flags that the government tourism portal was offline during research and explicitly withholds upgrading the entry's status until re-checked. This is good-faith, cautious work; it just predates or wasn't matched to the spec's format.

## What this means for the migration task

Faith's original framing ("classify, then add front matter") undersells the work in at least these two folders: each needs a **mapping decision** (which of their fields maps to which spec field, and what to do with fields the spec has no equivalent for, like `media_rights` or the narrative conflict discussion) before a human or script can convert them. Recommend treating 09_Statistics and 04_Tourism as two separate migration sub-tasks with their own owners, rather than one bulk "add front matter" pass.

**Not yet sampled**: 06_Education (19 candidate + 14 malformed), 08_Agriculture (6 + 13), 05_Culture (12 malformed). These may be a third schema, or match one of the two above -- worth sampling one file from each before assuming.
