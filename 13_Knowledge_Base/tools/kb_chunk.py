#!/usr/bin/env python3
"""
kb_chunk.py: split verified, ingestible KB documents into retrievable chunks.

Reads 13_Knowledge_Base/kb_manifest.csv (from kb_validate.py) and, for every
row with ingestible == "yes", reads the document, pulls the Facts and Summary
sections, and writes one chunk per fact (plus one summary chunk) with the
source metadata a retriever and Ask Ekiti need at answer time.

Chunking rule (spec A9.3, "cite every factual claim"): one fact = one chunk,
so a retrieved chunk never mixes two claims under one citation.

Citation rule (v2, fixes a v1 bug flagged in review): a fact's own [S1] /
[S1, S2] marker decides which sources that specific chunk cites. The v1
version discarded the marker and attached every document-level source_id to
every chunk, which meant a fact backed by only S1 could be shown as if S2
also supported it. v2 resolves each marker against the document's own
"## Sources" list (lines like "- [S1] SRC-001: title...") and only falls
back to the full document-level source list if a fact has no marker at all
(flagged as a warning, since spec A3 expects every fact to be traceable).

Output: 13_Knowledge_Base/kb_chunks.jsonl (one JSON object per line) and
kb_chunks.csv (same data, for spreadsheet review). Deliberately no vector
store or embedding call here: this only depends on kb_manifest.csv and the
verified documents, so it can run before the embeddings/pgvector decision is
made. Embedding is a separate step that reads this file's "text" field.

Usage:
    python 13_Knowledge_Base/tools/kb_chunk.py
    python 13_Knowledge_Base/tools/kb_chunk.py --selftest
"""
import argparse
import csv
import json
import os
import re
import sys
import tempfile

CHUNK_FIELDS = ["chunk_id", "doc_id", "chunk_type", "text", "source_ids", "source_titles",
                "category", "doc_type", "tier", "language", "last_verified", "path", "seq"]

SOURCE_LINE_RE = re.compile(r"^-\s*\[(S\d+)\]\s*(.+)$")
INLINE_MARKER_RE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]\s*$")


