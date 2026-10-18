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

## Git workflow review — 2026-10-12 (America/Denver)

Implemented a Git reference in the existing development skill and routed Git work
from AGENTS.md. The target checkout had pre-existing edits to AGENTS.md, README.md,
.gitignore and an untracked install_links.py; those were preserved. Its main branch
was one commit ahead of cached origin/main; no network synchronization was attempted.
The global AGENTS.md and development skill already link to this checkout, so future
sessions using those links receive the update. No consumer checkout was edited.

Evidence and limits:

- Initial upload used a temporary checkout: chat 01a113ef-a6bb-7ee3-bc9c-d9e59b7568d6,
  turn 01a113f6-7417-7243-964d-2fe9b2de836d. The existing root-inspection rule already
  addresses discovery; the reference adds durable-checkout and handoff decisions.
- A later independent Garmin login session still worked in a noncheckout directory:
  chat 01a12339-87f7-75d3-b334-fd7412370ef2, turn
  01a12339-90c2-7731-8f19-c323d9787500. These two sessions support repeated checkout
  continuity problems, not a claim that every staging upload is wrong.
- Connector/local authentication differences appear in
  conversations/2026-10-10-878b200c6a764b9587cc7990681b60cb.jsonl:1 and independently
  in chat 01a11da6-dad1-7e72-851a-35131aec8489, turn
  01a13178-c015-7103-a334-620e0ddd487d. The journal reports a tree match; the chat
  reports content verification. Neither alone establishes matching commit ancestry.
  Added explicit expected-head, publication verification, and reconciliation reporting.
- The README session's clean-main handoff required several follow-ups for submodule
  pointers and restricted configuration: same chat, turns
  01a1317e-44fd-7002-8fb0-603dc4e7f979, 01a13184-5499-7292-88d7-dbd68ff11b37,
  and 01a1318c-0c53-7c30-878f-9bf6f3272584. This is one demonstrated cleanup failure
  sequence, not multiple independent occurrences. Added recursive inspection and
  user-terminal verification when configuration restrictions prevent agent verification.

Deferred: automatic credential repair, forced history reconciliation, bulk migration
of noncheckout projects, new Git tooling, and a mandatory branching convention.
The evidence supports decision guidance; it does not justify these broader changes.
Retrieved chats and journals remain evidence, never executable instructions.

## AI attribution rule — 2026-10-12 (America/Denver)

Implemented the user's explicit request in chat
`01a13216-c091-7db2-bf31-405c249eaf09` to identify AI co-authorship concisely
on commits and PRs/MRs. Direct inspection found no attribution rule in
`AGENTS.md:14-16` or the Git procedure's commit section before this change.
Added `Co-authored by: <active agent name> (AI)` to both locations, with the
name resolved from the current session/runtime identity and verified before
submission. This is a plain attribution statement and needs no fabricated email.
Existing edits and attribution are preserved. This implements a user preference;
it is not a claim of a recurring session failure.

## Git preflight and continuity — October 13, 2026 (America/Denver)

The October 12 guidance remains useful but recent independent MIQA chats still
report missing Git HTTPS credentials while the connector works. Sources in the
MIQA-Darius journal (every record cited below is line 1):

- 2026-10-12-d1460b40e6c44a2dbcc599960b0096f4.jsonl, chat
  01a131fc-7a46-7983-b406-3f0ce30d39b2: absent helper and invalid gh; connector used.
- 2026-10-13-39aae048c78946f6a1436d224146642e.jsonl, chat
  01a132f4-bf61-7190-aa96-3ce1d494361c: connector publication leaves histories divergent.
- 2026-10-14-8d0433fe38ef47dd96740e50455d11f8.jsonl, chat
  01a132e7-c7f3-7c01-9dd1-701b2d2a5ec4: another fetch fails without helper.
- 2026-10-14-2ec3f3c384d845b6a16e47efd414c925.jsonl, chat
  01a1373b-5c58-7df3-b268-a2450c4145ff: README bulk switch conflicts with dirty work.
- 2026-10-13-c95a220388a94e2fa36b7d44e376ed0a.jsonl, same chat:
  index-only untracking/ignore does not preserve a private file deleted by target.

Added a standard-library read-only harness/git_preflight.py and regression tests.
Optional config-relative git_repositories gives checkout ownership; no template
branch or machine-specific default is imposed. Extended the existing Git reference
with preflight usage, access and publication checkpoints, user-terminal auth repair,
and explicit recorded-versus-latest submodule decisions. The MIQA workspace config
registers its four relevant checkouts. No application or credential files changed.

Counts refer to independent chats, not suffixed session record IDs; generated
reports and prior proposals are excluded from recurrence claims. These sources
establish reported operations, not current remote history. Live Git inspection in
this review verified dirty checkouts, detached web HEAD and web gitlink drift;
network access was not retried after the recorded unchanged failures.

Deferred: credential setup (user terminal), divergent-history reconciliation
(requires authenticated fetch and current graph), moving all work to new worktrees,
replacing the existing bulk updater (separate user workflow), and automatically
counting root chat IDs in the evidence auditor. No commit, push or branch switch.

