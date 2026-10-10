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

## Project installation repair — 2026-10-09 (America/Denver)

Direct inspection of the Garmin project confirmed that its repaired CLI passes all
seven logger regressions and reads the newly saved session. The previous failure is
recorded at `garmin-readiness-app/conversations/2026-10-10-761ed1002c4e4523b3f01bf645edb368.jsonl:1`
(UTC filename), with pre-repair file/line references in `harness/REPAIR-NOTES.md:8-15`.
The template's manual installation guidance did not provide a project installer;
`harness/install_links.py` installs global assets, not project-local files.

Implemented `harness/install_project.py` and documented it in
[project setup](project-setup.md). It previews by default, installs missing local
assets only on `--apply`, preserves existing config and files, refuses conflicts and
linked installation targets, initializes configured directories, and verifies config.
Six integration regressions exercise preview, end-to-end log/audit, rerun behavior,
existing config/ignore preservation, conflicts, legacy layout, and symlink boundaries.
Together with the original seven logger tests, all 13 pass.

Evidence limitations: `conversations/2026-09-28-203000-session-audit.jsonl:1`
contains a test observation, and `2026-09-20-100000-old.jsonl:1` contains a placeholder
observation. Neither supports recurring real-work claims. This change is a targeted
response to a verified installation gap, not a newly inferred recurring pattern.
Fixture reclassification, automated legacy migration, scheduler setup, and changes
to global links are deferred. Historical records and pre-existing template edits
are preserved. No credentials or conversation dumps are included here.
