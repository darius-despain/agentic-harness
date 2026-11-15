# Model routing

This is an optional **Codex-specific** integration. Load or invoke it only when
tiered routing or orchestrated mode is explicitly enabled. Selecting a tool profile
alone preserves the current runtime settings and does not run the router. Other
profiles use their native capabilities without these OpenAI model requirements.

## Driver and worker policy

- `ORCHESTRATOR_MODEL` defaults to `gpt-6.1-sol` at medium reasoning. The driver owns pairing, implementation, TDD, integrations, and code review. Use high or max reasoning only for refactors spanning architectural boundaries, complex concurrency or async debugging, or schema contract planning.
- Delegate mechanical work such as linting, test execution, boilerplate, file scans, diff inspection, and log parsing to `SUBAGENT_WORKER_MODEL`. Use `gpt-6.1-terra` by default or explicitly configure `gpt-6-luna`. All parallel dispatches use the configured worker model, low reasoning, temperature 0.1–0.2, and an enforced timeout. Workers return compact diffs or findings and exit immediately after their assigned checks complete.
- Count consecutive failures against the same task and file or spec. On the second failed test or repeated fix, or when starting a zero-context architecture, the driver may request one `ESCALATION_MODEL` (`gpt-6-astra`) advisory response. Pass only the core error, relevant interfaces, and constraints. Astra has no tools, write access, shell, or delegation. The driver takes back control to implement and verify the blueprint or isolated fix.
- Use runtime controls to enforce model, reasoning, time limits, and tool access. If a required control is unavailable, report the affected route as unavailable and continue independently where possible. Keep the scoped [orchestration protocol](../.agents/skills/harness-development-loop/references/orchestration.md) for opted-in sessions.


`harness/model_routing.py` provides validated routes, an in-memory failure
counter, bounded worker dispatch and a single-request Astra advisory transport.
Role prompts live under `.agents/skills/harness-development-loop/agents/`.

## Tiers and configuration

| Tier | Roles | Model | Controls |
| --- | --- | --- | --- |
| 1 | worker, verifier, scanner, test_runner, investigator | `gpt-6.1-terra` or `gpt-6-luna` | low reasoning, temperature 0.15, 60-second timeout, 1024 output tokens |
| 2 | orchestrator, implementer, reviewer, cleanup | `gpt-6.1-sol` | medium reasoning |
| 3 | escalation advisory | `gpt-6-astra` | one response, high reasoning, 4096 output tokens, tools disabled |

Existing project configs receive these defaults. Add a `model_routing` object to
the project's `harness-config.json` to customize the supported settings.

```json
{
  "model_routing": {
    "orchestrator_model": "gpt-6.1-sol",
    "subagent_worker_model": "gpt-6.1-terra",
    "escalation_model": "gpt-6-astra",
    "worker_temperature": 0.15,
    "worker_timeout_seconds": 60
  }
}
```

`ORCHESTRATOR_MODEL`, `SUBAGENT_WORKER_MODEL` and `ESCALATION_MODEL` override their
corresponding config values when present in the process environment. Validation
requires Sol for driver roles, Terra/Luna for workers and Astra for advisories.
Worker temperature must be 0.1–0.2 and timeout must be a positive integer.
Unknown routing keys fail validation. Astra cannot be assigned a worker role.

```bash
python3 harness/model_routing.py --config harness-config.json check
python3 harness/model_routing.py --config harness-config.json route orchestrator
python3 harness/model_routing.py --config harness-config.json route scanner --parallel
python3 harness/model_routing.py --config harness-config.json route implementer \
    --effort high --complexity architectural_refactor
```

The eligible complexity values are `architectural_refactor`,
`concurrency_debugging` and `schema_contract`. High/max driver effort requires
one of these values. Worker effort stays low. Parallel driver dispatch is
rejected. `route` prints settings for the host to apply.

## Failure events and handoffs

`run` reads one JSON event per stdin line and emits one JSON receipt per stdout
line. Keep the process running throughout a session to retain its counters.
Restarting starts a fresh counter. Feed trusted execution receipts to the router.

```bash
python3 harness/model_routing.py --config harness-config.json run <<'JSONL'
{"kind":"test","target":{"task_id":"T1","file_or_spec":"tests/test_api.py::test_contract"},"attempt":1,"outcome":"failure","error":"AssertionError: expected schema version 2","interfaces":"API returns {version: int}","constraints":"Preserve existing clients"}
{"kind":"test","target":{"task_id":"T1","file_or_spec":"tests/test_api.py::test_contract"},"attempt":2,"outcome":"failure","error":"AssertionError: expected schema version 2","interfaces":"API returns {version: int}","constraints":"Preserve existing clients"}
JSONL
```

Every target combines a stable `task_id` with `file_or_spec`. Supply a positive,
increasing `attempt` for test events. Duplicate or older attempts are ignored.
Supported outcomes are `pass`, `failure`, `repeated_fix` and `blocked`.
Two consecutive failed attempts create an escalation request, including mixed
`failure` and `repeated_fix` outcomes. Passing or blocked execution clears the
streak. Further failures in the same streak do
not repeatedly escalate.

