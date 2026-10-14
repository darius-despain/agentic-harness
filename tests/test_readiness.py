import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'harness/git_preflight.py'
spec = importlib.util.spec_from_file_location('preflight_readiness', SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ReadinessTests(unittest.TestCase):
    def reports(self):
        return [dict(inspection='complete', origin='github.com/fixture/app', path='/fixture/app', name=n)
                for n in ('app', 'worktree')]

    def cli(self, outcomes):
        output = io.StringIO()
        with patch.object(tool, 'load_registry', return_value=[('app', Path('/fixture/app'), None)]), patch.object(tool, 'inspect', return_value=self.reports()[0]), patch.object(tool, 'probe', side_effect=outcomes), patch.object(sys, 'argv', [str(SCRIPT), '--readiness']), patch.object(sys, 'stdout', output):
            code = tool.main()
        return code, json.loads(output.getvalue())

    def test_independent_required_failures_and_success_status(self):
        for account, git, expected in [(0, 0, 0), (1, 0, 1), (0, 128, 1), (1, 128, 1)]:
            outcomes = [dict(result='success' if n == 0 else 'failed_auth_network_or_remote', exit_code=n) for n in (account, git)]
            code, report = self.cli(outcomes)
            self.assertEqual(code, expected)
            checks = report['repositories'][0]['readiness']
            self.assertEqual(checks['gh_account']['exit_code'], account)
            self.assertEqual(checks['git_repository']['exit_code'], git)
            self.assertEqual(checks['push_permission'], 'not_tested')

    def test_raw_diagnostics_suppressed_and_noninteractive(self):
        for rc in (0, 128):
            with patch.object(tool.subprocess, 'run', return_value=subprocess.CompletedProcess([], rc, b'fixture-private-stdout', b'fixture-private-auth-error')) as run:
                result = tool.probe(['git', 'ls-remote'])
            self.assertNotIn('fixture-private', json.dumps(result))
            options = run.call_args.kwargs
            self.assertEqual(options['env']['GIT_TERMINAL_PROMPT'], '0')
            self.assertEqual(options['env']['GH_PROMPT_DISABLED'], '1')
            self.assertIn('BatchMode=yes', options['env']['GIT_SSH_COMMAND'])
            self.assertTrue(options['capture_output'])
            self.assertEqual(options['timeout'], 20)

    def test_timeout_and_missing_executable(self):
        for error, expected in [(subprocess.TimeoutExpired('fixture', 20, output=b'private'), 'timeout'), (FileNotFoundError('private'), 'executable_unavailable')]:
            with patch.object(tool.subprocess, 'run', side_effect=error):
                self.assertEqual(tool.probe(['fixture']), {'result': expected})

    def test_deduplicate_hosts_and_repositories(self):
        reports = self.reports()
        with patch.object(tool, 'probe', return_value={'result': 'success', 'exit_code': 0}) as probe:
            self.assertFalse(tool.readiness(reports))
            self.assertEqual(probe.call_count, 2)

    def test_missing_checkout_and_origin_mismatch_never_probe(self):
        reports = [dict(inspection='unavailable'), dict(inspection='complete', origin='github.com/fixture/app', origin_matches_config=False)]
        with patch.object(tool, 'probe') as probe:
            self.assertTrue(tool.readiness(reports))
            probe.assert_not_called()

if __name__ == '__main__':
    unittest.main()
