import unittest
from urllib.error import URLError
from evaluate_ask_ekiti import evaluate, INSUFFICIENT


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.case = {'id': 'example', 'request': {'question': 'Question?', 'language': 'en'},
                     'expected_answer': INSUFFICIENT}

    def test_blocked_never_calls_transport(self):
        def fail(*args):
            self.fail('Blocked evaluation made a request')
        result = evaluate([self.case], blocked_reason='No endpoint', transport=fail)[0]
        self.assertEqual(result['outcome'], 'blocked')
        self.assertIsNone(result['expected_answer_matches'])

    def test_abstention_requires_no_citations(self):
        for citations, expected in [([], True), ([{'doc_id': 'draft'}], False)]:
            response = {'answer': INSUFFICIENT, 'answer_status': 'insufficient', 'citations': citations}
            result = evaluate([self.case], 'unused', transport=lambda *a: (200, response))[0]
            self.assertEqual(result['expected_answer_matches'], expected)
            self.assertEqual(result['behaviour_review'], 'pending')

    def test_http_errors_and_non_object_are_not_passes(self):
        for status, body in [(422, {'detail': 'invalid'}), (503, {}), (200, [])]:
            result = evaluate([self.case], 'unused', transport=lambda *a: (status, body))[0]
            self.assertEqual(result['outcome'], 'expectation_mismatch')
            self.assertEqual(result['http_status'], status)

    def test_transport_failure_remains_unknown(self):
        def fail(*args):
            raise URLError('offline')
        result = evaluate([self.case], 'unused', transport=fail)[0]
        self.assertEqual(result['outcome'], 'transport_error')
        self.assertIsNone(result['expected_answer_matches'])


if __name__ == '__main__':
    unittest.main()