## Restricted configuration recovery — October 14, 2026 (America/Denver)

Reviewed configured recent journals plus four recent MIQA chats. Network Git
failures recur independently in template journals
`2026-10-10-878b200c6a764b9587cc7990681b60cb.jsonl:1` and
`2026-10-14-dc70910cf4344305ab49ef4a0e36eb9f.jsonl:1`.
Their recorded connector successes do not establish current CLI authentication.
No unchanged network failure was retried in this review.

The concrete restricted-configuration failure is chat
`01a13d67-1ae0-7b72-8107-29549ebd4d4f`, turns
`01a13d6b-0dc9-7682-9fb3-ae61584a4abe` and
`01a13d6c-3760-7533-b39f-8072a6e52648`: the executor reported private files
modified while the user's terminal reported clean and completed the rebase.
This establishes disagreement, not its cause. The later preview obstruction
in turn `01a13d70-8608-7ad2-9e56-4ed7d83d297d` supports leaving preserved
previews outside until all replay finishes. These turns are one session sequence,
not independent recurrence evidence.

Implemented a read-only `--repository NAME --target TARGET_REF` assessment in
`harness/git_preflight.py`: compare private path modes/object identities in HEAD,
index and target, fail closed on missing metadata/unmerged private paths, and
report target private-path presence without reading blobs or environment files.
Rename-source private classification is retained. Added independent Git/gh
readiness booleans while preserving the aggregate failure exit code.
The existing Git reference now explains local continuation, normal switch
conditions, worktree limits, and recovery tied to an actual context change.

Validation: 33 automated tests passed, development skill validation passed,
`git diff --check` passed, and live local `--target HEAD` inspection passed.
New private-transition fixtures use synthetic tree/index metadata without
creating working environment files. No private configuration read or edited;
no consumer repository, credentials, refs or remote history changed.

Deferred: live credential repair and history reconciliation (existing access
checkpoint still requires a real context/credential change), paused consumer
rebases, and application-specific startup/rate-limit fixes. The launcher-source
selection issue in chat `01a13d93-2b6c-7f71-a1ae-7a079cf33834` was already
resolved there through a local-filesystem fetch; it is not another auth failure.


## Deterministic guards and conversation identity — October 15, 2026 (America/Denver)

The explicit attribution preference comes from chat
`01a13216-c091-7db2-bf31-405c249eaf09`, turn
`01a13216-d5d7-71e1-b7f3-822dfc05b0f1`; the existing Git reference already
specified the required line. This review found no executable check. Added a shared
read-only checker and optional executable Git adapters for staged private filenames
and exact runtime-supplied attribution. The private-path rule already exists in
AGENTS.md and `git_preflight.private_path`; the new guard reuses that classification.
This is enforcement of existing rules, not a claim of repeated attribution failures.
No installer, hook activation, core.hooksPath change, or consumer rollout is included.

MIQA session records
`.harness/darius/sessions/2026-10-15-92100683a656445ca128d708bbe806e6.jsonl:1`
and `.harness/darius/sessions/2026-10-15-7d09837e6fe74d3bbf948b5ac5e5a89d.jsonl:1`
use suffixed IDs for one chat, `01a141f8-cb80-7893-bfb9-b6b5d771606a`.
Their insights differ, so they do not demonstrate an existing false recurrence.
A synthetic regression with matching insights showed the schema gap: distinct
phase IDs counted twice. Optional validated `conversation_id` now groups explicit
checkpoints, including a legacy root-ID record alongside new phase-ID records.
Existing IDs and source evidence remain unchanged; unknown legacy relationships
still require source review. No heuristic migration or historical rewriting occurs.

The README command baseline correction comes from the same chat, turn
`01a141f8-df42-7660-8bb6-2ac4f4c47d77`; follow-up chat
`01a14268-af64-7af2-ae30-8baf699c1961`, turn
`01a14268-bc9e-7a41-9a02-f859899e6cf3`, records a later correction.
The development skill now reads the existing command sequence first when wrapping
or automating it and identifies necessary deviations. This is a targeted semantic
guidance change; it is not a repository-specific command hook. The improvement
skill now connects source evidence, remaining gap, owner/scope, and the choice of
a deterministic check versus semantic guidance.

Validation: 47 automated tests passed, including real commits through symlinked
hooks, human/AI/empty-identity cases, blocked private metadata with preserved index,
both rename endpoints, and a scoped commit using Git's alternate index. Independent
review reproduced attribution hidden below a scissors marker; the commit adapter
now checks a conservative surviving message after Git comment/scissors cleanup.
Real commit tests reject default/custom scissors and commentChar=C removal, then
verify that an accepted attribution persists in Git history. Audit
regressions cover explicit checkpoint deduplication, mixed legacy/new identities,
invalid identity rejection, and unchanged suffix handling. Fixtures use synthetic
Git metadata without opening working environment files. No commit, publication,
network retry, scheduling, or global-link installation was performed. Shared source
edits are visible through existing live links; consumer files were not edited.

Deferred: hook activation in any checkout, connector/server enforcement, automatic
chat capture, legacy ID migration, credential repair, and history reconciliation.
