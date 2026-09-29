#!/usr/bin/env python3
"""Build a review queue from existing metadata and links, without approving data."""
import argparse
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import re
import subprocess

from kb_inventory import scan
from kb_validate import load_registry, run


def urls(text):
    return sorted({u.rstrip(').,;') for u in re.findall(r'https?://[^\s<>"\]]+', text)})


def build(root, today):
    registry = load_registry(str(root / '14_Source_Documents/Ask_Ekiti_Source_Inventory.xlsx'))
    documents, rows, errors, warnings = run(str(root),
        str(root / '14_Source_Documents/Ask_Ekiti_Source_Inventory.xlsx'),
        str(root / '13_Knowledge_Base/kb_manifest.csv'), False, False, today, quiet=True)
    parsed = {d['path']: d for d in documents}
    candidates, links, counts = [], defaultdict(set), Counter()
    for entry in scan(str(root)):
        path = entry['path']
        text = (root / path).read_text(encoding='utf-8')
        doc = parsed.get(path)
        fm = doc['fm'] if doc else {}
        kind = entry['classification']
        counts[kind] += 1
        label = re.search(r'^verification_status:\s*(.+)$', text, re.M)
        source_ids = fm.get('source_ids', [])
        source_ids = source_ids if isinstance(source_ids, list) else []
        reference_files = [path]
        # Institution packages keep source lists alongside their metadata.
        sibling = Path(path).with_name('sources.md')
        if Path(path).name == 'metadata.md' and (root / sibling).exists():
            reference_files.append(sibling.as_posix())
        found = set()
        for ref in reference_files:
            found.update(urls((root / ref).read_text(encoding='utf-8')))
        if kind != 'likely_support_file':
            for url in found:
                links[url].add(path)
        blockers = list(doc['errors']) if doc else ['Convert missing or unsupported front matter; preserve original research.']
        if kind == 'likely_support_file':
            blockers = ['Supporting material; do not convert into answer facts automatically.']
        else:
            if fm.get('status') != 'verified':
                blockers.append('KB document approval is not recorded.')
            if not re.search(r'^## Facts\s*$', text, re.M):
                blockers.append('Per-fact citation structure needs review; do not assign paragraph sources by guesswork.')
            for sid in source_ids:
                if registry.get(sid, {}).get('status') != 'Verified':
                    blockers.append(sid + ': source approval is not recorded as Verified.')
        candidates.append({
            'path': path, 'classification': kind, 'id': fm.get('id'),
            'legacy_doc_id': fm.get('doc_id'), 'kb_status': fm.get('status'),
            'author_verification_label': fm.get('verification_status') or (label[1] if label else None),
            'metadata_errors': doc['errors'] if doc else [],
            'metadata_warnings': doc['warnings'] if doc else [],
            'source_ids': source_ids, 'source_reference_files': reference_files,
            'candidate_source_urls': sorted(found), 'remaining_actions': blockers,
        })
    by_url = defaultdict(list)
    for sid, record in registry.items():
        if record['location']:
            by_url[record['location']].append(sid)
    source_queue = [{'url': u, 'referencing_documents': sorted(paths),
                     'exact_registry_matches': by_url.get(u, []),
                     'action': 'Review existing source approval' if u in by_url else
                     'Check source relevance, existing aliases, and register if appropriate'}
                    for u, paths in sorted(links.items())]
    try:
        base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        base = None
    return {
        'audit_date': today.isoformat(), 'working_tree_base': base,
        'scope': 'Working tree; links are extracted candidates, not verified evidence or new source IDs.',
        'summary': {'parsed_documents': len(documents), 'metadata_errors': errors,
                    'metadata_warnings': warnings, 'inventory_counts': dict(counts),
                    'verified_documents': sum(r['status'] == 'verified' for r in rows),
                    'ingestible_documents': sum(r['ingestible'] == 'yes' for r in rows),
                    'source_records': len(registry),
                    'source_status_counts': dict(Counter(r['status'] for r in registry.values())),
                    'unique_candidate_urls': len(source_queue),
                    'urls_without_exact_registry_match': sum(not s['exact_registry_matches'] for s in source_queue)},
        'documents': candidates, 'source_registration_queue': source_queue,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, default=Path('13_Knowledge_Base/readiness_report.json'))
    parser.add_argument('--today', type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    report = build(args.root, args.today)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], indent=2))
