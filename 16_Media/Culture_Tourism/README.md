# 16_Media/Culture_Tourism — Member 7

One folder per canonical Culture/Tourism content entry, named with the exact
same slug as its matching file in 04_Tourism/, 05_Culture/, or 01_History/ —
this guarantees a 1:1 alignment between content and media, with no separate
numbering scheme to keep in sync by hand.

Every entry also carries a stable **Asset ID** (CT-001, CT-002, ...) in its
`metadata.md`, `sources.md`, and `permission.md` — use this ID when
referencing an entry in chat, a spreadsheet, or WhatsApp. The Asset ID is a
label, never a folder name: the folder itself is always the slug, so
re-numbering IDs later never breaks the link between content and media. See
`ASSET_INDEX.md` (human-readable table) or `ASSET_INDEX.csv` (for
spreadsheets) for the full ID-to-entry lookup.

Each entry folder contains:
- `media/` — the actual image/video files go here (currently empty placeholders)
- `metadata.md` — submission record, split into Site information source
  (where the facts about the place/festival come from) and Image source /
  Photographer (kept separate and marked TBD until a real photo is sourced)
- `sources.md` — the specific source(s) behind the site information, plus a
  short reliability note
- `permission.md` — licensing/usage-rights log; nothing here is publishable
  until this is filled in

`_pending_new_entries/` holds two real, verified sites that are NOT yet part
of the 27-entry canonical inventory (Itapaji Water Dam, Oore Monumental
Palace), carrying CT-PENDING-01/02 IDs instead of the main CT-0XX sequence.
They need a matching content entry added to 04_Tourism/ or 05_Culture/
before being promoted into the main numbering.

Every entry's `File name` field is `TBD` until an actual photo exists —
never a placeholder filename implying a file that isn't there yet.

Standard: Context + Source + Verification + Permission + Quality > Quantity
