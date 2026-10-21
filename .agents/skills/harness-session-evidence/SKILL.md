---
name: harness-session-evidence
description: Save or inspect sanitized project session journals for cross-session handoffs and harness audits. Use when recording development outcomes, resuming from logs, or checking the evidence behind a proposed workflow change.
---

# Session evidence

## When to use it

- Save verified session outcomes or recover source-backed context. Use the configured project journal; no global archive/raw chat copying by default.
- Next-session objectives belong to handoff; cross-session workflow changes to improvement.

## Inspect existing evidence

- Locate intended `harness-config.json`; run `check` to resolve paths. Read relevant records/references, then verify mutable filesystem/runtime state.
- Summaries establish reported claims, not underlying success. Report missing config/sources; configure persistence only in scope, never borrow another project's journal.

## Save a record

- Prepare temporary sanitized JSON:
  - `session_id`: actual chat ID or stable unique session ID, reused across checkpoints.
  - Optional `conversation_id`: actual shared chat ID, nonempty/unpadded; groups distinct phase IDs. Otherwise grouping uses unchanged `session_id`; never infer/strip legacy suffixes. Optional `phase` is metadata.
  - Required string lists: `workflow_insights` (direct observations only), `changes_made` (actual actions/paths), `validation` (performed checks/results, failures/unverified flows), `blockers` (dependencies/next action), `source_references` (external chat/turn or file/line citations; empty allowed).
  - Optional `references_prior_sessions`: existing filenames in this journal only. Structured checks belong in optional `validation_details`, never `validation`.
  - Optional `timestamp`: timezone-aware ISO 8601; omitted means current UTC.
- Exclude inherited proposals/generated report text, secrets, device codes, raw environment/transcripts, sensitive personal data.
- From project root, run `check` before logging:

```bash
python3 harness/audit.py --config harness-config.json check
python3 harness/audit.py --config harness-config.json log --record path/to/session-record.json
```

- Check result and read back the exclusive new JSONL file before claiming persistence. Preserve old journals; disclose failure. Journals/reports are ignored by default; tracked docs may hold sanitized shareable rationale.

## Review patterns

- `audit` aggregates read-only; `audit --write` saves a separate report only when requested.
- Cite filename/line; count independent sessions, exclude generated audits, separate demonstrated failures from suggestions. Logging grants no implementation/scheduling authority.