The first example receipt has a null escalation. The second contains an
`escalation` with the route, compact evidence and Sol/medium handoff settings.
The driver implements the returned direction and verifies the result. A
zero-context domain can request one advisory per target using this event.

```json
{"kind":"zero_context_domain","target":{"task_id":"T2","file_or_spec":"new-domain-contract"},"interfaces":"Input and output contract under design","constraints":"Define the minimum implementation and verification steps"}
```

Only `error`, `interfaces`, `constraints`, the target spec and the trigger reach
Astra. Extract the core error trace and relevant interfaces before submission.
The router drops unrelated event fields and caps evidence in UTF-8 bytes at
1024 for error, 1536 for interfaces, 512 for constraints and 256 for the spec.
Keep credentials and private configuration outside every packet.

Malformed events produce an error receipt, subsequent lines continue processing
and the process ultimately exits 1. Hosts must also inspect receipts for
blocked/unavailable outcomes. Process exit zero alone does not establish
successful task execution.

## Worker adapter contract

The host supplies an executable adapter for mechanical execution. Dispatch
validates the whole batch first, then runs up to four adapter processes in
parallel. Every task must use a worker role and a unique target within its batch.
Dispatch attempts must increase per target. Replayed or stale attempts are
rejected before launching workers. Interface and constraint fields must be text.

```bash
python3 harness/model_routing.py --config harness-config.json run \
    --worker-adapter /absolute/path/to/worker-adapter <<'JSONL'
{"kind":"dispatch","tasks":[{"target":{"task_id":"T1","file_or_spec":"tests/test_api.py"},"role":"test_runner","attempt":1,"packet":{"acceptance":"Run the named test and return its exit status","interfaces":"API version contract","constraints":"Read-only verification"}}]}
JSONL
```

Each adapter process receives one stdin JSON request containing `target`,
`role`, `packet` and `settings`. Packets are capped at 8192 UTF-8 bytes.
`settings` contains the complete routed model, effort, temperature, timeout,
output-token limit and capability flags. The adapter must apply these settings,
honor the assigned file scope, stop when its check completes and emit one JSON
object before exiting.

```json
{
  "outcome": "pass",
  "error": "",
  "report": "tests passed; exit=0; changed files=[]",
  "resolved_settings": {
    "tier": 1,
    "model": "gpt-6.1-terra",
    "reasoning_effort": "low",
    "temperature": 0.15,
    "timeout_seconds": 60,
    "max_output_tokens": 1024,
    "single_turn": false,
    "tools_allowed": true
  }
}
```

`resolved_settings` must exactly match the request. The harness checks this
receipt, applies a process timeout, suppresses adapter stderr and rejects invalid
or oversized responses. It caps reports at 4096 UTF-8 bytes. A nonzero adapter
exit, timeout or incompatible settings produces `blocked`. The adapter is a
trusted execution boundary and must truthfully report what its backend enforced.
It must return `blocked` when required controls are unavailable.

Current OpenAI APIs accept `temperature` only when reasoning effort is `none`.
The configured worker policy requests `low` together with temperature 0.1–0.2,
so an adapter using those APIs must report that route unavailable. Native Codex
subagent controls expose model and reasoning effort, with no documented
temperature setting. The worker transport requires an adapter capable of the
whole configured policy. The included local checks verify routing with synthetic
adapters. [Official API compatibility guidance](https://developers.openai.com/api/docs/guides/latest-model#update-api-and-model-parameters),
[Codex custom agent controls](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agent-file-schema).

## One-shot Astra transport

`run --live-escalation` makes one stateless request to the official Responses
API when a trigger fires. The process consumes `OPENAI_API_KEY` from its
environment. Keep credentials in the approved terminal or credential source.

The request has `tools=[]`, `tool_choice="none"` and `store=false`, with no prior
response ID or transcript. It requests one advisory, applies a 90-second socket
operation timeout, limits the HTTP response read to 131073 bytes and performs no
retries or redirects. Total elapsed time can exceed the socket timeout. The
transport returns a blueprint or an `unavailable` receipt. Sol receives control
for file edits and tests.

Live API access and authenticated model execution require separate verification.
The harness test suite uses fixtures and mocked responses.

## Linked projects

Use absolute CLI and config paths when a project keeps its harness outside the
current Git root. MIQA's shared workspace provides these commands from its web
checkouts.

```bash
python3 /home/ddespain/workspace/MIQA/harness/model_routing.py \
    --config /home/ddespain/workspace/MIQA/harness-config.json check
python3 /home/ddespain/workspace/MIQA/harness/model_routing.py \
    --config /home/ddespain/workspace/MIQA/harness-config.json route verifier
```

Adapt machine paths for another installation. A direct consumer `harness` link
shares the router immediately. The global `~/.codex/AGENTS.md` and
`~/.agents/skills/harness-*` links share the instruction and role prompts.
Start a fresh Codex run after changing instructions or skills so instruction
discovery loads the revised files. Preserve project-local configs and journals.
Reviewed copied installations need the updated router, prompts, references and
merged routing instructions. [Instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance).
