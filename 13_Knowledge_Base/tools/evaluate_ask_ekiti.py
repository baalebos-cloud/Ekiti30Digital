#!/usr/bin/env python3
"""Record real API responses or explicit blocked cases; never infer behaviour passes."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import openpyxl

INSUFFICIENT = "The available verified knowledge isn't enough to answer that yet."


def cases(path):
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        result = []
        for row in book['Eval Set'].iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            ident = str(row[0])
            yoruba = ident in {'E-016', 'E-017', 'E-018', 'E-019'}
            question = '' if ident == 'E-049' else row[3] if yoruba else row[2]
            if not isinstance(question, str) or not row[9] or not row[10]:
                raise ValueError(f'{ident}: missing question, expected answer or evidence')
            result.append({'id': ident, 'type': row[1],
                'request': {'question': question, 'language': 'yo' if yoruba else 'en'},
                'expected_behaviour': row[4], 'pass_criteria': row[6],
                'expected_answer': row[9], 'evidence': row[10]})
        if len(result) != 50 or len({r['id'] for r in result}) != 50:
            raise ValueError('Expected 50 unique evaluation IDs')
        return result
    finally:
        book.close()


def request_api(url, payload):
    req = Request(url, data=json.dumps(payload).encode('utf-8'),
                  headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=30) as response:
            status, raw = response.status, response.read().decode('utf-8')
    except HTTPError as exc:
        status, raw = exc.code, exc.read().decode('utf-8', errors='replace')
    try:
        body = json.loads(raw)
    except ValueError:
        body = {'non_json_body': raw}
    return status, body


def evaluate(items, url=None, blocked_reason=None, transport=request_api):
    results = []
    for case in items:
        row = dict(case, http_status=None, actual_response=None,
                   expected_answer_matches=None, behaviour_review='pending')
        if blocked_reason:
            row.update(outcome='blocked', reason=blocked_reason)
        else:
            try:
                status, body = transport(url, case['request'])
                match = (status == 200 and isinstance(body, dict)
                         and body.get('answer') == case['expected_answer'])
                if case['expected_answer'] == INSUFFICIENT and match:
                    match = body.get('answer_status') == 'insufficient' and body.get('citations') == []
                row.update(http_status=status, actual_response=body,
                    expected_answer_matches=match,
                    outcome='expectation_match' if match else 'expectation_mismatch')
            except (URLError, TimeoutError, OSError) as exc:
                row.update(outcome='transport_error', reason=str(exc))
        results.append(row)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', type=Path, default=Path('14_Source_Documents/Ask_Ekiti_Eval_Set.xlsx'))
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--api-url', help='Full POST endpoint URL, without credentials or tokens')
    target.add_argument('--blocked-reason')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = evaluate(cases(args.workbook), args.api_url, args.blocked_reason)
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
        'api_url': args.api_url, 'workbook_sha256': hashlib.sha256(args.workbook.read_bytes()).hexdigest(),
        'interpretation': 'Exact current-answer matches are not behavioural passes or proof of grounded retrieval. Review citations, language, UI, and multi-turn behaviour separately.',
        'summary': dict(Counter(r['outcome'] for r in results)), 'results': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary']))


if __name__ == '__main__':
    main()
