# Agent evaluation episodes

Run the standard-library Python framework from the checkout root.

```bash
python3 -m evals.agents.runner --case failure --output /tmp/orchestrator-failure.json
python3 -m evals.agents.runner --config evals/agents/offline.json --output /tmp/orchestrator-matrix.json
python3 -m unittest discover -s tests -v
```

The version-3 default matrix calibrates twelve scenarios against known good and bad
traces. Cases cover scoped delegation, shared ownership, two repeated test failures,
blocked credentials, stale checks, unavailable advisory capabilities, user steering,
parallel mechanical workers and zero-context domain scaffolding. Scripted replay
creates simulated decisions and reports `live_multi_agent: false`.

## Tier policy

The scorer imports the production `harness.model_routing` policy. It tracks test
outcomes by task and file/spec using the same router as the runtime. Offline replay
resolves `model_routing` settings from the evaluation config with an empty environment
for reproducibility.

- Tier 1 uses the configured `gpt-6.1-terra` worker, with `gpt-6-luna` supported as
  an explicit configuration choice. Verifiers, evidence investigators, scanners and
  test runners receive low reasoning, temperature 0.15 and a 60-second timeout by
  default. Parallel scenarios enforce the configured worker model for every slot.
- Tier 2 uses `gpt-6.1-sol` with medium reasoning for the driver, serial implementer
  and scoped cleanup. High or max reasoning requires an eligible
  `architectural_refactor`, `concurrency_debugging` or `schema_contract` complexity
  field on the assignment.
- Tier 3 uses `gpt-6-astra` for one tool-free advisory after two consecutive failures
  on the same target, or for zero-context domain scaffolding. An `escalate` action
  requests the compact router payload. The next trusted blueprint observation hands
  control back to Sol for implementation and verification. The scorer rejects Astra
  worker assignments, extra escalation history/tools fields and repeated advisory
  requests during the same failure streak.

The default serial cases retain one active worker and same-instance Sol correction.
An explicit `parallel_slots` scenario permits independent Tier 1 work. Workers
release their slots upon completion. Cleanup preserves failed changes in a scoped
patch before restoration and independent-track pivoting.

## Experiment boundary

Each case supplies versioned fixed observations. The coordinator returns structured
actions for the current observation, then receives the next scripted response.
Observations advance even when an expected assignment is missing. The score measures
reaction and contract compliance under that script. Actual worker execution belongs
to the production runtime and its adapter verification.

Required action patterns earn deterministic partial credit. Hard violations fail an
episode independently of that credit. Invariants cover private paths, write scope,
capacity, model routing, independent verification, stale acceptance, correction limits,
cleanup ordering and root-owned schema-compatible journaling. Synthetic event
metadata drives the production failure counter and blueprint availability. These
events come from the fixture, while the adapter sees the corresponding observation,
routing settings and compact escalation payload.

Receipts distinguish syntax, tests, service health and user flows. Tests require a
positive count and exit zero. Telemetry uses role counts and the advisory count.
Ver includes test runners, and Inv includes scanners.

```text
[ORCH_TELEMETRY] track=T1 | outcome=verified | spawns=Impl:1,Ver:1,Inv:0,Clean:0,Esc:1 | cycles=2 | escalated=true
```

Calibration checks declared structure and ordering. Claims about sufficient context,
supported diagnosis, recoverable patches and actual command execution require
separate live verification. A future action-conditioned adapter must use a distinct
execution label and retain its own evidence.

## External coordinator adapters

Copy `models.example.json` to a local config and set an absolute adapter command.
The example requests Sol medium. The command is an argv array invoked once per
decision, reading one JSON request from stdin and returning one JSON response on
stdout. Use a trusted adapter that sanitizes stdout and keeps credential values
inside the local process. Adapter stderr is discarded. Inherited credentials remain
accessible to that process.

```bash
python3 -m evals.agents.runner --config /tmp/my-models.json --allow-external --output /tmp/model-results.json
```

External execution requires `--allow-external` and an explicit call/cost budget.
The runner checks the run and call limits before execution and reserves
`calls * per_call_cost_ceiling_usd <= max_cost_usd`. The adapter must enforce the
supplied cost ceiling, output/token limits and bounded retries. Reservation measures
declared spending scope. Provider charge enforcement depends on the adapter.
The example reserves twelve decisions across two repetitions of the failure episode.
Its $0.12 ceiling is illustrative.

The coordinator process receives a total per-case timeout. Its adapter must manage
child processes and provider cancellation. An Astra coordinator profile is rejected
because coordinator decisions form an interactive loop. Advisory decisions remain
simulated within this evaluation. Runtime advisory requests use the production
tool-free transport.

Command profiles enforce the configured Sol driver. High or max reasoning requires
an eligible complexity field. The returned resolved model and reasoning receipt must
match the requested route for the decision to succeed.

## Adapter protocol

These scenarios explicitly select the Codex harness profile and orchestrated
mode; evaluation model profiles do not change that selection or trigger a prompt.
Hashed contracts include `AGENTS.md`, `harness/CORE.md`, the selected
`harness/profiles/codex.md`, and the executive/Git routing instructions. Worker
prompts and other tool profiles are not loaded into every coordinator request.

Request fields include `protocol_version`, `instructions`, `contracts`, `profile`,
`routing`, `escalation`, `scenario`, `scope`, `action_kinds`, `history` and
`observation`. The role routes expose requested model, effort, temperature, timeout
and output bounds. External commands must return a matching `resolved_settings`
receipt identifying their backend model and reasoning.

A pending `escalation` contains the requested model and a whitelisted payload with
trigger, file/spec, core error, relevant interfaces and constraints. Coordinator
history stays outside that payload. The production router caps every evidence field
before it reaches the advisory request. Hidden rubric and calibration actions remain
outside the coordinator request.

```json
{
  "actions": [
    {"kind": "escalate", "target": "parser.py::test_eof", "model": "gpt-6-astra", "single_turn": true}
  ],
  "usage": {"input_tokens": 100, "output_tokens": 20, "reasoning_tokens": 10},
  "resolved_settings": {"model": "gpt-6.1-sol", "reasoning": "medium"},
  "cost_usd": null
}
```

Assignments declare worker, role, exact files, compact context, acceptance, state,
model, reasoning and `fresh_context: true`. Verifiers also declare concrete checks.
`correct` resumes the existing Sol implementer and consumes a correction cycle.
`escalate` accepts exactly kind, target, model and single_turn. A trusted blueprint
observation must precede the final correction and its explicit direction.
`verify` supplies an independent five-line receipt, `edit` invalidates verification,
and `accept` identifies the checked revision. Journal actions contain the logger's
required string lists and root ownership.

## Results and extensions

Results include schema version 3, UTC timestamp, protocol/contracts/suite/scorer/router
hashes, requested profile settings, traces, resolved settings, usage, cost and latency.
`worker_launches` counts simulated assignments. `advisory_requests` counts simulated
one-turn advisory calls. Missing usage and cost remain null. Adapter startup contributes
to latency, and failed runs remain in pass-rate denominators.

Version-3 scores and hashes require fresh calibration. Custom cases declare mode,
track, allowed files, optional locked/new paths, required checks and parallel slots.
Trusted `event.test` records declare task ID, file/spec, outcome and compact evidence.
`event.zero_context_domain` requests domain scaffolding, and
`event.blueprint_ready` supplies the single-turn handoff boundary.

Extend role-specific cases and adversarial tests alongside new invariants. Keep
reports outside session journals. Actual implementation and verification outcomes
may be recorded through the configured session logger.
