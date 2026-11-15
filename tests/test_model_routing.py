import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

from harness.model_routing import (
    DRIVER_ROLES, WORKER_ROLES, Model, Router, RoutingConfig, Target,
    TestOutcome, compact, invoke_astra, invoke_worker, responses_request,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "harness/model_routing.py"


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.config = RoutingConfig.from_mapping(environ={})
        self.router = Router(self.config)
        self.target = Target("fix-cache", "tests/test_cache.py::test_expiry")

    def test_all_agent_instantiations_and_effort_gates(self):
        for role in DRIVER_ROLES:
            with self.subTest(role=role):
                route = self.config.route(role)
                self.assertEqual((route.model, route.reasoning_effort), (Model.SOL, "medium"))
                for effort in ("high", "max"):
                    with self.assertRaises(ValueError):
                        self.config.route(role, effort=effort)
                    for complexity in ("architectural_refactor", "concurrency_debugging", "schema_contract"):
                        self.assertEqual(self.config.route(role, effort=effort, complexity=complexity).reasoning_effort, effort)
                with self.assertRaises(ValueError):
                    self.config.route(role, parallel=True)
        for role in WORKER_ROLES:
            for model in (Model.TERRA, Model.LUNA):
                route = RoutingConfig(subagent_worker_model=model).route(role, parallel=True)
                self.assertEqual((route.model, route.reasoning_effort), (model, "low"))
                self.assertEqual((route.temperature, route.timeout_seconds, route.max_output_tokens), (0.15, 60, 1024))
                with self.assertRaises(ValueError):
                    self.config.route(role, effort="high")
        with self.assertRaises(ValueError):
            self.config.route("escalation")

    def test_config_environment_validation_and_schema_agree(self):
        config = RoutingConfig.from_mapping({"subagent_worker_model": Model.TERRA},
                                            {"SUBAGENT_WORKER_MODEL": Model.LUNA})
        self.assertEqual(config.subagent_worker_model, Model.LUNA)
        schema = json.loads((ROOT / "harness/model-routing.schema.json").read_text())
        self.assertEqual(schema["properties"]["subagent_worker_model"]["enum"], [Model.TERRA, Model.LUNA])
        for key in ("ORCHESTRATOR_MODEL", "SUBAGENT_WORKER_MODEL", "ESCALATION_MODEL"):
            with self.assertRaises(ValueError):
                RoutingConfig.from_mapping(environ={key: "unknown"})
        with self.assertRaises(ValueError):
            RoutingConfig(subagent_worker_model=Model.ASTRA)
        for value in (None, True, 0, 0.09, 0.21, float("nan")):
            with self.assertRaises(ValueError):
                RoutingConfig(worker_temperature=value)
        for value in (None, True, 0, -1, 1.5):
            with self.assertRaises(ValueError):
                RoutingConfig(worker_timeout_seconds=value)
        for value in ([], {"unknown": "value"}, {"worker_timeout_seconds": "60"}):
            with self.assertRaises(ValueError):
                RoutingConfig.from_mapping(value, {})

    def test_consecutive_failures_mixed_fixes_and_target_isolation(self):
        other_file = Target(self.target.task_id, "different-spec")
        other_task = Target("different-task", self.target.file_or_spec)
        for target in (self.target, other_file, other_task):
            self.assertIsNone(self.router.observe_test(target, TestOutcome.FAILURE, attempt=1))
        request = self.router.observe_test(self.target, TestOutcome.REPEATED_FIX,
                                           attempt=2, error="AssertionError: expired cache")
        self.assertEqual(request.route.model, Model.ASTRA)
        self.assertTrue(request.route.single_turn)
        self.assertFalse(request.route.tools_allowed)
        self.assertIsNone(self.router.observe_test(self.target, TestOutcome.FAILURE, attempt=3))
        self.assertIsNone(self.router.observe_test(self.target, TestOutcome.FAILURE, attempt=2))
        self.assertIsNone(self.router.observe_test(self.target, TestOutcome.PASS, attempt=4))
        self.assertIsNone(self.router.observe_test(self.target, TestOutcome.FAILURE, attempt=5))
        self.assertIsNotNone(self.router.observe_test(self.target, TestOutcome.FAILURE, attempt=6))
        self.assertIsNotNone(self.router.observe_test(other_task, TestOutcome.FAILURE, attempt=2))

    def test_blockers_reset_streak_and_invalid_evidence_preserves_retry(self):
        self.router.observe_test(self.target, TestOutcome.FAILURE)
        self.router.observe_test(self.target, TestOutcome.BLOCKED)
        self.assertIsNone(self.router.observe_test(self.target, TestOutcome.FAILURE))
        with self.assertRaises(ValueError):
            self.router.observe_test(self.target, TestOutcome.FAILURE, error=[], attempt=2)
        self.assertIsNotNone(self.router.observe_test(self.target, TestOutcome.FAILURE, attempt=2))

    def test_compact_packet_whitelist_and_zero_context_single_turn(self):
        request = self.router.plan_domain(self.target, interfaces="λ" * 3000, constraints="x" * 2000)
        self.assertIsNone(self.router.plan_domain(self.target))
        payload = request.as_payload()
        self.assertEqual(set(payload), {"trigger", "file_or_spec", "error", "interfaces", "constraints"})
        self.assertLessEqual(len(payload["interfaces"].encode()), 1536)
        self.assertLessEqual(len(payload["constraints"].encode()), 512)
        body = responses_request(request)
        self.assertEqual(body["tools"], [])
        self.assertEqual(body["tool_choice"], "none")
        self.assertFalse(body["store"])
        self.assertFalse({"previous_response_id", "conversation", "history", "bash_output"} & body.keys())
        self.assertEqual(body["reasoning"], {"effort": "high"})
        self.assertEqual(body["max_output_tokens"], 4096)
        self.assertEqual(compact("short", 10), "short")

    def test_parallel_workers_validate_before_any_dispatch(self):
        tasks = [{"role": "scanner", "attempt": 1, "target": {"task_id": str(i), "file_or_spec": "spec"},
                  "packet": {"interfaces": "class Cache"}} for i in range(2)]
        barrier = threading.Barrier(2)

        def adapter(request):
            self.assertEqual(request["settings"]["model"], Model.TERRA)
            self.assertEqual(request["settings"]["reasoning_effort"], "low")
            barrier.wait(timeout=2)
            return {"outcome": "pass"}

        self.assertEqual(len(self.router.dispatch_workers(tasks, adapter)), 2)
        with self.assertRaises(ValueError):
            self.router.dispatch_workers(tasks, adapter)
        tasks[1]["role"] = "implementer"
        with patch("harness.model_routing.ThreadPoolExecutor") as executor:
            with self.assertRaises(ValueError):
                self.router.dispatch_workers(tasks, adapter)
            executor.assert_not_called()
        tasks[1]["role"] = "scanner"
        tasks[1]["packet"]["interfaces"] = []
        with patch("harness.model_routing.ThreadPoolExecutor") as executor:
            with self.assertRaises(ValueError):
                self.router.dispatch_workers(tasks, adapter)
            executor.assert_not_called()

    def test_astra_direct_transport_has_no_shell_or_retry(self):
        request = self.router.plan_domain(self.target)
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "status": "completed", "output": [
                {"type": "reasoning"},
                {"type": "message", "role": "assistant",
                 "content": [{"type": "output_text", "text": "Fix expiry comparison. Verify test_expiry."}]},
            ],
        }).encode()
        opener = MagicMock()
        opener.open.return_value = response
        with patch.dict(os.environ, {"OPENAI_API_KEY": "unit-test-placeholder"}), \
                patch("harness.model_routing.build_opener", return_value=opener), \
                patch("harness.model_routing.subprocess.Popen") as process:
            self.assertIn("Fix expiry", invoke_astra(request))
            opener.open.assert_called_once()
            body = json.loads(opener.open.call_args.args[0].data)
            self.assertEqual(body["tool_choice"], "none")
            process.assert_not_called()
            opener.open.reset_mock()
            opener.open.side_effect = OSError("must never reach user")
            with self.assertRaisesRegex(ValueError, "^tool-free advisory failed"):
                invoke_astra(request)
            opener.open.assert_called_once()


class RoutingCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "harness-config.json"
        self.config.write_text("{}")
        self.environment = dict(os.environ)
        for key in ("ORCHESTRATOR_MODEL", "SUBAGENT_WORKER_MODEL", "ESCALATION_MODEL"):
            self.environment.pop(key, None)

    def cli(self, *args, events=()):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--config", str(self.config), *args],
                              input="".join(json.dumps(event) + "\n" for event in events),
                              capture_output=True, text=True, cwd="/tmp", env=self.environment)

    def adapter(self, body):
        path = self.root / "adapter.py"
        path.write_text("#!" + sys.executable + "\n" + body)
        path.chmod(0o700)
        return str(path)

    def test_old_configs_environment_override_and_invalid_cli(self):
        result = self.cli("route", "verifier", "--parallel")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["model"], Model.TERRA)
        self.environment["SUBAGENT_WORKER_MODEL"] = Model.LUNA
        self.assertEqual(json.loads(self.cli("route", "scanner").stdout)["model"], Model.LUNA)
        self.environment["SUBAGENT_WORKER_MODEL"] = Model.ASTRA
        self.assertEqual(self.cli("check").returncode, 1)

    def test_event_stream_counter_and_compact_payload(self):
        event = {"kind": "test", "target": {"task_id": "t", "file_or_spec": "spec"},
                 "outcome": "failure", "error": "AssertionError", "history": "discard-me",
                 "bash_output": "discard-me", "interfaces": "Cache.get(key)"}
        result = self.cli("run", events=[dict(event, attempt=1), dict(event, attempt=2), dict(event, attempt=3)])
        self.assertEqual(result.returncode, 0, result.stderr)
        first, second, third = map(json.loads, result.stdout.splitlines())
        self.assertIsNone(first["escalation"])
        self.assertIsNone(third["escalation"])
        self.assertEqual(second["escalation"]["handoff"]["model"], Model.SOL)
        self.assertNotIn("discard-me", result.stdout)

    def test_invalid_event_does_not_stop_independent_events_and_exits_nonzero(self):
        result = self.cli("run", events=[{}, {"kind": "zero_context_domain",
                                            "target": {"task_id": "t", "file_or_spec": "spec"}}])
        self.assertEqual(result.returncode, 1)
        first, second = map(json.loads, result.stdout.splitlines())
        self.assertIn("error", first)
        self.assertEqual(second["escalation"]["route"]["model"], Model.ASTRA)

    def test_worker_adapter_enforcement_timeout_and_output_limit(self):
        router = Router(RoutingConfig(worker_timeout_seconds=1))
        task = {"role": "test_runner", "attempt": 1, "target": {"task_id": "t", "file_or_spec": "spec"}, "packet": {}}
        executable = self.adapter("import time\ntime.sleep(30)\n")
        started = time.monotonic()
        reply = router.dispatch_workers([task], lambda request: invoke_worker(executable, request))[0]
        self.assertEqual(reply["outcome"], "blocked")
        self.assertLess(time.monotonic() - started, 3)
        executable = self.adapter("print('x' * 20000)\n")
        task["attempt"] = 2
        reply = router.dispatch_workers([task], lambda request: invoke_worker(executable, request))[0]
        self.assertEqual(reply["outcome"], "blocked")
        executable = self.adapter("print('{}')\n")
        task["attempt"] = 3
        reply = router.dispatch_workers([task], lambda request: invoke_worker(executable, request))[0]
        self.assertEqual(reply["outcome"], "blocked")

    def test_parallel_dispatch_receipts_automatically_escalate_to_sol(self):
        executable = self.adapter(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "print(json.dumps({'outcome': 'failure', 'error': 'AssertionError', "
            "'resolved_settings': request['settings']}))\n")
        task = {"role": "test_runner", "target": {"task_id": "t", "file_or_spec": "spec"},
                "packet": {"interfaces": "Cache.get(key)"}}
        events = [{"kind": "dispatch", "tasks": [dict(task, attempt=i)]} for i in (1, 2)]
        result = self.cli("run", "--worker-adapter", executable, events=events)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipts = [json.loads(line)["workers"][0] for line in result.stdout.splitlines()]
        self.assertIsNone(receipts[0]["escalation"])
        self.assertEqual(receipts[1]["escalation"]["handoff"]["reasoning_effort"], "medium")


if __name__ == "__main__":
    unittest.main()
