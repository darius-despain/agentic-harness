import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "harness/git_preflight.py"
spec = importlib.util.spec_from_file_location("git_preflight", SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class GitPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.repo / "source.txt").write_text("base\n")
        self.git("add", "source.txt")
        self.git("commit", "-m", "fixture")
        self.config = self.root / "harness-config.json"
        self.config.write_text(json.dumps({"git_repositories": {
            "app": {"path": "repo", "origin": "github.com/fixture/app"}}}))

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    def test_readonly_dirty_inventory_and_credential_redaction(self):
        self.git("remote", "add", "origin", "https://fixture-user:fixture-password@github.com/fixture/app.git?fixture-query")
        self.git("config", "credential.helper", "!echo fixture-helper-value")
        (self.repo / "source.txt").write_text("edited\n")
        (self.repo / "notes.txt").write_text("notes\n")
        before = self.git("status", "--porcelain")
        with patch.dict(os.environ, {"GH_TOKEN": "fixture-override-value"}):
            report = tool.inspect(self.repo, "github.com/fixture/app")
        encoded = json.dumps(report)
        for hidden in ("fixture-password", "fixture-query", "fixture-helper-value", "fixture-override-value"):
            self.assertNotIn(hidden, encoded)
        self.assertFalse(report["clean"])
        self.assertTrue(report["origin_matches_config"])
        self.assertIn("GH_TOKEN", report["credential_override_names_present"])
        self.assertEqual(report["local_git_network_access"], "not_probed")
        self.assertEqual(before, self.git("status", "--porcelain"))

    def test_rename_parsing_and_private_path_names_only(self):
        self.git("mv", "source.txt", "renamed file.txt")
        # Fixture names exercise status only; no populated environment files are read.
        (self.repo / ".env.fixture").write_text("synthetic fixture\n")
        report = tool.inspect(self.repo)
        changes = {c["path"]: c for c in report["changes"]}
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes["renamed file.txt"]["code"], "R ")
        self.assertTrue(changes[".env.fixture"]["private_configuration"])
        self.assertNotIn("synthetic fixture", json.dumps(report))

    def test_wrong_checkout_and_symlink_escape(self):
        inside = self.repo / "directory"
        inside.mkdir()
        self.assertEqual(tool.inspect(inside)["inspection"], "unavailable")
        self.config.write_text(json.dumps({"git_repositories": {"bad": {"path": "../escape"}}}))
        with self.assertRaises(ValueError):
            tool.load_registry(self.config)
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        self.config.write_text(json.dumps({"git_repositories": {"bad": {"path": "escape"}}}))
        with self.assertRaises(ValueError):
            tool.load_registry(self.config)

    def test_uninitialized_submodule_is_not_mistaken_for_clean_parent(self):
        head = self.git("rev-parse", "HEAD")
        self.git("update-index", "--add", "--cacheinfo", f"160000,{head},components/app")
        report = tool.inspect(self.repo)
        child = report["submodules"][0]
        self.assertEqual(child["inspection"], "unavailable")
        self.assertIsNone(child["matches_gitlink"])

    def test_cached_divergence_and_detached_head(self):
        self.git("remote", "add", "origin", "https://github.com/fixture/app.git")
        base = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", base)
        self.git("config", "branch.main.remote", "origin")
        self.git("config", "branch.main.merge", "refs/heads/main")
        self.git("commit", "--allow-empty", "-m", "local")
        report = tool.inspect(self.repo)
        self.assertEqual(report["cached_history"], {"ahead": 1, "behind": 0})
        self.git("checkout", "--detach")
        report = tool.inspect(self.repo)
        self.assertIsNone(report["branch"])
        self.assertIsNone(report["cached_history"])

    def test_required_inspection_failure_never_reports_clean(self):
        actual = tool.run
        def failing(path, *args):
            return (128, "") if args[0] == "status" else actual(path, *args)
        with patch.object(tool, "run", side_effect=failing):
            report = tool.inspect(self.repo)
        self.assertEqual(report["inspection"], "unavailable")
        self.assertNotIn("clean", report)

    def test_config_is_relative_to_file_and_cli_returns_mismatch(self):
        self.git("remote", "add", "origin", "https://github.com/fixture/wrong.git")
        result = subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config)],
                                cwd="/tmp", capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)["repositories"][0]
        self.assertEqual(report["path"], str(self.repo))
        self.assertFalse(report["origin_matches_config"])

    def test_probe_failure_is_suppressed_and_not_repeated_for_same_origin(self):
        self.git("remote", "add", "origin", "https://github.com/fixture/app.git")
        actual = tool.run
        calls = []
        def probing(command):
            calls.append(command)
            return {"result": "failed_auth_network_or_remote", "exit_code": 128}
        entries = [("first", self.repo, None), ("second", self.repo, None)]
        from io import StringIO
        output = StringIO()
        with patch.object(tool, "probe", side_effect=probing), patch.object(tool, "load_registry", return_value=entries), patch.object(sys, "argv", [str(SCRIPT), "--probe-remote"]), patch.object(sys, "stdout", output):
            code = tool.main()
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 1)
        self.assertNotIn("fixture-private-raw-error", output.getvalue())

    def test_host_scoped_helper_is_detected_without_exposing_its_value(self):
        self.git("remote", "add", "origin", "https://github.com/fixture/app.git")
        self.git("config", "credential.https://github.com.helper", "!fixture-scoped-helper")
        report = tool.inspect(self.repo)
        self.assertFalse(report["generic_credential_helper_present"])
        self.assertTrue(report["origin_credential_helper_present"])
        self.assertNotIn("fixture-scoped-helper", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
