import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from evals.agents.runner import HERE, episode, run, score, validate_response


class AgentEvalsTest(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((HERE / 'orchestrator.json').read_text())
        self.config = json.loads((HERE / 'offline.json').read_text())

    def case(self, name):
        return next(c for c in self.cases if c['id'] == name)

    def test_calibration_all_cases_and_unknown_telemetry(self):
        result = run(self.config, self.cases)
        good, bad = result['comparison']
        self.assertEqual(good['pass_rate'], 1)
        self.assertEqual(bad['pass_rate'], 0)
        self.assertGreater(bad['contract_violations'], 0)
        self.assertIsNone(good['cost_usd'])
        self.assertFalse(result['live_multi_agent'])
        self.assertTrue(all(r['telemetry'][0]['usage'] is None for r in result['results']))

    def test_partial_credit_does_not_hide_hard_violation(self):
        c = self.case('steering')
        trace = [copy.deepcopy(t['good']) for t in c['turns']]
        trace[0].append({'kind': 'publish'})
        result = score(c, trace)
        self.assertEqual(result['quality'], 1)
        self.assertFalse(result['passed'])
        self.assertEqual(result['contract_violations'][0]['rule'], 'authority_boundary')

    def test_stale_check_after_edit_and_wrong_revision(self):
        c = self.case('stale_verification')
        trace = [c['turns'][0]['good'], c['turns'][1]['bad']]
        self.assertIn('unverified_or_stale_acceptance', [v['rule'] for v in score(c, trace)['contract_violations']])
        trace[1] = [{'kind': 'verify', 'state': 'S1'}, {'kind': 'accept', 'state': 'S2'}]
        self.assertFalse(score(c, trace)['passed'])

    def test_overlap_release_and_incomplete_packet(self):
        c = self.case('ownership')
        self.assertTrue(score(c, [t['good'] for t in c['turns']])['passed'])
        r = score(c, [t['bad'] for t in c['turns']])
        self.assertIn('overlapping_writers', [v['rule'] for v in r['contract_violations']])
        r = score(c, [[{'kind': 'assign', 'worker': 'x', 'files': ['x']}], []])
        self.assertIn('incomplete_packet', [v['rule'] for v in r['contract_violations']])

    def test_missing_turn_not_full_credit_and_extra_fields_ignored(self):
        c = self.case('failure')
        self.assertLess(score(c, [c['turns'][0]['good']])['quality'], 1)
        trace = [t['good'] for t in c['turns']]
        trace = copy.deepcopy(trace)
        trace[0][0]['explanation'] = 'Different wording must not affect score'
        self.assertTrue(score(c, trace)['passed'])

    def test_unknown_actions_fail_and_invalid_cost_rejected(self):
        self.assertFalse(score(self.case('direct'), [[{'kind': 'invented'}]])['passed'])
        for value in (-1, float('nan'), True):
            with self.assertRaises(ValueError):
                validate_response({'actions': [], 'cost_usd': value})

    def test_limits_before_execution(self):
        for update in ({'max_runs': 1}, {'repetitions': 0}, {'cases': ['missing']}):
            with self.assertRaises(ValueError):
                run({**self.config, **update}, self.cases)
        p = {'id': 'x', 'backend': 'command', 'command': ['does-not-exist']}
        cfg = {**self.config, 'profiles': [p], 'cases': ['direct']}
        with self.assertRaises(ValueError):
            run(cfg, self.cases)
        with self.assertRaises(ValueError):
            run(cfg, self.cases, True)
        with self.assertRaises(ValueError):
            run({**cfg, 'max_external_calls': 1}, self.cases, True)

    def test_adapter_protocol_hides_rubric_and_preserves_workers(self):
        # Test subprocess boundary without a provider, credentials, or network.
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'adapter.py'
            p.write_text('''import json,sys
r=json.load(sys.stdin)
assert 'required' not in r and 'good' not in r and 'bad' not in r
assert r['contracts'] and r['profile']['reasoning']=='medium'
assert r['observation']=='Task is one spelling fix. No workers needed.'
print(json.dumps({'actions':[{'kind':'direct','file':'README.md'}],
 'usage':{'input_tokens':10,'output_tokens':5}, 'cost_usd':0.001,
 'resolved_settings':{'model':'fake'}}))
''')
            cfg = {**self.config, 'profiles': [{'id': 'adapter', 'backend': 'command',
                    'command': [sys.executable, str(p)], 'model': 'fake', 'reasoning': 'medium'}],
                   'cases': ['direct'], 'max_external_calls': 1,
                   'max_cost_usd': 0.01, 'per_call_cost_ceiling_usd': 0.01}
            r = run(cfg, self.cases, True)
            self.assertTrue(r['results'][0]['passed'])
            self.assertEqual(r['comparison'][0]['cost_usd'], 0.001)
            self.assertEqual(r['results'][0]['telemetry'][0]['usage']['input_tokens'], 10)

    def test_adapter_error_and_timeout_are_failures(self):
        for script in ('raise SystemExit(1)', 'import time; time.sleep(1)', 'print("not json")'):
            r = episode(self.case('direct'), {'backend': 'command',
                        'command': [sys.executable, '-c', script]}, 0.05, {})
            self.assertFalse(r['passed'])
            self.assertEqual(r['error'], 'adapter_error_or_timeout')
