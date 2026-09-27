# EKITI@30 Historical Timeline Media: Tracker and Process

**Tracker file:** `EKITI30_Historical_Media_Tracker_UPDATED.csv`\
**Project:** EKITI@30 DIGITAL --- Our Story. Our People. Our Future.\
**Team role:** Member 4 --- Research & History / Historical Timeline
Media

## Purpose

This folder tracks candidate photographs, portraits, maps, documents,
scans, institutional images and other historical media connected to the
EKITI@30 timeline.

The tracker currently contains **51 candidate asset rows** covering **50
timeline event IDs**. Finding an image online does **not** mean that the
image has been approved for publication. Each candidate must still be
checked for provenance, creator/photographer information, copyright or
permission, attribution requirements and historical relevance.

## Tracker Columns

The CSV uses the following fields:

`asset_id`, `related_timeline_id`, `asset_title`, `event_year`,
`description`, `category`, `location`, `source`, `source_url`,
`asset_url`, `creator_photographer`, `copyright_permission_status`,
`attribution_required`, `verification_status`, `suggested_filename`,
`cloudinary_public_id`, `cloudinary_url`, `notes_limitations`,
`submitted_by`, `date_submitted`.

### URL fields

-   **`source_url`** --- the webpage, article, institutional page,
    social-media post or other provenance page that explains where the
    candidate came from.
-   **`asset_url`** --- the direct image/file URL when available. A
    CDN/JPG/PNG URL belongs here rather than being treated as provenance
    by itself.
-   **`cloudinary_url`** --- the final hosted copy after an asset has
    been reviewed, approved and uploaded to Cloudinary.

A direct image URL alone is not sufficient evidence of ownership,
creator identity or permission to republish.

## Verification Status

Use the following statuses consistently:

-   **Not yet sourced** --- no suitable candidate source has been
    established.
-   **Needs verification** --- a candidate/source has been located, but
    one or more checks remain.
-   **Verified** --- the image, provenance and relevant
    rights/permission information have been checked sufficiently for the
    project workflow.
-   **Community contribution** --- media supplied by a community member
    and requiring the appropriate contribution/permission record.

At the time this README was generated, the tracker contains **0
`Verified` rows**, **38 rows marked `Needs verification`**, and **13
rows still marked `Not yet sourced`**.

## Verification Workflow

For every candidate asset:

1.  Open the `source_url` and confirm that the source page is genuine
    and relevant to the timeline event.
2.  Confirm that the proposed image is actually present on, or traceable
    from, that source.
3.  Check the event/person/place represented by the image. Do not rely
    on facial recognition to identify real people; use captions,
    documentary evidence and source descriptions.
4.  Identify the creator or photographer where possible.
5.  Check copyright, licence or explicit reuse permission. An image
    being publicly visible online does not automatically make it
    reusable.
6.  Record whether attribution is required and the form that attribution
    should take.
7.  Update `copyright_permission_status`, `creator_photographer`,
    `verification_status` and `notes_limitations`.
8.  Give the approved asset a clear `suggested_filename`.
9.  Upload only an approved asset to the designated Cloudinary location
    and record its `cloudinary_public_id` and `cloudinary_url`.

## Source Guidance

### Official and institutional sources

Government, university, palace, museum and other institutional pages are
useful provenance sources, but publication on an official website does
not automatically establish unrestricted reuse rights. Check the site's
terms or obtain permission where necessary.

### News and commercial publications

Images from newspapers, broadcasters, news sites, travel sites and
commercial publications should normally be treated as copyrighted unless
a licence or permission says otherwise. Record the photographer/agency
credit when provided.

### Facebook, TikTok, X and other social media

Use the **specific original post** as `source_url` whenever possible
rather than a profile page or CDN image. A Facebook `scontent` URL,
Google-hosted image, X image CDN or YouTube thumbnail may be stored as
`asset_url`, but the original post/page should still be located for
provenance.

Social-media publication does not establish permission for EKITI@30 to
republish the underlying photograph.

### Wikimedia/Wikipedia

Do not rely only on a Wikipedia thumbnail URL. Open the corresponding
Wikimedia Commons or file-description page and check the licence for
that specific file. Record the creator, licence and required
attribution.

## Current Source Work

The updated tracker incorporates candidate links supplied during Member
4's historical-media research, including government/institutional
sources, news publications, Facebook posts, TikTok, Wikimedia/Wikipedia,
ResearchGate, university sources and direct image links.

Where only a direct image/CDN URL was supplied, it is recorded as
`asset_url` and the row remains **Needs verification** until a parent
source page, creator and reuse status can be established.

The previous CARA candidate for **EK-048** has been replaced by the
subsequently supplied Facebook-hosted image candidate. Because the
replacement is currently a direct Facebook CDN URL, its original
post/page and creator still need to be established.

## Historical Integrity

Do not:

-   use random Google Images results as final sources;
-   remove watermarks or ownership marks;
-   present an unverified photograph as documentary fact;
-   assume that "available online" means "free to use";
-   use AI-generated imagery as if it were an authentic historical
    photograph.

If an AI-generated reconstruction or illustration is ever used, label it
clearly as:

**Illustration / Reconstruction --- not a historical photograph.**

## Cloudinary

Approved media should be uploaded under:

`EKITI30/Historical/Timeline/`

Use meaningful public IDs based on the event and subject. Cloudinary
upload is a hosting step only; **uploading an image does not make it
verified or approved**.

Recommended sequence:

`Candidate found → provenance checked → historical context checked → creator/rights checked → permission/licence recorded → verified/approved → renamed → Cloudinary upload → URL recorded`

## GitHub

The CSV and this README belong in:

`16_Media/Historical/`

Do not commit unnecessary large or high-resolution media files directly
to GitHub. Keep the tracker as the index to sources and approved hosted
assets.

Suggested files:

``` text
16_Media/
└── Historical/
    ├── README.md
    └── EKITI30_Historical_Media_Tracker_UPDATED.csv
```

## Quality Standard

For EKITI@30 historical media, **context + source + verification +
permission + quality** are more important than the number of images
collected.

A candidate is not complete merely because an image has been found. The
goal is a traceable, historically responsible and publication-ready
media archive.
