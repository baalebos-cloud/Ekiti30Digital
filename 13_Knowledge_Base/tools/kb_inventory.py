#!/usr/bin/env python3
"""
kb_inventory.py: classify every Markdown file under the KB topic folders,
per Issue #43 points 1-2 (inventory + genuine-KB-content vs support-file
classification).

This does NOT touch any file -- read-only, produces a CSV report so a human
decides what's genuinely intended as Ask Ekiti content before anyone adds
front matter to it.

Classification per file:
  - "kb_document"        : has front matter with an 'id' field -> already
                            a recognized KB document (kb_validate.py will
                            check it fully)
  - "malformed_frontmatter": has a '---' block but it doesn't parse cleanly
                            or has no 'id' -- needs a look before deciding
  - "candidate_kb_content": no front matter, but the filename/location
                            doesn't match the known support-file patterns
                            -- probably intended as KB content and needs
                            front matter added
  - "likely_support_file" : no front matter AND matches a known
                            non-content pattern (README, index, notes,
                            template, draft-note, etc.) -- probably NOT
                            meant to be ingested; confirm before touching

Usage:
    python 13_Knowledge_Base/tools/kb_inventory.py
    python 13_Knowledge_Base/tools/kb_inventory.py --selftest
"""
import argparse
import csv
import os
import re
import sys
import tempfile

TOPIC_DIRS = ["01_History", "02_LGAs", "03_Timeline", "04_Tourism", "05_Culture",
              "06_Education", "07_Health", "08_Agriculture", "09_Statistics"]

# Filename/path patterns that suggest "this file exists to support the repo
# or the team's workflow, not to be Ask Ekiti content" -- checked only when
# a file has NO front matter, never used to override a file that does.
SUPPORT_PATTERNS = [
    r"^readme\.md$", r"^index\.md$", r"^contributing\.md$", r"^code_of_conduct\.md$",
    r"^license\.md$", r"^_meta/", r"^_template", r"template\.md$",
    r"notes?\.md$", r"todo\.md$", r"draft-?notes?\.md$", r"gap[s-]?", r"outline\.md$",
    r"checklist\.md$", r"agenda\.md$", r"minutes?\.md$", r"scratch",
]
SUPPORT_RE = re.compile("|".join(SUPPORT_PATTERNS), re.IGNORECASE)


def has_front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None  # no front matter at all
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return "unclosed"
    fm_text = "\n".join(lines[1:end])
    has_id = bool(re.search(r"^id\s*:\s*\S", fm_text, re.M))
    return "ok_with_id" if has_id else "no_id"


def classify(rel_path, text):
    fm_state = has_front_matter(text)
    fname = os.path.basename(rel_path)
    if fm_state == "ok_with_id":
        return "kb_document"
    if fm_state in ("unclosed", "no_id"):
        return "malformed_frontmatter"
    # fm_state is None: no front matter block at all
    if SUPPORT_RE.search(fname) or SUPPORT_RE.search(rel_path):
        return "likely_support_file"
    return "candidate_kb_content"


def scan(root):
    rows = []
    for top in TOPIC_DIRS:
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn.sort()
            for name in sorted(fn):
                if not name.endswith(".md"):
                    continue
                full = os.path.join(dp, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                with open(full, encoding="utf-8", errors="replace") as f:
                    text = f.read()
                first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
                rows.append({
                    "path": rel,
                    "classification": classify(rel, text),
                    "size_bytes": len(text.encode("utf-8")),
                    "first_nonblank_line": first_line[:80],
                })
    return rows


def write_csv(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "classification", "size_bytes", "first_nonblank_line"])
        w.writeheader()
        w.writerows(rows)


def run(root, out_path, quiet=False):
    rows = scan(root)
    write_csv(rows, out_path)
    if not quiet:
        counts = {}
        for r in rows:
            counts[r["classification"]] = counts.get(r["classification"], 0) + 1
        print(f"Scanned {len(rows)} Markdown files under {', '.join(TOPIC_DIRS)}:")
        for k in ("kb_document", "candidate_kb_content", "likely_support_file", "malformed_frontmatter"):
            print(f"  {k}: {counts.get(k, 0)}")
        print(f"Wrote: {out_path}")
        print("\nNext step: have a human confirm the 'likely_support_file' guesses "
              "and 'malformed_frontmatter' entries before anyone adds front matter "
              "to 'candidate_kb_content' files.")
    return rows


def selftest():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "01_History"))
    open(os.path.join(tmp, "01_History", "with-fm.md"), "w", encoding="utf-8").write(
        "---\nid: history-x\ntitle: X\n---\n\n## Summary\nx\n")
    open(os.path.join(tmp, "01_History", "no-fm-content.md"), "w", encoding="utf-8").write(
        "# Some historical claim\nThis looks like real content with no front matter yet.\n")
    open(os.path.join(tmp, "01_History", "README.md"), "w", encoding="utf-8").write(
        "# Folder notes\nThis explains how this folder is organized.\n")
    open(os.path.join(tmp, "01_History", "bad-fm.md"), "w", encoding="utf-8").write(
        "---\ntitle: no id here\n---\n\ntext\n")
    open(os.path.join(tmp, "01_History", "unclosed.md"), "w", encoding="utf-8").write(
        "---\nid: x\ntitle: y\n\nno closing marker\n")
    rows = {r["path"].split("/")[-1]: r["classification"] for r in scan(tmp)}
    failures = []
    expect = {
        "with-fm.md": "kb_document",
        "no-fm-content.md": "candidate_kb_content",
        "README.md": "likely_support_file",
        "bad-fm.md": "malformed_frontmatter",
        "unclosed.md": "malformed_frontmatter",
    }
    for fname, want in expect.items():
        got = rows.get(fname)
        if got != want:
            failures.append(f"{fname}: expected {want}, got {got}")
    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASSED ({len(expect)} classification cases)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Inventory and classify KB Markdown files (Issue #43).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None, help="default: 13_Knowledge_Base/kb_inventory.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    out = a.out or os.path.join(a.root, "13_Knowledge_Base", "kb_inventory.csv")
    run(a.root, out)


if __name__ == "__main__":
    main()
