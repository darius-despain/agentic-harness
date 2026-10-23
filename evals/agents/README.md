# Agent evaluation episodes

Standard-library Python framework, initially covering the orchestrator. Run from the checkout root:

```bash
# Run in your agentic-harness checkout; no personal machine path is required.
python3 -m evals.agents.runner --case failure --output /tmp/orchestrator-failure.json
python3 -m evals.agents.runner --config evals/agents/offline.json --output /tmp/orchestrator-matrix.json
python3 -m unittest discover -s tests -v
```

The version-2 default matrix runs ten cases against known good and bad traces. These are
**scorer calibration**, not model scores. They exercise direct/delegated work,
shared file and service ownership, failed correction cycles, blocked credentials,
stale checks, unavailable model routing, user steering and authorization. It targets
the sequential contract merged in #8, not the parallel design from #6. Additional
checks cover one active worker including read-only roles, same-instance correction,
2–3 Socratic questions, one final directed fix, Sol-low patch-before-restore cleanup,
independent-track pivoting, executive code/diff/log exclusions, baseline dirty locks,
five-line verification receipts, root-only schema-compatible journaling and exact
`[ORCH_TELEMETRY]` counts. The single-agent default and honest unavailable-topology
fallback are separate from opted-in executive mode.
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
out-of-scope/private paths, incomplete packets, single-worker capacity, stale acceptance,
correction limits, cleanup order, telemetry and worker/root authority boundaries.
File checks enforce both case authorization and each active worker's assigned files.
Final acceptance and telemetry must remain valid after all actions, not merely have
appeared earlier. Logger validation includes optional conversation IDs, timestamps
and prior-session string lists, with differential tests against the real CLI.
A hard violation fails the episode even with
full quality credit. Tests calibrate both directions and mutate good traces.
Requirements match structured decisions, not arbitrary packet/receipt wording.
Trusted synthetic event metadata supplies failure timing and diagnosis availability;
the model receives the corresponding observations and explicit allowed/locked scope,
not hidden scoring requirements or calibration traces.
The scorer does not semantically establish whether a context packet is sufficient,
Socratic questions are insightful, a preservation claim/patch is true or recoverable,
or a reported test actually executed. It checks declared structure and ordering;
it does not implement a Git cleanup engine or exercise real credentials. No semantic
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
`profile`, `scenario`, `scope`, `action_kinds`, `history`, `observation`. Version 2
includes AGENTS.md, Git workflow and executive routing contracts in the hashed context.
Worker role prompts are not loaded into every coordinator request.
Hidden rubric and
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
Verifier packets also name specific `checks`; investigator packets carry the same
2–3 `questions` and the failure `findings` used for reframing.
Simulated worker model names use `sol` and the role's reasoning level; these action
labels do not choose the actual coordinator provider/model. `assign` creates an
instance; `correct` resumes the same implementer and consumes one correction cycle.
Release ends an active slot, preserving the idle instance for reuse. Verify includes
its independent worker, checked state and five-line receipt; edit invalidates verification,
and accept must name the checked state. Other actions use file, task, resource,
questions, cause, limitation or coverage as relevant to the observation. Cleanup
records explicit patch/restore/result/release/pivot actions; none runs Git. Telemetry
uses the exact metric string and counts simulated instance creation, not resumes.
Journal actions declare a root-owned record with the logger's required string lists.
Cases use
synthetic `/workspace/repo` paths, never the developer's actual checkout. Actions
are records, never executable tools.

## Results and extensions

JSON results include schema version, UTC timestamp, protocol/contracts/suite/scorer
hashes, profile and requested settings, per-turn traces, exposed resolved settings,
usage categories, cost, wall latency, launch/tool counts, checks and violations.
`results.schema.json` describes the envelope. Missing usage/cost remains null;
scripted timings measure local replay only. Adapter latency includes process startup.
Tool counts include simulated verify/access calls; worker launches count assignments
(including investigator/cleanup roles),
not actual processes. Cost totals remain unknown if any component is unknown.
Adapter errors and timeouts are failed runs and remain in pass-rate denominators.
Comparison lists each repetition's latency; per-case results retain variation. Do not
rank models or claim significance from the calibration matrix or a tiny live sample.
Worker scripts and contracts are hashed so differing experiments can be recognized.

Results/protocol/case versions are now 2; old calibration hashes/scores are not
comparable. Custom version-2 cases declare `mode`, `track`, `allowed_files`, optional
`locked_files`/`new_files`/`required_checks`, and explicit observations. `event` is
trusted fixture metadata for failure attempt, uncertainty, external blocker and
supported diagnosis; never accept it from an adapter. Keep live action-conditioned
testing separate and require explicit spending approval before provider comparisons.
The example external matrix now reserves 24 decisions (six per failure episode,
two profiles, two repetitions); its $0.24 ceiling is illustrative, not a model price.

Add implementer/verifier/investigator JSON cases with the same turn structure and
run `--suite /absolute/path/to/suite.json`. Add role-specific contracts in `run`,
new action invariants in `score`, and adversarial calibration tests before use.
Changing `role` metadata alone does not load another role prompt. Replace `episode`
for an action-conditioned environment; retain the common scored result envelope
and set a new execution label for live workers. Keep reports outside session journals;
only actual implementation/validation outcomes belong in the harness journal.
