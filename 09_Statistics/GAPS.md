# Open Gaps — 09_Statistics package

Flagged rather than smoothed over, same policy as prior sector packages (Education, Agriculture, Health):

1. **Ownership unknown.** As with Agriculture and Health at first draft, I don't know who on the repo team owns Statistics the way Member 4 owns Education/Research. Needs assignment before merge (see INTEGRATION_NOTES.md).

2. **Current population figure not reconciled.** At least three different current/recent figures are in circulation and NOT reconciled in this package: the 2016 NPC/NBS projection (3,270,798), the state's own StatCloud portal figure (~3.2M), and the ~3.5M figure used in this repo's own 07_Health package (from a 2025 Nigeria Health Watch source). No authoritative current figure is asserted here — pick one deliberately if the platform needs a single number, and document which and why.

3. **Literacy rate genuinely disputed, not resolved.** 84% (SBS StatCloud) vs. 95.79% (Guardian Nigeria analysis of national data). Both are sourced and retained as-is (EK-STAT-011/012, EK-STAT-DATA-005). Whoever reviews this should either find the underlying methodology for each (adult vs. youth literacy; survey year; sampling) or explicitly present both with caveats on the live platform — don't silently pick one.

4. **No full 16-LGA breakdown table assembled.** Individual LGA population figures were found for a few LGAs (Ado-Ekiti, Ikere-Ekiti, Gbonyin) but a complete 16-LGA table (population, area, poverty, literacy) was not assembled — flagged as a natural follow-up task, likely obtainable directly from citypopulation.de or NPC/NBS state office records.

5. **No GDP/Gross State Product time series.** Statistics packages for other Nigerian states often include a GSP or gross domestic product estimate; no reliable Ekiti-specific GSP figure was located in the sources reviewed (national GDP growth figures were found but are not state-specific — see EK-STAT-DATA-002's national MPI-report citation of national GDP growth 2020-2021, which should NOT be read as an Ekiti-specific figure).

6. **SBS establishment date not verified.** The Ekiti State Bureau of Statistics almost certainly predates its 2025-era "StatCloud" digital rebrand, but no specific founding year/law was located — flagged at EK-STAT-006 and in institutions/sbs_statcloud/metadata.md.

7. **No vital-registration (births/deaths) completeness data.** Commonly part of a "statistics" sector but not covered here — not located in the sources reviewed.

8. **No migration statistics** (in- or out-migration, diaspora remittance data) — not covered.

9. **2023 general election voter-registration/turnout statistics** were not pursued for this package — arguably belongs in a Governance/History sector instead, but flagging the boundary decision here in case Statistics is expected to own it.

10. **NBS 2023 Labour Force Survey's Ekiti-specific tables (by sex, residence, education, age-group)** exist (Tables 67-70 of the national report) but were not individually transcribed into this package — only the single headline participation-rate figure was extracted. A follow-up pass could pull the full breakdown directly from the cited PDF.

11. **StatCloud's live interactive dashboards were not directly queried** — only its published summary figures (3.2M population, 84% literacy, 142 datasets) were captured. The portal may hold much more granular, authoritative data than what's reflected here.
