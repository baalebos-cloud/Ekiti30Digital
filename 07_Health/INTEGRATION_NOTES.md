# Integration Notes — Health Content

Built to match the conventions established in `06_Education/` and `08_Agriculture/` (following the PR #11/PR #20 KB ingestion schema).

## 1. Ownership & Folder Numbering (Resolved)
- **Sector Owner, Reviewer & Yoruba Lead:** Member 1 (Technical Lead) took explicit ownership of `07_Health`, serving as sector owner, technical reviewer, and Yoruba localization reviewer.
- **Folder Path:** `07_Health` is confirmed as the correct path in the repository tree.
- **Reviewer Chain:** Technical, content, and Yoruba review handled by Member 1 (Technical Lead), with final verification sign-off with Member 8 (Verification Lead).

## 2. Ingestible Status (`ingestible: no`)
- **Yoruba review pending:** Formal Yoruba localization and review pass by Member 1 is pending before marking rows as ingestible for live deployment.
- **Tier assignments (A/B/C/D):** C-tier entries (e.g., specific facility counts, target projections) require second-reviewer sign-off before upgrade to VERIFIED. All 55 data rows in `kb_manifest_health_rows.csv` strictly enforce `ingestible=no` until these sign-offs are completed.

## 3. Package Meta-File ID Scheme
Package-level overview and methodology documents use reserved `EK-HEA-000` prefix IDs to maintain full schema validation across all manifest rows:
- `README.md` -> `EK-HEA-000` (Section Overview)
- `INTEGRATION_NOTES.md` -> `EK-HEA-000-INT` (Integration Notes)
- `GAPS.md` -> `EK-HEA-000-GAP` (Gaps and Follow-ups)
- `docs/RESEARCH_METHOD.md` -> `EK-HEA-000-RES` (Research Methodology)

## 4. Disputed Figures & Open Items
- **EK-HLT-008**: Divergent figures regarding exact functional Primary Healthcare Centres across the 16 LGAs (103 vs 148 fully operational baseline).
- **EK-HLT-012**: EKSUTH resident doctor allowance and residency training funding implementation timeline discrepancies across administration transitions.

## 5. What's Ready to Build On
- 17 timeline entries (`EK-HEA-TL-001` to `017`), each single-fact, each sourced, and cross-referenced to institutional and programme files.
- 10 institution markdown profiles (Ministry of Health, EKSUTH, FMC Ido-Ekiti, FMC Ikole-Ekiti, EKPHCDA, etc.).
- 14 programme write-ups (Ulerawa, BHCPF, Free Health Missions, MNCH, IMPACT PHC, Digital Health).
- 7 current project records (EKSUTH 80-bed facility, Ikogosi/Awo/Ipao hospital upgrades, PHC revitalizations).
- Sector snapshots and facility landscape data files (`EK-HEA-HEALTH-FACILITY-LANDSCAPE.md`, 2024 State of Health, 2026 Budget & Current System).
- A `kb_manifest_health_rows.csv` fragment containing exactly 55 document records (excluding header), verified to parse cleanly.
- `GAPS.md` listing open evidence items and data discrepancies.

## 6. Mechanics
- **Branch:** `smartexploit/health-content`
- **Pull Request:** PR #34 opened under `07_Health`.
- All updates staged cleanly in modular commits without overwriting existing root repository structures.
