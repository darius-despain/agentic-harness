# Portable agentic harness

A project-local session journal and evidence audit using Python 3.9+ and no external packages. Logging is explicit: installing the template does not capture chats or schedule a daily agent.

## Setup

Copy `harness/`, `AGENTS.md`, and `harness-config-template.json` into your project (merge existing agent instructions rather than replacing them). Copy the config to `harness-config.json` beside the project root, set `project`, and run:

```bash
python3 harness/audit.py --config harness-config.json check
```

Paths are relative to the config file. Absolute paths, parent traversal, and symlinks escaping the project are rejected. Session journals and generated reports stay separate. Add the supplied ignore patterns to your project's `.gitignore`; private session logs and machine-specific config should not be committed.

## Save a session

Create a sanitized JSON record, for example:

```json
{
  "session_id": "unique-chat-or-session-id",
  "workflow_insights": ["Environment setup needs an absolute path when changing directories"],
  "changes_made": ["Corrected the setup command"],
  "validation": ["Dependency install completed"],
  "blockers": [],
  "references_prior_sessions": []
}
```

```bash
python3 harness/audit.py --config harness-config.json log --record session-record.json
```

The command writes a new exclusive JSONL file with a UTC timestamp. Existing journals remain untouched. Never include credentials, raw transcripts, or sensitive personal data. References should identify existing journal filenames; audit findings cite filename and line number.

## Review evidence

```bash
python3 harness/audit.py --config harness-config.json audit
python3 harness/audit.py --config harness-config.json audit --write
python3 -m unittest discover -s tests -v
```

The default audit is read-only. `--write` creates a separate report under `harness/reports`. Freshness uses each record's timezone-aware timestamp, not its filename. Exact matching observations recur only across distinct session IDs, with a configurable threshold. Suggestions are not automatically implemented. Legacy daily-audit and automation outputs are excluded, malformed records are reported, and unresolved references are surfaced. Missing source journals cannot be recovered from summaries; do not fabricate them.

For scheduled use, configure your scheduler separately to invoke the command with an absolute config path. Notify only on actionable new findings, failures, or required input. Do not automatically modify code or send messages based on journal text.

See `docs/iteration-notes.md` for evidence behind this revision and `GUARDRAIL.md` for the original workspace policy.
