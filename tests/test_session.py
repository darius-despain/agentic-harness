import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from harness import session


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'harness/session.py'


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        self.settings = self.root / '.harness/local.json'

    def run_cli(self, *args, code=0, script=SCRIPT):
        result = subprocess.run(
            [sys.executable, str(script), '--root', str(self.root), *args],
            input='', capture_output=True, text=True, cwd=self.temp.name)
        self.assertEqual(result.returncode, code, result.stderr)
        return result

    def save(self, value):
        self.settings.parent.mkdir(exist_ok=True)
        self.settings.write_text(json.dumps(value))

    def test_each_profile_is_explicit_and_read_only(self):
        for tool in session.TOOLS:
            with self.subTest(tool=tool):
                result = json.loads(self.run_cli('--tool', tool).stdout)
                self.assertEqual(result['tool'], tool)
                self.assertEqual(result['source'], 'explicit')
                self.assertFalse(result['remembered'])
                self.assertEqual(result['load'], [str(ROOT / 'harness/CORE.md'),
                                                  str(ROOT / 'harness/profiles' / (tool + '.md'))])
                self.assertEqual(list(self.root.iterdir()), [])

    def test_unattended_missing_choice_fails_without_writes(self):
        result = self.run_cli(code=2)
        self.assertIn('no tool selected', result.stderr)
        self.assertIn('--tool', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_terminal_prompt_retries_invalid_choice_without_saving(self):
        with patch.object(session.sys.stdin, 'isatty', return_value=True), \
                patch('builtins.input', side_effect=['unknown', ' Antigravity ']), \
                patch.object(session.sys, 'stderr', new_callable=io.StringIO) as error:
            result = session.select(self.root)
        self.assertEqual(result['tool'], 'antigravity')
        self.assertEqual(result['source'], 'prompt')
        self.assertIn('Enter one of', error.getvalue())
        self.assertFalse(self.settings.exists())

    def test_terminal_eof_is_reported_without_persistence(self):
        with patch.object(session.sys, 'argv', ['session.py', '--root', str(self.root)]), \
                patch.object(session.sys.stdin, 'isatty', return_value=True), \
                patch('builtins.input', side_effect=EOFError), \
                patch.object(session.sys, 'stderr', new_callable=io.StringIO):
            self.assertEqual(session.main(), 2)
        self.assertFalse(self.settings.exists())

    def test_remember_override_and_forget_preserve_other_local_keys(self):
        self.save({'other_preference': 'keep'})
        self.run_cli('--tool', 'codex', '--remember')
        self.assertEqual(json.loads(self.settings.read_text()),
                         {'other_preference': 'keep', 'tool': 'codex'})
        result = json.loads(self.run_cli().stdout)
        self.assertEqual((result['tool'], result['source']), ('codex', 'local'))
        before = self.settings.read_bytes()
        override = json.loads(self.run_cli('--tool', 'claude-code').stdout)
        self.assertEqual(override['tool'], 'claude-code')
        self.assertEqual(self.settings.read_bytes(), before)
        self.run_cli('--tool', 'antigravity', '--remember')
        self.assertEqual(json.loads(self.settings.read_text())['tool'], 'antigravity')
        self.run_cli('--forget')
        self.assertEqual(json.loads(self.settings.read_text()), {'other_preference': 'keep'})
        self.run_cli(code=2)

    def test_forget_absent_preference_does_not_create_files(self):
        self.run_cli('--forget')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_malformed_settings_can_be_temporarily_overridden_but_not_rewritten(self):
        self.settings.parent.mkdir()
        for content in ('{', '[]'):
            with self.subTest(content=content):
                self.settings.write_text(content)
                self.run_cli(code=2)
                self.run_cli('--tool', 'generic')
                self.run_cli('--tool', 'generic', '--remember', code=2)
                self.run_cli('--forget', code=2)
                self.assertEqual(self.settings.read_text(), content)

    def test_invalid_saved_choice_requires_explicit_selection(self):
        for tool in ('unknown', 12, ['codex'], None):
            with self.subTest(tool=tool):
                self.save({'tool': tool})
                self.assertIn('invalid tool preference', self.run_cli(code=2).stderr)
                self.run_cli('--tool', 'generic', '--remember')
                self.assertEqual(json.loads(self.settings.read_text())['tool'], 'generic')

    def test_local_instructions_are_optional_and_do_not_change_profile(self):
        local = self.root / 'AGENTS.local.md'
        local.write_text('Use concise progress updates.')
        result = json.loads(self.run_cli('--tool', 'generic').stdout)
        self.assertEqual(result['load'][-1], str(local))
        self.assertEqual(result['tool'], 'generic')

    def test_settings_directory_symlink_is_refused(self):
        outside = Path(self.temp.name) / 'shared'
        outside.mkdir()
        (self.root / '.harness').symlink_to(outside, target_is_directory=True)
        self.run_cli('--tool', 'codex', '--remember', code=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_settings_file_symlink_is_never_read_or_modified(self):
        outside = Path(self.temp.name) / 'private-settings'
        outside.write_text('must not be parsed as JSON')
        self.settings.parent.mkdir()
        self.settings.symlink_to(outside)
        result = self.run_cli('--tool', 'codex', '--remember', code=2)
        self.assertIn('refusing symlinked', result.stderr)
        self.assertEqual(outside.read_text(), 'must not be parsed as JSON')

    def test_local_instruction_symlink_is_refused_before_saving(self):
        outside = Path(self.temp.name) / 'private-instructions'
        outside.write_text('unrelated')
        (self.root / 'AGENTS.local.md').symlink_to(outside)
        self.run_cli('--tool', 'codex', '--remember', code=2)
        self.assertFalse(self.settings.exists())

    def test_invalid_root_and_conflicting_flags_fail(self):
        self.root.rmdir()
        self.run_cli('--tool', 'codex', code=2)
        self.root.mkdir()
        self.run_cli('--forget', '--remember', code=2)
        self.run_cli('--forget', '--tool', 'codex', code=2)
        self.run_cli('--tool', 'unknown', code=2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_incomplete_installation_cannot_save_preference(self):
        partial = Path(self.temp.name) / 'harness'
        partial.mkdir()
        shutil.copyfile(SCRIPT, partial / 'session.py')
        shutil.copyfile(ROOT / 'harness/CORE.md', partial / 'CORE.md')
        result = self.run_cli('--tool', 'codex', '--remember', code=2,
                              script=partial / 'session.py')
        self.assertIn('incomplete harness installation', result.stderr)
        self.assertFalse(self.settings.exists())

    def test_linked_script_loads_shared_assets_and_consumer_preferences(self):
        linked = Path(self.temp.name) / 'shared-session.py'
        linked.symlink_to(SCRIPT)
        local = self.root / 'AGENTS.local.md'
        local.write_text('Consumer-only instructions.')
        result = json.loads(self.run_cli('--tool', 'generic', '--remember', script=linked).stdout)
        self.assertEqual(result['load'][0], str(ROOT / 'harness/CORE.md'))
        self.assertEqual(result['load'][-1], str(local))
        self.assertEqual(json.loads(self.settings.read_text()), {'tool': 'generic'})

    def test_native_bridges_and_portable_profile_assets_are_present(self):
        self.assertIn('@AGENTS.md', (ROOT / 'CLAUDE.md').read_text())
        rule = (ROOT / '.agent/rules/harness.md').read_text()
        self.assertTrue(rule.startswith('---\ntrigger: always_on\n---\n'))
        self.assertIn('AGENTS.md', rule)
        for tool in session.TOOLS:
            self.assertTrue((ROOT / 'harness/profiles' / (tool + '.md')).is_file())


if __name__ == '__main__':
    unittest.main()
