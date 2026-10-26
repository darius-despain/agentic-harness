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

Return compactly: `track/attempt/status`, changed/new paths, criteria met/unmet, exact checks with exit codes and test counts, and blocker/failure category plus `file:line` citations. Preserve failure findings verbatim when resuming the same Implementer. Return no code or raw logs to Sol. Unknown facts stay unknown.

## Verifier input and receipt

The only task-specific inputs are **acceptance criteria, explicit owned paths, and specific validation commands** (each includes cwd/expected result). Role and inherited repository safety rules are fixed overhead. No implementation narrative, proposed diagnosis, executive history, journal, or repo-wide search. Inspect only `git diff -- <owned_files>` with literal explicit safe paths (disable external diff/textconv). For new files, use a disposable temporary index initialized from HEAD with intent-to-add for only owned new paths, then the same scoped diff; never modify the shared index. No blob inspection outside owned files. If more context is necessary, return the exact missing scope/check; Sol may issue a bounded revised contract, not an exploration mandate. Commands may execute project tests but must not mutate application files or access private contents as diagnostics.

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
failure: category=changed_code|existing_behavior|environment|credentials|external_dependency; certainty=confirmed|uncertain
evidence: <command/exit/counts, sanitized symptom, owned file:line if supported>
unmet: <criterion>; next: <specific missing check/scope/prerequisite>
```

Use the best-supported category and mark uncertainty explicitly; do not invent a root cause. Return exact findings for retry, no raw logs/diff. A scope or guard failure must also be reported, even when tests pass.

## Investigator and cleanup

```text
investigate: track=T1; root=<path>; read=[bounded safe files]; failures=[exact findings]
questions: [2–3 symptom/category-based reframings]; checks=[bounded reproductions]
return: diagnosis=<supported|unresolved>; cause=<brief>; evidence=[file:line]; direction=<bounded fix>; prerequisite=<if any>
```

Read-only investigation grants no edits, cleanup, journal/preflight/network Git, or nested delegation. Supported direction is not implementation; unresolved diagnosis must not be presented as a verified fix.

```text
cleanup: track=T1; root=<path>; own=[exact files]; changed=[track-modified subset]
entry=<HEAD/status/index metadata, authorized dirty preservation artifact>; new=[proven track-created files]
save=.harness/handoffs/blocked-T1.patch; blocker=<brief>; mode=Sol-low
```

Cleanup returns exactly three lines:

```text
track=T1 cleanup=restored|incomplete patch=<actual path|unavailable>
preserved=baseline-and-earlier-tracks; restored=[paths]; removed=[track-created files]; checks=<metadata/patch verification>
blocker=<category, symptom, prerequisite>; retained=[paths if incomplete]
```

Never claim preservation/restoration without evidence. No shared-index changes, broad reset/stash/clean, or private contents. Follow orchestration's patch-before-restore and dirty-exception rules.

## Session record and telemetry

Only Sol invokes the logger and verifies the resulting JSONL. All required fields below are string lists except `session_id`; `validation_details` is optional structured metadata supported by the logger, not an auditor aggregation API. **Output Token Diet:** Maximum **3 items** per array, maximum **120 characters** per string entry. Ban custom nested objects.

```json
{
  "session_id": "stable-session-id",
  "workflow_insights": ["[ORCH] mode=subagent | spawns=Impl(Sol-Low):1,Ver(Sol-Low):1 | cycles=0 | outcome=verified"],
  "changes_made": ["T1: observed resulting behavior"],
  "validation": ["syntax: outcome; tests: command/exit/counts; service_health: outcome; user_flows: outcome"],
  "blockers": [],
  "source_references": ["path/to/changed-file:12"],
  "validation_details": {"orchestration": [{"track": "T1", "outcome": "verified", "spawns": {"implementer": 1, "verifier": 1, "investigator": 0, "cleanup": 0}, "cycles": 0, "reframed": false}]}
}
```

Replace examples with actual observations/citations and one telemetry string per track, exactly:

```text
[ORCH] mode=<fast-path|subagent> | spawns=Impl(Sol-Low):1,Ver(Sol-Low):1 | cycles=0 | outcome=verified
```

Count spawns, not resumptions; record correction cycles actually used (0–2). Use `escalated` for unresolved tracks without verified restoration; retain cleanup details and patch paths in `blockers`/structured metadata. No invented token savings, test results, or spawn counts.