def read_manifest(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_body_sections(text):
    """Return (summary_text, [fact_lines], sources_map) from a document body.

    sources_map: {"S1": "SRC-001: title, publisher, URL, date"} parsed from
    the document's own "## Sources" list, keyed by the local marker used in
    the Facts section (not the global SRC-### id, since one document can
    reuse S1 for a source that appears earlier in its own list).
    """
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            lines = lines[end + 1:]
    sections, current = {}, None
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(ln)
    summary = " ".join(x.strip() for x in sections.get("Summary", []) if x.strip())
    facts = []
    for ln in sections.get("Facts", []):
        ln = ln.strip()
        if ln.startswith("- "):
            facts.append(ln[2:].strip())
    sources_map = {}
    for ln in sections.get("Sources", []):
        m = SOURCE_LINE_RE.match(ln.strip())
        if m:
            sources_map[m.group(1)] = m.group(2).strip()
    return summary, facts, sources_map


def split_fact_and_markers(fact_line):
    """Return (claim_text, [local_markers]) e.g. 'X happened. [S1, S2]' ->
    ('X happened.', ['S1', 'S2'])."""
    m = INLINE_MARKER_RE.search(fact_line)
    if not m:
        return fact_line.strip(), []
    markers = [x.strip() for x in m.group(1).split(",")]
    claim = fact_line[:m.start()].strip()
    return claim, markers


def extract_src_id(source_text):
    m = re.match(r"^(SRC-\d{3})", source_text.strip())
    return m.group(1) if m else ""


def title_from_source_text(source_text):
    # "SRC-001: Title of the source. Publisher. URL. Published date."
    rest = re.sub(r"^SRC-\d{3}:\s*", "", source_text.strip())
    return rest.split(".")[0].strip()


def make_id(doc_id, seq):
    return f"{doc_id}#{seq:03d}"


def resolve_sources(markers, sources_map, doc_level_source_ids, doc_level_title):
    """Turn local markers (['S1']) into (source_ids, source_titles) for one
    chunk. Falls back to the document-level source list only when the fact
    has no marker at all -- this keeps the fallback visible as a warning
    upstream rather than silently attaching every source to every fact."""
    if not markers:
        return list(doc_level_source_ids), doc_level_title, False
    sids, titles = [], []
    for m in markers:
        src_text = sources_map.get(m)
        if not src_text:
            continue
        sid = extract_src_id(src_text)
        if sid:
            sids.append(sid)
            titles.append(title_from_source_text(src_text))
    if not sids:  # markers present but none resolved against the Sources list
        return list(doc_level_source_ids), doc_level_title, False
    return sids, "; ".join(titles), True


def build_chunks(manifest_rows, root):
    chunks, skipped, errors, warnings = [], [], [], []
    for row in manifest_rows:
        if row.get("ingestible") != "yes":
            skipped.append((row.get("path", ""), row.get("reason", "not ingestible")))
            continue
        # Defensive check, independent of kb_validate.py: never chunk a
        # document whose status isn't literally "verified", even if
        # ingestible was somehow set to "yes" by a manifest bug or a hand
        # edit. This is the last line of defense before unverified content
        # could reach retrieval (spec A9.1).
        if row.get("status") != "verified":
            errors.append(f"{row['path']}: marked ingestible=yes but status is "
                           f"'{row.get('status')}', not 'verified' -- refusing to chunk "
                           f"(check kb_manifest.csv for a bug)")
            continue
        full = os.path.join(root, row["path"])
        if not os.path.exists(full):
            errors.append(f"{row['path']}: file listed in manifest but not found on disk")
            continue
        with open(full, encoding="utf-8") as f:
            text = f.read()
        summary, facts, sources_map = parse_body_sections(text)
        doc_sids = [s for s in (row.get("source_ids") or "").split(";") if s]
        doc_title = row.get("id", "")
        meta = dict(doc_id=row["id"], category=row.get("category", ""),
                    doc_type=row.get("doc_type", ""), tier=row.get("source_tier", ""),
                    language=row.get("language", "en"), last_verified=row.get("last_verified", ""),
                    path=row["path"])
        seq = 0
        if summary:
            seq += 1
            chunks.append(dict(chunk_id=make_id(row["id"], seq), chunk_type="summary",
                                text=summary, seq=seq, source_ids=";".join(doc_sids),
                                source_titles="", **meta))
        if not facts:
            errors.append(f"{row['path']}: verified and ingestible but has no '## Facts' bullet lines")
        for fact in facts:
            claim, markers = split_fact_and_markers(fact)
            if not claim:
                continue
            sids, titles, resolved = resolve_sources(markers, sources_map, doc_sids, doc_title)
            if not markers:
                warnings.append(f"{row['path']}: fact has no [S#] marker, "
                                 f"attached all document sources: {claim[:60]!r}")
            elif not resolved:
                warnings.append(f"{row['path']}: marker {markers} did not match the "
                                 f"document's Sources list: {claim[:60]!r}")
            seq += 1
            chunks.append(dict(chunk_id=make_id(row["id"], seq), chunk_type="fact",
                                text=claim, seq=seq, source_ids=";".join(sids),
                                source_titles=titles, **meta))
        if seq == 0:
            errors.append(f"{row['path']}: produced zero chunks (empty Summary and Facts)")
    return chunks, skipped, errors, warnings


def write_outputs(chunks, jsonl_path, csv_path):
    os.makedirs(os.path.dirname(os.path.abspath(jsonl_path)), exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({k: c.get(k, "") for k in CHUNK_FIELDS}, ensure_ascii=False) + "\n")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHUNK_FIELDS)
        w.writeheader()
        for c in chunks:
            w.writerow({k: c.get(k, "") for k in CHUNK_FIELDS})


def run(root, manifest_path, jsonl_path, csv_path, quiet=False):
    rows = read_manifest(manifest_path)
    chunks, skipped, errors, warnings = build_chunks(rows, root)
    write_outputs(chunks, jsonl_path, csv_path)
    if not quiet:
        for path, reason in skipped:
            print(f"SKIP    {path}: {reason}")
        for w in warnings:
            print(f"WARNING {w}")
        for e in errors:
            print(f"ERROR   {e}")
        by_doc = len({c["doc_id"] for c in chunks})
        print(f"\nChunks written: {len(chunks)} from {by_doc} document(s) "
              f"| skipped: {len(skipped)} | warnings: {len(warnings)} | errors: {len(errors)}")
        print(f"Wrote: {jsonl_path}\nWrote: {csv_path}")
    return chunks, skipped, errors, warnings


