# Agent evaluation episodes

Standard-library Python framework, initially covering the orchestrator. Run from the checkout root:

```bash
cd /home/ddespain/workspace/harness-template
python3 -m evals.agents.runner --case failure --output /tmp/orchestrator-failure.json
python3 -m evals.agents.runner --config evals/agents/offline.json --output /tmp/orchestrator-matrix.json
python3 -m unittest discover -s tests -v
```

The default matrix runs eight cases against known good and bad traces. These are
**scorer calibration**, not model scores. They exercise direct/delegated work,
shared file and service ownership, failed correction cycles, blocked credentials,
stale checks, unavailable model routing, user steering and authorization.
No workers, provider requests, Git mutations or services run.

## Experiment boundary

Each case is a versioned scenario with sequential fixed observations. A coordinator
returns structured actions at each turn; the runner feeds back its previous actions
and the next scripted worker/tool response. All candidates receive identical worker
behavior. This is an open-loop simulation: observations advance even if the model
does not dispatch the expected task. Missing actions lose credit. It measures reaction
and contract compliance under a curated script, not actual task completion or worker
performance. Use a separate future environment adapter for action-conditioned live
workers; never combine those measurements under this execution label.

`required` patterns earn equal-weight deterministic partial credit on the specified
turn. Extra prose does not score. Patterns match action fields, not exact headings.
`forbidden` patterns and temporal invariants track hard violations separately:
overlapping writers, incomplete packets, capacity, stale acceptance, unknown actions,
and worker/root authority boundaries. A hard violation fails the episode even with
full quality credit. Tests calibrate both directions and mutate good traces.
The scorer does not semantically establish whether a context packet is sufficient,
a preservation claim is true, or a reported test actually executed. No semantic
judge is implemented; such a judge must have a separately versioned rubric, identity,
usage and calibration traces. Results must retain these limits.

## Comparing models

Copy `models.example.json` to a local config and replace the command and exact model
IDs with a supported authenticated runtime adapter. No provider adapter or runtime
model availability is assumed. The command is an argv array, invoked from the current
working directory once per decision. Use absolute paths. It reads one JSON request
from stdin and writes one JSON response to stdout; diagnostics belong on stderr.
Never print credentials. No shell is used. Model/reasoning/seed are requested fields;
only returned `resolved_settings` establishes what the backend actually used.

```bash
python3 -m evals.agents.runner --config /tmp/my-models.json --allow-external --output /tmp/model-results.json
```

Use this only after choosing the authenticated adapter and agreeing the spending
scope. `--allow-external` explicitly permits command execution. The runner checks
max runs and external calls before execution and reserves
`calls * per_call_cost_ceiling_usd <= max_cost_usd`. Execution is serial (concurrency
one), with one total timeout per case. The adapter **must enforce** the supplied
per-call dollar ceiling, token/output limits, and disable hidden retries or include
them in that ceiling. Reservation is not a provider billing guarantee; the framework
cannot enforce charges inside arbitrary external commands. No default prices are
assumed. For estimates, adapters must return dated pricing sources in usage metadata.
Timeout kills the direct adapter process; adapters must manage their own children
and cancel provider work. Inherited environment credentials remain inside the local
process; this is not isolation or automatic redaction. Use only trusted adapters and
synthetic fixtures. Adapters must sanitize actions/telemetry before stdout; raw stderr
is discarded. Do not point this runner at private transcripts or environment files.

Request fields: `protocol_version`, `instructions`, current role `contracts`,
`profile`, `scenario`, `action_kinds`, `history`, `observation`. Hidden rubric and
calibration actions are excluded. Response:

```json
{
  "actions": [{"kind": "correct", "worker": "w", "cause": "changed_code"}],
  "usage": {"input_tokens": 100, "output_tokens": 20, "cached_tokens": 0, "reasoning_tokens": 10},
  "resolved_settings": {"model": "actual-id", "reasoning": "high"},
  "cost_usd": null
}
```

Actions use the case vocabulary. Assignments contain worker, role, files, context,
acceptance and state; include model/reasoning/fresh_context for routing decisions.
Release ends a worker's ownership; verify identifies state, edit invalidates verification,
and accept must name the checked state. Other actions use file, task, resource,
question, cause, limitation or coverage as relevant to the observation. Cases use
synthetic `/workspace/repo` paths, never the developer's actual checkout. Actions
are records, never executable tools.

## Results and extensions

JSON results include schema version, UTC timestamp, protocol/contracts/suite/scorer
hashes, profile and requested settings, per-turn traces, exposed resolved settings,
usage categories, cost, wall latency, launch/tool counts, checks and violations.
`results.schema.json` describes the envelope. Missing usage/cost remains null;
scripted timings measure local replay only. Adapter latency includes process startup.
Tool counts include simulated verify/access calls; worker launches count assignments,
not actual processes. Cost totals remain unknown if any component is unknown.
Adapter errors and timeouts are failed runs and remain in pass-rate denominators.
Comparison lists each repetition's latency; per-case results retain variation. Do not
rank models or claim significance from the calibration matrix or a tiny live sample.
Worker scripts and contracts are hashed so differing experiments can be recognized.

Add implementer/verifier/investigator JSON cases with the same turn structure and
run `--suite /absolute/path/to/suite.json`. Add role-specific contracts in `run`,
new action invariants in `score`, and adversarial calibration tests before use.
Changing `role` metadata alone does not load another role prompt. Replace `episode`
for an action-conditioned environment; retain the common scored result envelope
and set a new execution label for live workers. Keep reports outside session journals;
only actual implementation/validation outcomes belong in the harness journal.
