import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "harness/git_guard.py"
sys.path.insert(0, str(SCRIPT.parent))
try:
    spec = importlib.util.spec_from_file_location("git_guard", SCRIPT)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
finally:
    sys.path.pop(0)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="harness guard ")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.env = dict(os.environ)
        self.env.pop("HARNESS_AI_AGENT", None)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.hooksPath", str(self.repo / "hooks"))
        (self.repo / "source.txt").write_text("synthetic source\n")
        self.git("add", "source.txt")
        self.git("commit", "-m", "initial fixture")
        self.blob = self.git("rev-parse", "HEAD:source.txt").stdout.strip()

    def git(self, *args, check=True, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=check,
                              capture_output=True, text=True, env=env or self.env)

    def install_adapters(self):
        (self.repo / "hooks").mkdir()
        for name in ("pre-commit", "commit-msg"):
            (self.repo / "hooks" / name).symlink_to(ROOT / "harness/hooks" / name)

    def add_private_metadata(self, name="server/.env"):
        self.git("update-index", "--add", "--cacheinfo", f"100644,{self.blob},{name}")

    def test_safe_names_unborn_and_unstaged_private_metadata(self):
        guard.check_staged(self.repo)
        self.add_private_metadata()
        self.git("commit", "-m", "synthetic metadata only")
        # Working private file is absent; only its staged difference matters.
        guard.check_staged(self.repo)
        other = self.repo / "unborn"
        other.mkdir()
        self.git("-C", str(other), "init")
        (other / "source.txt").write_text("safe\n")
        self.git("-C", str(other), "add", "source.txt")
        guard.check_staged(other)

    def test_private_additions_deletions_and_rename_sources(self):
        self.add_private_metadata("nested space/.env.example")
        with self.assertRaises(ValueError):
            guard.check_staged(self.repo)
        self.git("commit", "-m", "synthetic metadata only")
        self.git("update-index", "--force-remove", "nested space/.env.example")
        with self.assertRaises(ValueError):
            guard.check_staged(self.repo)
        self.git("update-index", "--add", "--cacheinfo", f"100644,{self.blob},public.txt")
        with self.assertRaises(ValueError):
            guard.check_staged(self.repo)

    def test_private_rename_destination_and_unusual_name(self):
        self.git("update-index", "--force-remove", "source.txt")
        self.add_private_metadata("line\nbreak/.env.fixture")
        with self.assertRaises(ValueError):
            guard.check_staged(self.repo)

    def test_metadata_only_and_failed_git_is_closed_without_diagnostics(self):
        actual = subprocess.run
        def metadata(command, **kwargs):
            self.assertEqual(command[5:8], ["diff", "--cached", "--name-only"])
            self.assertIn("--no-renames", command)
            return actual(command, **kwargs)
        with patch.object(guard.subprocess, "run", side_effect=metadata):
            guard.check_staged(self.repo)
        with patch.object(guard.subprocess, "run", return_value=subprocess.CompletedProcess([], 128, b"", b"private diagnostic")):
            with self.assertRaisesRegex(ValueError, "diagnostics suppressed") as raised:
                guard.check_staged(self.repo)
        self.assertNotIn("private diagnostic", str(raised.exception))

    def test_messages_require_exact_runtime_identity_and_never_rewrite(self):
        message = self.repo / "message.txt"
        for content in ("change", "Co-authored by: Someone Else (AI)",
                        "prefix Co-authored by: Test Agent (AI)", " Co-authored by: Test Agent (AI)"):
            message.write_text(content)
            with self.assertRaises(ValueError):
                guard.check_message(message, "Test Agent")
            self.assertEqual(message.read_text(), content)
        message.write_text("change\n\nCo-authored by: Test Agent (AI)\n")
        guard.check_message(message, "Test Agent")
        for invalid in ("", "  ", " Test Agent", "Test\nAgent"):
            with self.assertRaises(ValueError):
                guard.check_message(message, invalid)
        result = subprocess.run([sys.executable, str(SCRIPT), "message", "--file", str(message),
                                 "--agent", "Test Agent"], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_private_message_path_refused_without_open(self):
        with patch.object(Path, "read_text", side_effect=AssertionError("must not read")):
            with self.assertRaises(ValueError):
                guard.check_message(self.repo / ".env", "Test Agent")

    def test_hook_chain_human_ai_empty_identity_and_index_preservation(self):
        self.install_adapters()
        self.git("commit", "--allow-empty", "-m", "human change")
        env = dict(self.env, HARNESS_AI_AGENT="Test Agent")
        before = self.git("rev-parse", "HEAD").stdout
        rejected = self.git("commit", "--allow-empty", "-m", "AI change", check=False, env=env)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(before, self.git("rev-parse", "HEAD").stdout)
        rejected = self.git("commit", "--allow-empty", "-m", "change", check=False,
                            env=dict(self.env, HARNESS_AI_AGENT=""))
        self.assertNotEqual(rejected.returncode, 0)
        self.git("commit", "--allow-empty", "-m", "change\n\nCo-authored by: Test Agent (AI)", env=env)
        self.add_private_metadata()
        before = self.git("ls-files", "--stage", "-z").stdout
        rejected = self.git("commit", "-m", "must fail", check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(before, self.git("ls-files", "--stage", "-z").stdout)
        self.assertNotIn("synthetic source", rejected.stderr)

    def test_commit_cleanup_rejects_discarded_attribution(self):
        self.install_adapters()
        env = dict(self.env, HARNESS_AI_AGENT="Test Agent", GIT_EDITOR="true")
        message = self.repo / "message.txt"
        before = self.git("rev-parse", "HEAD").stdout
        for prefix in ("#", ";"):
            self.git("config", "core.commentChar", prefix)
            message.write_text("change\n\n" + prefix + " ------------------------ >8 ------------------------\n"
                               "Co-authored by: Test Agent (AI)\n")
            rejected = self.git("commit", "--allow-empty", "--cleanup=scissors", "--edit",
                                "--file", str(message), check=False, env=env)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(before, self.git("rev-parse", "HEAD").stdout)
            # PR/MR bodies have no Git cleanup semantics.
            guard.check_message(message, "Test Agent")
        self.git("config", "core.commentChar", "C")
        message.write_text("change\n\nCo-authored by: Test Agent (AI)\n")
        rejected = self.git("commit", "--allow-empty", "--cleanup=strip", "--edit",
                            "--file", str(message), check=False, env=env)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(before, self.git("rev-parse", "HEAD").stdout)
        self.git("config", "core.commentChar", "#")
        # Older Git ignores commentString; the default scissors marker still
        # removes the attribution. Guard both prefixes without version guessing.
        self.git("config", "core.commentString", "//")
        message.write_text("change\n\n# ------------------------ >8 ------------------------\n"
                           "Co-authored by: Test Agent (AI)\n")
        rejected = self.git("commit", "--allow-empty", "--cleanup=scissors", "--edit",
                            "--file", str(message), check=False, env=env)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(before, self.git("rev-parse", "HEAD").stdout)
        self.git("config", "--unset", "core.commentString")
        message.write_text("change\n\nCo-authored by: Test Agent (AI)\n"
                           "# ------------------------ >8 ------------------------\nignored tail\n")
        self.git("commit", "--allow-empty", "--cleanup=scissors", "--edit", "--file", str(message), env=env)
        committed = self.git("log", "-1", "--format=%B").stdout
        self.assertIn("Co-authored by: Test Agent (AI)", committed.splitlines())
        self.assertNotIn("ignored tail", committed)

    def test_unreadable_message_diagnostics_do_not_echo_decoder_details(self):
        message = self.repo / "message.txt"
        message.write_bytes(b"\xff private-message-fixture")
        result = subprocess.run([sys.executable, str(SCRIPT), "message", "--file", str(message),
                                 "--agent", "Test Agent"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "Harness guard: message file unavailable or unreadable")

    def test_scoped_commit_uses_git_supplied_index(self):
        self.install_adapters()
        self.add_private_metadata()
        (self.repo / "source.txt").write_text("safe update\n")
        self.git("commit", "--only", "source.txt", "-m", "scoped human change")
        staged = self.git("diff", "--cached", "--name-only").stdout
        self.assertIn("server/.env", staged)
        self.assertNotIn("source.txt", staged)


if __name__ == "__main__":
    unittest.main()
