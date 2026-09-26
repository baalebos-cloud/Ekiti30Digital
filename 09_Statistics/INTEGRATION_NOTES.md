# Integration Notes — 09_Statistics package

**Structural note (read this first):** Statistics is a data-centric sector, not an institutions-and-programmes narrative like Agriculture or Health. I kept the same top-level conventions (timeline/, institutions/, a manifest CSV, this Gaps/Integration pairing) but replaced the "programmes/" folder used in Agriculture/Health with a "datasets/" folder — each file is a compiled indicator time series with its own EK-STAT-DATA-0XX id, rather than a policy-programme write-up. If the repo has since standardized on a different convention for this sector, rename the folder rather than restructure the content — the doc_id scheme (EK-STAT-*) is what matters for cross-referencing.

**Cross-references to existing sectors:** This package deliberately does NOT duplicate population/poverty/literacy figures already used in 06_Education, 07_Health or 08_Agriculture — it instead documents the primary sourcing behind those figures and flags where they don't cleanly reconcile (see Gaps #2 and #3). If those other packages are updated to match a single authoritative figure decided here, this package's doc_ids (EK-STAT-001, EK-STAT-004, EK-STAT-011/012) are the right citation anchors.

**Same checklist as prior packages before this goes into a PR:**
1. Confirm this repo's actual current top-level folder name/number for Statistics (this package assumes `09_Statistics`, per the live repo tree at time of research — please confirm it hasn't been renumbered since).
2. Assign an owner/reviewer and update this file plus GAPS.md to name them.
3. Note the mapping Issue number, if one exists.
4. Same merge process as documented for 08_Agriculture: pull latest, diff the existing folder against this package before touching anything, resolve any doc_id / EK-STAT-0XX collisions by renumbering to continue after the existing highest ID, and append (never overwrite) into any existing root `kb_manifest.csv`.
