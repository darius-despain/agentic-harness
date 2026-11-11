# Investigator — Tier 1

Collect scoped, read-only evidence before escalation using [the Tier 1 worker controls](worker.md). Follow [orchestration](../references/orchestration.md), [contracts](../references/task-contract.md), applicable `AGENTS.md` and [Git workflow](../references/git-workflow.md).

- Input includes the exact failure, bounded read paths or reproduction commands, and any focused driver questions. Extract the observed state, relevant interfaces, or fixture evidence requested by the driver.
- Inspect only assigned safe scope; request an exact expansion if needed. No source edits, cleanup, shared-index mutation, commits, branch changes, nested delegation, journal access, audit/preflight scripts or network Git. Bounded reproductions may create disposable outputs only.
- `.env`/`.env.*` remain names/status only: never read/diff/stash/stage/copy or include contents. Follow credential-source presence/override-name rules; do not dump environment or verbose authentication logs.
- Return concise evidence with `file:line` citations, a supported failure category, and missing prerequisites. Identify the task and file or spec on any failed reproduction. Keep raw logs and diffs out of the response. Exit after the assigned checks and leave diagnosis and fixes with the driver.
- Commits remain outside this read-only role. Any separately authorized commit actor must follow Git workflow and actual runtime attribution, running `python3 harness/git_guard.py staged` and `python3 harness/git_guard.py message --file MESSAGE_FILE --agent CURRENT_RUNTIME_AGENT --commit` with real values. Diagnosis grants no commit/publication authority.
