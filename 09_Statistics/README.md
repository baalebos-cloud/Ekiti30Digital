# 09_Statistics — Ekiti State Knowledge Base

A sourced statistics package covering Ekiti State's population, poverty, labour-force, fiscal and literacy indicators from 1991 (last pre-statehood census) through 2026, following the same conventions established in 06_Education, 07_Health and 08_Agriculture.

## Contents
- `timeline/` — 12 dated entries (EK-STAT-001 to EK-STAT-012), each with sources.
- `institutions/` — 2 institution folders (Ekiti State Bureau of Statistics/StatCloud; National Population Commission state office), each with metadata.md, sources.md, permission.md.
- `datasets/` — 5 compiled indicator time-series write-ups (population/census, poverty/MPI, labour force, fiscal/IGR, literacy) — this sector's equivalent of the "programmes/" folder used elsewhere.
- `sector_snapshot.md` — one-page sourced overview.
- `kb_manifest_statistics_rows.csv` — 19 candidate/source registry rows, same column order as other sector manifests (doc_id, source_title, source_url, class, tier, last_verified, ingestible).
- `GAPS.md` — 11 open items, including two genuinely unresolved data disputes (current population figure; literacy rate).
- `INTEGRATION_NOTES.md` — merge checklist and cross-sector notes.

## Before merging
See INTEGRATION_NOTES.md and GAPS.md — ownership is unconfirmed and two headline figures (population, literacy) are presented as disputed rather than resolved. Please do not pick a winner between them without documenting why.
