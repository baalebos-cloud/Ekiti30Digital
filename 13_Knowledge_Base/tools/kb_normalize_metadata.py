#!/usr/bin/env python3
"""Align safe metadata fields without changing bodies or approving research.

Only parseable legacy front matter is changed. Existing canonical IDs are
untouched. Missing evidence, dates, document types and ambiguous tiers stay
missing for explicit review. Dry-run by default; --apply writes the changes.
"""
import argparse
import json
import re
from pathlib import Path

from kb_inventory import classify
from kb_validate import CATEGORY_FOLDERS, TIERS, collect_docs, parse_front_matter


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize(path, text):
    fm, _, error = parse_front_matter(text)
    if error or fm.get("id") or classify(path, text) == "likely_support_file":
        return text, {}
    fields = {}
    legacy_id = fm.get("doc_id")
    fields["id"] = slug(str(legacy_id)) if legacy_id else slug(str(Path(path).with_suffix("")))
    if not fm.get("title") and fm.get("source_title"):
        fields["title"] = str(fm["source_title"])
    # A new KB workflow state is not a replacement for the author's research
    # verification_status, which remains in the file exactly as supplied.
    if not fm.get("status"):
        fields["status"] = "needs_review"
    if not fm.get("source_tier") and fm.get("tier") in TIERS:
        fields["source_tier"] = fm["tier"]
    category = fm.get("category")
    replacement = None
    if category not in CATEGORY_FOLDERS:
        inferred = next((cat for cat, dirs in CATEGORY_FOLDERS.items()
                         if path.split('/')[0] in dirs and cat != "government"), None)
        if inferred:
            if category:
                if "research_category" in fm:
                    return text, {}  # avoid overwriting existing author metadata
                fields["research_category"] = category
                replacement = inferred
            fields["category"] = inferred
    lines = text.splitlines(keepends=True)
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    newline = "\r\n" if lines[0].endswith("\r\n") else "\n"
    if replacement:
        for i in range(1, end):
            if lines[i].startswith("category:"):
                lines[i] = "category: " + replacement + newline
    additions = [key + ": " + (str(value) if key in {"id", "status", "category", "source_tier"}
                               else json.dumps(value, ensure_ascii=False)) + newline
                 for key, value in fields.items() if key != "category" or not replacement]
    lines[end:end] = additions
    return "".join(lines), fields


def run(root, apply=False):
    docs, _ = collect_docs(str(root))
    ids = {str(d["fm"]["id"]) for d in docs if d["fm"].get("id")}
    changes = []
    # Validate the complete plan before writing, including new ID collisions.
    for doc in docs:
        file = root / doc["path"]
        old = file.read_bytes().decode("utf-8")
        new, fields = normalize(doc["path"], old)
        if not fields:
            continue
        if not fields["id"] or fields["id"] in ids:
            raise ValueError("duplicate or empty planned ID: " + fields["id"])
        ids.add(fields["id"])
        changes.append((file, new, {"path": doc["path"], "fields": fields}))
    if apply:
        for file, text, _ in changes:
            file.write_bytes(text.encode("utf-8"))
    return [item for _, _, item in changes]


def selftest():
    original = '---\ndoc_id: EK-EDU-1\nclass: education\ntier: B\nverification_status: Verified\n---\n# Body\nUnchanged claim.\n'
    new, changes = normalize('06_Education/institutions/a/metadata.md', original)
    assert changes['id'] == 'ek-edu-1'
    assert changes['status'] == 'needs_review'
    assert new.split('---', 2)[2] == original.split('---', 2)[2]
    assert 'verification_status: Verified' in new
    assert normalize('06_Education/institutions/a/metadata.md', new)[0] == new
    assert normalize('06_Education/Education_Gaps_and_Follow-ups.md', original)[0] == original
    ambiguous = original.replace('tier: B', 'tier: A/B')
    assert 'source_tier' not in normalize('06_Education/a.md', ambiguous)[1]
    print('SELFTEST PASSED (metadata preservation, approval, idempotency, support, ambiguous tier)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        print(json.dumps(run(args.root, args.apply), ensure_ascii=False, indent=2))
