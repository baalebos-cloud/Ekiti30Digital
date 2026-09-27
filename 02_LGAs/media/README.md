# Ekiti LGA Geography and Media Assets

This folder contains geographical and visual media records for the 16 Local Government Areas of Ekiti State.

The assets support the Explore Ekiti section of EKITI@30 DIGITAL.

## Folder Structure

Each LGA has its own folder:

- `ado-ekiti`
- `aiyekire`
- `efon`
- `ekiti-east`
- `ekiti-south-west`
- `ekiti-west`
- `emure`
- `ido-osi`
- `ijero`
- `ikere`
- `ikole`
- `ilejemeje`
- `irepodun-ifelodun`
- `ise-orun`
- `moba`
- `oye`

The central `lga_media_assets.csv` file records the metadata for every asset.

## Suitable Assets

Assets may include:

- LGA photographs
- Maps
- Landmarks
- Important locations
- Government buildings
- Educational institutions
- Tourism locations
- Administrative and geographical visuals
- Other useful location-based media

## Required Metadata

Every asset record must contain:

- Asset ID
- Asset title
- LGA
- Location
- Description
- Media type
- File name
- GitHub path
- Source name
- Source URL
- Creator or photographer
- Creation date, where available
- Date accessed
- Rights or permission information
- Licence
- Verification status
- Attribution requirement
- Attribution text
- Cloudinary public ID
- Cloudinary URL
- Limitations
- Owner

## Asset Identification

Use a unique asset ID for every record.

Examples:

- `EK30-LGA-ADO-001`
- `EK30-LGA-OYE-001`
- `EK30-LGA-IKL-001`

An asset ID must not be reused for another file.

## File Naming

Use lowercase descriptive file names with hyphens.

Examples:

- `ado-ekiti-fajuyi-park-01.jpg`
- `oye-ekiti-ekiti-state-polytechnic-01.jpg`
- `ikole-ekiti-landmark-01.jpg`

Do not use unclear names such as:

- `IMG001.jpg`
- `photo.jpg`
- `new-image.jpg`

## Source Requirements

The original page containing the asset should be recorded in `source_url`.

Do not use a Google Images search-result URL as the source.

Whenever possible, prefer:

- Official government websites
- Official institutional websites
- Wikimedia Commons files with clear licences
- Public-domain archives
- Photographs supplied directly by their creators
- Project photographs with documented permission

A social-media post may be recorded as a source, but it does not automatically grant permission to reuse the image.

## Rights and Permission

Do not assume that an image is free to use because it is available online.

Use a clear rights value such as:

- `Permission granted`
- `Permission required`
- `Creative Commons`
- `Public domain`
- `Official government media`
- `Unknown`

Assets with `Unknown` rights or requiring permission must not be uploaded to Cloudinary as approved website assets.

## Verification Status

- `Pending`: The asset has been identified but still requires checking.
- `Reviewed`: Its identity, location, description and source have been checked.
- `Verified`: It has passed independent review and is approved for publication.

Verification of an asset does not replace copyright or permission clearance.

## Attribution

If attribution is required, set `attribution_required` to `Yes` and record the exact credit in `attribution_text`.

Example:

`Photograph by Example Creator, licensed under CC BY 4.0.`

## GitHub Storage

GitHub should contain:

- Metadata
- Source references
- Small approved images where appropriate
- Optimized previews where needed

Do not upload unnecessarily large original photographs or videos.

## Cloudinary Storage

Only approved, website-ready assets should be uploaded to Cloudinary.

Use this folder pattern:

`EKITI30/LGAs/<LGA_NAME>/`

Example:

`EKITI30/LGAs/Ado-Ekiti/`

Use a traceable public ID such as:

`EKITI30/LGAs/Ado-Ekiti/ado-ekiti-fajuyi-park-01`

The Cloudinary public ID and delivery URL must be recorded in `lga_media_assets.csv`.

## Traceability

Every published asset should support this chain:

`Cloudinary asset → Asset ID → GitHub metadata → Original source`

Engineering should be able to identify the asset, its location, source, rights and attribution without guessing.

## Initial Target

The initial target is approximately two well-documented assets per LGA:

1. One general LGA or location photograph
2. One landmark, institution, map or important-place asset

Quality, source credibility and clear reuse rights are more important than quantity.

## Owner

Akintade Daniel Emmanuel  
Geospatial and LGA Lead

## Boundary Dataset and Reproducibility

The highlighted LGA maps use the following pinned geoBoundaries dataset:

- Boundary ID: `NGA-ADM2-59680162`
- Boundary type: `ADM2 — Local Government Areas`
- Year represented: `2022`
- Original source: `GRID3`
- geoBoundaries build date: `2023-12-12`
- Pinned repository commit: `9469f09`
- Licence: `CC BY 4.0`
- GeoJSON: https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/NGA/ADM2/geoBoundaries-NGA-ADM2.geojson

The script uses this pinned GeoJSON URL rather than the moving `current` API endpoint, ensuring that the maps remain reproducible.

## Aiyekire and Gbonyin Mapping

The pinned geoBoundaries dataset contains one source feature named `Gbonyin`, with shape ID `59680162B53652676960042`. It does not contain a separate feature named `Aiyekire`.

For this project, that single source boundary is displayed under the canonical current name `Aiyekire`. The script validates the exact source name and shape ID and does not combine or duplicate two geometries.

The validation requires exactly 16 unique Ekiti LGA features and 16 unique shape IDs before any map can be generated.

## Visual Map Review

On 24 September 2026, Akintade Daniel Emmanuel visually inspected all 16 generated LGA maps.

The review confirmed that:

- Each map has the correct LGA title.
- Each intended LGA is highlighted in dark green.
- The remaining LGAs are displayed in light green.
- No boundary is duplicated or accidentally substituted.
- All 16 generated PNG files are readable and correctly labelled.

This visual review confirms that the script selected and highlighted the intended source feature. It does not convert the third-party boundaries into official surveyed Ekiti State Government boundaries. The map assets therefore remain marked as `Pending` until independent geographic verification is completed.
