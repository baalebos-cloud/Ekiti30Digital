# KB Inventory & Classification (Issue #43, points 1-2)

Scanned 176 Markdown files under 01_History-09_Statistics on `main`.

| Classification | Count | Meaning |
|---|---|---|
| kb_document | 1 | Has front matter with an `id` field; already recognized by the validator (state-creation-1996.md) |
| candidate_kb_content | 90 | No front matter, doesn't match a known support-file pattern -- likely intended as KB content, needs front matter added |
| malformed_frontmatter | 74 | Has a `---` block, but no `id` field (or it's unclosed) -- needs inspection before deciding whether to fix in place or add proper front matter |
| likely_support_file | 11 | No front matter, matches README/GAPS/INTEGRATION_NOTES/index patterns -- likely NOT meant to be Ask Ekiti content |

## Findings requiring a decision

**Likely duplicate files** (identical byte size, same folder, one with a `(1)` suffix -- probably an accidental double upload):
- `01_History/EKITI30_History_Storytelling_Draft_v2.md` and `... (1).md`
- `03_Timeline/README_Timeline_Data_Dictionary.md` and `... (1).md`

**Possibly empty/stub files** (very small size, worth confirming they have real content):
- `09_Statistics/datasets/EK-STAT-DATA-001.md` through `EK-STAT-DATA-005.md` (80 bytes each)
- `09_Statistics/institutions/npc_state_office/permission.md` (87 bytes)
- `09_Statistics/institutions/sbs_statcloud/sources.md` (149 bytes)

**candidate_kb_content by folder** (where front matter needs to be added):
| Folder | Count |
|---|---|
| 07_Health | 52 |
| 06_Education | 19 |
| 09_Statistics | 9 |
| 08_Agriculture | 6 |
| 01_History | 2 |
| 03_Timeline | 2 |

**malformed_frontmatter by folder** (has SOME front matter, missing `id`):
| Folder | Count |
|---|---|
| 09_Statistics | 20 |
| 06_Education | 14 |
| 04_Tourism | 13 |
| 08_Agriculture | 13 |
| 05_Culture | 12 |
| 01_History | 2 |

**likely_support_file** (pattern-matched guess -- needs human confirmation per Faith's request, not auto-excluded):
- `02_LGAs/README.md`
- `02_LGAs/media/README.md`
- `07_Health/GAPS.md`
- `07_Health/INTEGRATION_NOTES.md`
- `07_Health/README.md`
- `08_Agriculture/INTEGRATION_NOTES.md`
- `09_Statistics/GAPS.md`
- `09_Statistics/INTEGRATION_NOTES.md`
- `09_Statistics/README.md`
- `09_Statistics/institutions/npc_state_office/index.md`
- `09_Statistics/institutions/sbs_statcloud/index.md`

## Full inventory

See attached `kb_inventory.csv` for the complete file-by-file list.
