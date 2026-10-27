import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'harness/install_project.py'

sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("install_project", SCRIPT)
install_project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install_project)
sys.path.pop(0)


class ProjectInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_install(self, apply=True, success=True):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), str(self.root),
                                 '--project', 'fixture', *(['--apply'] if apply else [])],
                                cwd='/tmp', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 1, result.stderr)
        return result

    def test_preview_roundtrip_and_idempotence(self):
        self.assertTrue(json.loads(self.run_install(apply=False).stdout)['changes'])
        self.assertEqual(list(self.root.iterdir()), [])
        self.run_install()
        base = [sys.executable, str(self.root/'harness/audit.py'), '--config', str(self.root/'harness-config.json')]
        record = self.root/'record.json'
        record.write_text(json.dumps(dict(session_id='installer-fixture', workflow_insights=['fixture'],
                                         changes_made=[], validation=[], blockers=[], source_references=[])))
        subprocess.run(base+['log','--record',str(record)],check=True,capture_output=True)
        audit=json.loads(subprocess.run(base+['audit'],check=True,capture_output=True,text=True).stdout)
        self.assertEqual(audit['findings'][0]['session_count'],1)
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(json.loads(self.run_install().stdout)['changes'],[])
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_preserves_existing_config_and_ignore(self):
        (self.root/'.gitignore').write_text('user-rule')
        self.run_install()
        self.assertTrue((self.root/'.gitignore').read_text().startswith('user-rule\n'))
        path=self.root/'harness-config.json'
        data=json.loads(path.read_text())
        data['max_age_days']=17
        path.write_text(json.dumps(data))
        original=path.read_bytes()
        self.run_install()
        self.assertEqual(path.read_bytes(),original)

    def test_literal_gitignore_paths(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.run_install()
        config_path = self.root / 'harness-config.json'
        config = json.loads(config_path.read_text())
        paths = ('notes[private]', 'reports*?\\literal')
        config.update(session_persistence_dir=paths[0], audit_output_dir=paths[1])
        config_path.write_text(json.dumps(config))
        self.run_install()
        for directory in paths:
            result = subprocess.run(['git', '-C', str(self.root), 'check-ignore',
                                     '--quiet', '--', directory + '/entry.jsonl'])
            self.assertEqual(result.returncode, 0, directory)
        for sibling in ('notesp', 'reportsXXliteral', 'notesprivate'):
            result = subprocess.run(['git', '-C', str(self.root), 'check-ignore',
                                     '--quiet', '--', sibling + '/entry.jsonl'])
            self.assertEqual(result.returncode, 1, sibling)
        self.assertEqual(json.loads(self.run_install().stdout)['changes'], [])

    def test_line_break_paths_fail_without_changes(self):
        self.run_install()
        config_path = self.root / 'harness-config.json'
        config = json.loads(config_path.read_text())
        for line_break in ('\n', '\r'):
            with self.subTest(line_break=repr(line_break)):
                config['session_persistence_dir'] = 'notes' + line_break + 'private'
                config_path.write_text(json.dumps(config))
                before = {str(p.relative_to(self.root)): p.read_bytes()
                          for p in self.root.rglob('*') if p.is_file()}
                self.run_install(success=False)
                self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes()
                                         for p in self.root.rglob('*') if p.is_file()})
                self.assertFalse((self.root / config['session_persistence_dir']).exists())

    def test_conflicting_cli_fails_without_changes(self):
        (self.root/'harness').mkdir()
        (self.root/'harness/audit.py').write_text('existing user code')
        self.run_install(success=False)
        self.assertEqual((self.root/'harness/audit.py').read_text(),'existing user code')
        self.assertFalse((self.root/'harness-config.json').exists())

    def test_nested_legacy_config_requires_migration(self):
        (self.root/'harness').mkdir()
        (self.root/'harness/harness-config.json').write_text('{}')
        self.run_install(success=False)
        self.assertFalse((self.root/'harness/audit.py').exists())

    def test_symlink_targets_are_not_modified(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'harness').symlink_to(outside, target_is_directory=True)
            self.run_install(success=False)
            self.assertEqual(list(Path(outside).iterdir()),[])

    def test_escaping_journal_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'conversations').symlink_to(outside, target_is_directory=True)
            self.run_install(success=False)
            self.assertFalse((self.root/'harness').exists())
            self.assertEqual(list(Path(outside).iterdir()),[])



    @patch('sys.stderr', new_callable=io.StringIO)
    def test_main_prints_installation_error(self, mock_stderr):
        with patch.object(install_project, 'install', side_effect=ValueError('mock error')):
            with patch('sys.argv', ['install_project.py', str(self.root), '--project', 'fixture']):
                result = install_project.main()
                self.assertEqual(result, 1)
                self.assertIn('Installation error: mock error', mock_stderr.getvalue())

if __name__ == '__main__':
    unittest.main()
