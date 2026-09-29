# Ekiti State LGAs Geographic Dataset

This folder contains the initial geographic dataset for the 16 Local Government Areas of Ekiti State.

## Purpose

The dataset supports the Explore Ekiti map and other geographic features of EKITI@30 DIGITAL.

## Available Formats

- `ekiti_lgas.csv` — primary editable dataset
- `ekiti_lgas.json` — structured application data
- `ekiti_lgas.geojson` — map-ready point features

All three formats must contain the same 16 LGA records and remain synchronized after every correction.

## Data Included

Each LGA record contains:

- LGA name
- Headquarters
- Approximate headquarters coordinates
- Major towns and communities
- Notable places
- Important institutions
- Source information
- Source date and last-checked date
- Verification status
- Limitations
- Contributor

## Coordinate Standard

Coordinates use decimal degrees in the WGS84 coordinate system.

The coordinates are approximate town-centre reference points for the respective LGA headquarters. They are not official LGA boundaries, surveyed administrative coordinates, or precise locations of government secretariats.

The point coordinates are suitable for the initial Explore Ekiti map, but they must remain marked as approximate until independently checked against reliable geographic or official records.

## Source Structure

Each source is connected directly to its corresponding source type and URL.

In the CSV file, sources use numbered fields:

- `source_1_name`, `source_1_type`, `source_1_link`
- `source_2_name`, `source_2_type`, `source_2_link`
- `source_3_name`, `source_3_type`, `source_3_link`

The same number identifies one complete source record. For example, `source_1_name` corresponds directly to `source_1_type` and `source_1_link`.

In the JSON and GeoJSON files, source information is stored as a `sources` array. Each source object contains:

- `name`
- `type`
- `link`

This structure prevents ambiguity between a source and the URL supporting it.

## Source Policy

Government publications and official institutional websites are preferred for LGA names, headquarters, institutions, and administrative information.

Secondary geographic databases may support coordinate research, but they must not be treated as the sole authoritative source for administrative facts.

A general reference may only be recorded as a secondary supporting source. It must not serve as the sole basis for marking a record as verified.

Conflicting information must be documented in the `limitations` field instead of being silently resolved.

## Canonical LGA Naming

The dataset uses the current Ekiti State Government naming consistently.

- `Aiyekire` is used as the canonical LGA name. `Gbonyin` may appear in older or alternative references.
- `Ido/Osi` is used consistently instead of the `Ido-Osi` variation.

Alternative names should be documented as context and must not be mixed with the canonical names across the data formats.

## Institutional Entries

Important institutions are recorded under the LGA where their host community is located.

Current institutional additions include:

- Federal University of Technology and Environmental Sciences (FUTES), Iyin-Ekiti, under Irepodun/Ifelodun LGA
- Ekiti State Polytechnic, Isan-Ekiti, under Oye LGA

The inclusion of an institution does not mean its precise campus coordinates or full operational details have been independently verified.

## Verification Status

- `Pending`: Information has been collected but has not completed the required checks.
- `Reviewed`: The information and cited sources have been checked by a contributor or reviewer, but final independent approval is still required.
- `Verified`: The record has passed the project's required independent review and has been approved for publication as verified project knowledge.

A record must not move directly from `Pending` to `Verified` without the required independent review.

## Unresolved Information

Fields marked `To be researched` are intentionally unresolved. They must remain that way until reliable supporting information is found.

Contributors must not fill unresolved fields using assumptions or unsupported claims.

## Limitations

Some coordinates, communities, institutions, landmarks, and administrative details remain provisional.

All records currently marked `Pending` require further review before publication as verified information.

## Source of Truth

As of the admin content editor (see PR for feature/admin-content-editing), the live database is the source of truth for day-to-day corrections. The CSV remains the source of truth for bulk research updates and verification_status changes, and re-importing it will overwrite any live-only edits to other fields on the rows it touches (see the --force behavior in scripts/ingest_lgas.py / ingest_timeline.py).

## Contributor

Akintade Daniel Emmanuel  
Geospatial and LGA Lead  
Issue #5
