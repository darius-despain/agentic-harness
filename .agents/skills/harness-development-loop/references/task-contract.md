# Compact task contracts

Read [orchestration](orchestration.md) and the assigned role. Packets contain paths, criteria, commands and short evidence, never secret contents, journals, raw diffs or verbose logs. Resolve paths from explicit checkout root; do not infer missing authority. Use short IDs and exact files, no recursive repository exploration.

## Implementer assignment and result

```text
track: T1; root: /absolute/checkout; attempt: 1; mode: implement
accept: [observable criteria]
own: [exact writable files]; read: [bounded dependencies/instructions]
baseline: HEAD=<sha>; locked=[paths]; new=[initially absent files]; entry=<metadata/artifact>
checks: [exact commands, cwd, expected behavior]
limits: no journal/preflight/network Git/staging/commit; corrections<=2
```

Return compactly: `track/attempt/status`, changed/new paths, criteria met/unmet, exact checks with exit codes and test counts, and blocker/failure category plus `file:line` citations. Preserve compact failure findings when resuming the implementer. Identify the task and file or spec for failed tests. Keep raw logs out of the handoff.

## Verifier input and receipt

The only task-specific inputs are **acceptance criteria, explicit owned paths, and specific validation commands** (each includes cwd/expected result). Role and inherited repository safety rules are fixed overhead. No implementation narrative, proposed diagnosis, executive history, journal, or repo-wide search. Inspect only `git diff -- <owned_files>` with literal explicit safe paths (disable external diff/textconv). For new files, use a disposable temporary index initialized from HEAD with intent-to-add for only owned new paths, then the same scoped diff; never modify the shared index. No blob inspection outside owned files. If more context is necessary, return the exact missing scope/check; the driver may issue a bounded revised contract. Commands may execute project tests but must not mutate application files or access private contents as diagnostics.

Passing receipt: **at most five lines**, one safety line and four check classes:

```text
track=T1 verdict=pass diff_safety=owned-only,criteria-met guard_staged=pass|blocked|unrun:<reason>
syntax=pass:<command/exit>|NA:<reason>
tests=pass:<command/exit/counts>|NA:<reason>
service_health=pass:<evidence>|NA:<reason>
user_flows=pass:<evidence>|NA:<reason>
```

Run `python3 harness/git_guard.py staged` and report its actual result; it is read-only and is not preflight. Empty index is not proof owned edits are staged; unrelated/private staged entries can block a later commit without invalidating working-tree behavior. `pass` requires all acceptance criteria and required checks; NA requires an explanation and cannot hide a required unrun check. Distinguish passed, failed, expected failures, skips and unrun, with actual test counts; zero executed tests prove nothing. Health and user flows are independent; HTTP 200 is insufficient for authenticated behavior.

Rejection can exceed five lines only to provide compact actionable evidence:

```text
track=T1 verdict=reject
syntax=...; tests=...; service_health=...; user_flows=...
failure: task=<stable-id>; target=<file or spec>; category=changed_code|existing_behavior|environment|credentials|external_dependency; certainty=confirmed|uncertain
evidence: <command/exit/counts, sanitized symptom, owned file:line if supported>
unmet: <criterion>; next: <specific missing check/scope/prerequisite>
```

Use the best-supported category and mark uncertainty explicitly; do not invent a root cause. Return exact findings for retry, no raw logs/diff. A scope or guard failure must also be reported, even when tests pass.

## Investigation and escalation

```text
investigate: track=T1; root=<path>; read=[bounded safe files]; failures=[exact findings]
extract: [requested interfaces or observed state]; checks=[bounded reproductions]
return: task=<stable-id>; target=<file or spec>; evidence=[file:line and core error]; prerequisite=<if any>
```

The Tier 1 investigator extracts evidence and exits after the assigned checks.

```text
escalate: task=<stable-id>; target=<file or spec>; trigger=<second same-target failure or zero-context architecture>
error: <sanitized core error and expected behavior>
interfaces: <relevant signatures and constraints>
return: <supported cause and deterministic blueprint or isolated fix>; verify=<checks>
```

The driver sends a bounded packet through the tool-free, one-response Astra path. Omit execution history, verbose shell output, and raw diffs. The driver takes back control for edits and verification.

## Cleanup

```text
cleanup: track=T1; root=<path>; own=[exact files]; changed=[track-modified subset]
entry=<HEAD/status/index metadata, authorized dirty preservation artifact>; new=[proven track-created files]
save=.harness/handoffs/blocked-T1.patch; blocker=<brief>; mode=Tier-2-cleanup
```

Cleanup returns exactly three lines:

```text
track=T1 cleanup=restored|incomplete patch=<actual path|unavailable>
preserved=baseline-and-earlier-tracks; restored=[paths]; removed=[track-created files]; checks=<metadata/patch verification>
blocker=<category, symptom, prerequisite>; retained=[paths if incomplete]
```

Never claim preservation/restoration without evidence. No shared-index changes, broad reset/stash/clean, or private contents. Follow orchestration's patch-before-restore and dirty-exception rules.

## Session record and telemetry

The Tier 2 driver invokes the logger and verifies the saved record. Use at most three entries per list and at most 120 characters per string. Keep the required fields as string lists and use no custom nested objects.

```json
{
  "session_id": "stable-session-id",
  "workflow_insights": ["[ORCH_TELEMETRY] track=T1 | outcome=verified | spawns=Impl:1,Ver:1,Inv:0,Clean:0,Esc:0 | cycles=0 | escalated=false"],
  "changes_made": ["T1: observed resulting behavior"],
  "validation": ["syntax: outcome; tests: command/exit/counts; service_health: outcome; user_flows: outcome"],
  "blockers": [],
  "source_references": ["path/to/changed-file:12"]
}
```

Replace examples with actual observations and citations. Use short IDs and the telemetry format below for recorded tracks, within the list and string limits.

```text
[ORCH_TELEMETRY] track=<id> | outcome=<verified|blocked-reverted|escalated> | spawns=Impl:<n>,Ver:<n>,Inv:<n>,Clean:<n>,Esc:<n> | cycles=<n> | escalated=<true|false>
```

Count actual role starts and Astra requests. Record correction cycles actually used (0–2). Use the `escalated` outcome for unresolved tracks without verified restoration. Retain cleanup details and patch paths in the compact `blockers` string list.