def selftest():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "01_History"))
    doc = """---
id: history-example
---

## Summary
Example state was formed on a date, according to one source.

## Facts
- Fact one happened on 1 October. [S1]
- Fact two also happened, per two sources. [S1, S2]
- Fact three has no marker at all.

## Sources
- [S1] SRC-001: First Source Title. Publisher One. https://a.example. Published 2021.
- [S2] SRC-002: Second Source Title. Publisher Two. https://b.example. Published 2022.
"""
    open(os.path.join(tmp, "01_History", "example.md"), "w", encoding="utf-8").write(doc)
    doc2 = """---
id: history-empty
---

## Summary


## Facts

## Sources
"""
    open(os.path.join(tmp, "01_History", "empty.md"), "w", encoding="utf-8").write(doc2)
    manifest = os.path.join(tmp, "kb_manifest.csv")
    with open(manifest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "path", "category", "doc_type", "status", "source_tier", "source_ids",
                    "publication_date", "last_verified", "verified_by", "language",
                    "translation_of", "period_covered", "file_sha256", "ingestible", "reason"])
        w.writerow(["history-example", "01_History/example.md", "history", "event", "verified", "A",
                    "SRC-001;SRC-002", "2021-10-01", "2026-09-21", "Victor", "en", "", "1996", "x",
                    "yes", ""])
        w.writerow(["history-draft", "01_History/example.md", "history", "event", "draft", "A",
                    "SRC-001", "2021-10-01", "", "", "en", "", "1996", "x", "no", "status is draft"])
        w.writerow(["history-empty", "01_History/empty.md", "history", "event", "verified", "A",
                    "SRC-001", "2021-10-01", "2026-09-21", "Victor", "en", "", "1996", "x", "yes", ""])
        w.writerow(["history-missing", "01_History/missing.md", "history", "event", "verified", "A",
                    "SRC-001", "2021-10-01", "2026-09-21", "Victor", "en", "", "1996", "x", "yes", ""])
        w.writerow(["history-forged", "01_History/example.md", "history", "event", "needs_review", "A",
                    "SRC-001", "2021-10-01", "", "", "en", "", "1996", "x", "yes",
                    "manifest bug: ingestible=yes but status is not verified"])
    chunks, skipped, errors, warnings = run(tmp, manifest, os.path.join(tmp, "c.jsonl"),
                                             os.path.join(tmp, "c.csv"), quiet=True)
    failures = []
    ex = [c for c in chunks if c["doc_id"] == "history-example"]
    if len(ex) != 4:
        failures.append(f"expected 4 chunks (1 summary + 3 facts), got {len(ex)}")
    fact1 = next((c for c in ex if c["text"].startswith("Fact one")), None)
    fact2 = next((c for c in ex if c["text"].startswith("Fact two")), None)
    fact3 = next((c for c in ex if c["text"].startswith("Fact three")), None)
    if not fact1 or fact1["source_ids"] != "SRC-001":
        failures.append(f"Fact one should cite only SRC-001, got {fact1 and fact1['source_ids']}")
    if not fact1 or fact1["source_titles"] != "First Source Title":
        failures.append(f"Fact one source_titles should resolve to 'First Source Title', "
                         f"got {fact1 and fact1['source_titles']!r}")
    if not fact2 or fact2["source_ids"] != "SRC-001;SRC-002":
        failures.append(f"Fact two should cite both sources, got {fact2 and fact2['source_ids']}")
    if not fact3 or fact3["source_ids"] != "SRC-001;SRC-002":
        failures.append("Fact three (no marker) should fall back to the full document source list")
    if not any("no [S#] marker" in w for w in warnings):
        failures.append("a fact with no marker should raise a warning")
    if any("[S1]" in c["text"] or "[S1, S2]" in c["text"] for c in ex):
        failures.append("citation markers should be stripped from chunk text")
    if len(skipped) != 1 or skipped[0][0] != "01_History/example.md":
        failures.append(f"expected history-draft to be skipped as not ingestible, got: {skipped}")
    if not any("no '## Facts'" in e for e in errors):
        failures.append("empty document should raise a 'no Facts' error")
    if not any("not found on disk" in e for e in errors):
        failures.append("missing file should raise a 'not found' error")
    if not any("refusing to chunk" in e for e in errors):
        failures.append("a row marked ingestible=yes with a non-verified status must be refused")
    if any(c["doc_id"] == "history-forged" for c in chunks):
        failures.append("the forged (non-verified) row must never produce chunks")
    ids = [c["chunk_id"] for c in ex]
    if len(set(ids)) != len(ids):
        failures.append("chunk_ids should be unique")
    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASSED ({len(ex)} chunks, per-fact citation resolution, "
          f"{len(skipped)} skipped, {len(errors)} expected errors, {len(warnings)} expected warnings)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Chunk verified, ingestible Ask Ekiti KB documents.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--manifest", default=None, help="default: 13_Knowledge_Base/kb_manifest.csv")
    ap.add_argument("--out-jsonl", default=None, help="default: 13_Knowledge_Base/kb_chunks.jsonl")
    ap.add_argument("--out-csv", default=None, help="default: 13_Knowledge_Base/kb_chunks.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    manifest = a.manifest or os.path.join(a.root, "13_Knowledge_Base", "kb_manifest.csv")
    jsonl = a.out_jsonl or os.path.join(a.root, "13_Knowledge_Base", "kb_chunks.jsonl")
    csv_out = a.out_csv or os.path.join(a.root, "13_Knowledge_Base", "kb_chunks.csv")
    if not os.path.exists(manifest):
        sys.exit(f"manifest not found: {manifest} (run kb_validate.py first)")
    _, _, errors, _ = run(a.root, manifest, jsonl, csv_out)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
