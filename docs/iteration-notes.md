# Session-informed revision — 2026-10-06

Source locations below identify local evidence; private logs are deliberately not copied into this repository.

| Observation | Evidence | Change |
| --- | --- | --- |
| Template promised a daily script but contained only README/config; config embedded a machine path. | Original harness-template README and config; Garmin harness/daily-audit.py lines 7–9 and output path. | Ship a runnable CLI; resolve paths from config; check before use. |
| Generated audits consumed prior generated audits and produced “Generate skill/doc for” suggestions from those suggestions. | Garmin conversations/2026-09-29-035304-daily-audit.jsonl line 1 and daily-audit-log.jsonl lines 1–2. | Separate reports, exclude legacy generated records, count independent session IDs, preserve evidence locations. |
| An archive reference was missing and directory identities drifted. | Project 135c95e0eb314f8b9e3f25657a8a4ecc conversations/2026-09-29-041210-automation-run.jsonl line 1. | Report unresolved references and missing directories; never claim recovery from secondary summaries. |
| GitHub connector access did not establish local Git access; retries continued until CLI browser authentication changed. | “Push Garmin Readiness App”, chat 01a113ef-a6bb-7ee3-bc9c-d9e59b7568d6, turns 01a113f2-578d-7332-8b8b-f0831992382e and 01a113f4-64fa-72f0-a7b7-5e42b2fb1029. | Separate credential checks, avoid unchanged retries, record only credential source names. |
| A push from a staging checkout left the intended harness-template directory untracked. | Same chat, turn 01a113f6-7417-7243-964d-2fe9b2de836d; local template git status failed. | Check origin/status at the requested source, and make that directory the checkout. |
| Relative environment setup failed after changing directory; setup included a database reset; Docker remained blocked. | “Set up GitHub MCP access”, chat 01a113d4-3225-76b3-a1d7-fd6b53d3e1e1, recent local-development setup commands. | Absolute environment paths, inspect destructive scripts, precise blocker and validation reporting. |

These are targeted fixes supported by the inspected sources, not a claim of statistically recurring behavior. Legacy logs include test observations, malformed dates, and secondary summaries; the new audit exposes limitations rather than turning every string into a skill. The original GUARDRAIL is preserved; no scheduler or global agent configuration is changed.
