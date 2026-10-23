import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from evals.agents.runner import HERE, ROOT, episode, run, score, validate_response


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
        trace = [copy.deepcopy(t['good']) for t in c['turns']]
        trace[-1] = [a for a in trace[-1] if a['kind'] != 'verify']
        trace[-1][-1]['state'] = 'S1'
        self.assertIn('unverified_or_stale_acceptance', [v['rule'] for v in score(c, trace)['contract_violations']])
        trace[-1] = copy.deepcopy(c['turns'][-1]['good'])
        trace[-1][-1]['state'] = 'S3'
        self.assertFalse(score(c, trace)['passed'])

    def test_one_active_worker_including_readonly_verifiers(self):
        c = self.case('delegation')
        self.assertTrue(score(c, [t['good'] for t in c['turns']])['passed'])
        r = score(c, [t['bad'] for t in c['turns']])
        self.assertIn('worker_limit', [v['rule'] for v in r['contract_violations']])
        trace = [copy.deepcopy(t['good']) for t in c['turns']]
        trace[1] = trace[1][1:]  # Verifier dispatched before implementer releases.
        self.assertIn('worker_limit', [v['rule'] for v in score(c, trace)['contract_violations']])
        r = score(c, [[{'kind': 'assign', 'worker': 'x', 'files': ['x']}], []])
        self.assertIn('incomplete_packet', [v['rule'] for v in r['contract_violations']])

    def good_trace(self, case):
        return [copy.deepcopy(t['good']) for t in case['turns']]

    def rules(self, case, trace):
        return {v['rule'] for v in score(case, trace)['contract_violations']}

    def test_authority_fields_and_exact_file_scope(self):
        c = self.case('steering')
        trace = self.good_trace(c)
        trace[-1].append({'kind': 'journal', 'owner': 'worker'})
        self.assertIn('authority_boundary', self.rules(c, trace))
        c = self.case('direct')
        for filename in ('billing.py', '.env', '.env.local', 'nested/.env.example', '../README.md', '/tmp/README.md'):
            with self.subTest(filename=filename):
                trace = self.good_trace(c)
                trace[0].append({'kind': 'direct', 'file': filename})
                self.assertFalse(score(c, trace)['passed'])
        c = self.case('ownership')
        trace = self.good_trace(c)
        trace[0][-1]['files'] = ['schema.json']
        self.assertIn('write_scope', self.rules(c, trace))

    def test_worker_cannot_write_another_workers_allowed_file(self):
        c = self.case('delegation')
        trace = self.good_trace(c)
        trace[0].append({'kind': 'edit', 'worker': 'a', 'file': 'b.py', 'state': 'S0'})
        for actions in trace:
            validate_response({'actions': actions})
        self.assertIn('write_scope', self.rules(c, trace))

    def test_post_accept_edit_invalidates_terminal_state_and_telemetry(self):
        c = self.case('steering')
        trace = self.good_trace(c)
        packet = copy.deepcopy(self.case('delegation')['turns'][0]['good'][-1])
        packet.update(worker='after', files=['ui.py'])
        trace[-1].extend([packet, {'kind': 'edit', 'worker': 'after', 'file': 'ui.py', 'state': 'S4'},
                          {'kind': 'release', 'worker': 'after'}])
        for actions in trace:
            validate_response({'actions': actions})
        rules = self.rules(c, trace)
        self.assertIn('unverified_final_state', rules)
        self.assertIn('stale_final_telemetry', rules)

    def test_optional_logger_fields_match_real_logger(self):
        c = self.case('steering')
        invalid = [{'conversation_id': ' padded '}, {'references_prior_sessions': [{}]},
                   {'timestamp': '2026-10-23T00:00:00'}, {'timestamp': 'invalid'}]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            config = directory / 'config.json'
            config.write_text(json.dumps({'project': 'synthetic', 'session_persistence_dir': 'journal',
                                         'audit_output_dir': 'reports', 'max_age_days': 30, 'minimum_sessions': 2}))
            for update in invalid:
                with self.subTest(update=update):
                    trace = self.good_trace(c)
                    record = next(a['record'] for a in trace[-1] if a['kind'] == 'journal')
                    record.update(update)
                    self.assertIn('invalid_journal_record', self.rules(c, trace))
                    path = directory / 'record.json'
                    path.write_text(json.dumps(record))
                    result = subprocess.run([sys.executable, str(ROOT / 'harness/audit.py'),
                                             '--config', str(config), 'log', '--record', str(path)],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)

    def test_role_packets_include_checks_and_reframing_evidence(self):
        c = self.case('failure')
        trace = self.good_trace(c)
        del trace[2][-1]['questions']
        self.assertIn('missing_or_repeated_reframing', self.rules(c, trace))
        trace = self.good_trace(c)
        del trace[-2][-1]['checks']
        self.assertIn('missing_verification_commands', self.rules(c, trace))

    def test_executive_never_reads_or_implements_code(self):
        c = self.case('executive')
        for kind in ('direct', 'read_code', 'read_diff', 'raw_log'):
            with self.subTest(kind=kind):
                trace = self.good_trace(c)
                trace[0].append({'kind': kind, 'file': 'app.py'})
                self.assertIn('executive_code_access', self.rules(c, trace))

    def test_same_instance_socratic_threshold_and_final_attempt_budget(self):
        c = self.case('failure')
        trace = self.good_trace(c)
        trace[1][-1]['worker'] = 'replacement'
        self.assertIn('correction_budget_or_identity', self.rules(c, trace))
        trace = self.good_trace(c)
        trace[2] = [trace[2][0], {'kind': 'correct', 'worker': 'w'}]
        self.assertIn('correction_without_diagnosis', self.rules(c, trace))
        trace = self.good_trace(c)
        trace[-1].append({'kind': 'correct', 'worker': 'w'})
        self.assertIn('correction_budget_or_identity', self.rules(c, trace))
        trace = self.good_trace(c)
        trace[2][1]['questions'] = ['One unsupported guess?']
        self.assertIn('invalid_reframing', self.rules(c, trace))

    def test_uncertain_first_failure_requires_early_investigation(self):
        c = copy.deepcopy(self.case('failure'))
        c['turns'][1]['event']['uncertain'] = True
        self.assertIn('correction_without_diagnosis', self.rules(c, self.good_trace(c)))
        # Valid early escalation uses one final directed correction, not two retries.
        original = copy.deepcopy(c['turns'])
        c['turns'] = [original[0], original[1], original[3], original[4], original[5]]
        c['turns'][1]['good'] = original[2]['good']
        c['turns'][1]['required'] = copy.deepcopy(original[2]['required'])
        c['turns'][-1]['good'][-1]['metric'] = c['turns'][-1]['good'][-1]['metric'].replace('cycles=2', 'cycles=1')
        self.assertTrue(score(c, self.good_trace(c))['passed'])

    def test_patch_before_restore_and_cleanup_before_pivot(self):
        c = self.case('cleanup')
        for removed_kind, rule in [('save_patch', 'cleanup_without_preservation'),
                                   ('restore', 'unverified_cleanup'),
                                   ('cleanup_result', 'unsafe_pivot')]:
            with self.subTest(removed_kind=removed_kind):
                trace = self.good_trace(c)
                trace[-1] = [a for a in trace[-1] if a['kind'] != removed_kind]
                self.assertIn(rule, self.rules(c, trace))
        for kind in ('reset', 'stash', 'clean'):
            trace = self.good_trace(c)
            trace[-1].insert(2, {'kind': kind})
            self.assertIn('authority_boundary', self.rules(c, trace))
        trace = self.good_trace(c)
        trace[-1].insert(4, {'kind': 'remove', 'files': ['parser.py'], 'baseline_preserved': True})
        self.assertIn('remove_preexisting_file', self.rules(c, trace))
        trace = self.good_trace(c)
        trace[-1][1]['reasoning'] = 'medium'
        self.assertIn('unsupported_routing', self.rules(c, trace))

    def test_receipt_bounds_required_coverage_and_test_counts(self):
        c = self.case('steering')
        for replacement in ([], ['track=T1'] * 6):
            trace = self.good_trace(c)
            trace[-1][0]['receipt'] = replacement
            self.assertIn('invalid_independent_receipt', self.rules(c, trace))
        trace = self.good_trace(c)
        trace[-1][0]['receipt'][2] = 'tests=pass:unit/exit=0/count=0'
        self.assertIn('invalid_independent_receipt', self.rules(c, trace))
        c = copy.deepcopy(c)
        c['required_checks'] = ['tests', 'user_flows']
        self.assertIn('invalid_independent_receipt', self.rules(c, self.good_trace(c)))

    def test_telemetry_matches_instances_cycles_and_logger_schema(self):
        c = self.case('failure')
        self.assertTrue(score(c, self.good_trace(c))['passed'])
        for old, new in [('Impl(Sol-Med):1', 'Impl(Sol-Med):3'), ('cycles=2', 'cycles=3'),
                         ('reframed=true', 'reframed=false'), ('outcome=verified', 'outcome=blocked-reverted')]:
            trace = self.good_trace(c)
            trace[-1][-1]['metric'] = trace[-1][-1]['metric'].replace(old, new)
            self.assertIn('invalid_telemetry', self.rules(c, trace))
        c = self.case('steering')
        trace = self.good_trace(c)
        record = next(a['record'] for a in trace[-1] if a['kind'] == 'journal')
        record['workflow_insights'] = [{'metric': 'not a string'}]
        self.assertIn('invalid_journal_record', self.rules(c, trace))

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

    def test_malformed_adapter_fields_remain_failed_results(self):
        for action in ({'kind': 'correct', 'worker': []}, {'kind': 'assign', 'role': []},
                       {'kind': 'direct', 'file': {}}, {'kind': 'restore', 'files': 'parser.py'}):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    validate_response({'actions': [action]})

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
