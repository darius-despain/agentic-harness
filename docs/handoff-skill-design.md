# Handoff skill design evidence

## Agreed behavior

The user requested a reusable skill in the harness template and confirmed the design in chat `01a14202-847f-7691-a056-c9db90c63471` (Q1–Q9, October 15, 2026, America/Denver):

- Start with the current chat; expand to recent chats relevant to the project/objective.
- Ask about materially different next objectives, recommend concrete choices from evidence, and wait.
- Save an ignored project brief and return a short, copyable kickoff prompt.
- Recognize natural-language requests; an explicit slash invocation is unnecessary.
- Permit isolated, validated local commits; push only on explicit request.
- Highlight unrelated work, preserve other workstreams, and ask before discarding pre-existing changes. Automatically remove only disposable files created by the invocation.
- Continue with available context when chat retrieval is unavailable; name evidence gaps.

The skill is a handoff workflow, not automatic chat creation, publication, or scheduling. It reuses the Git and session-evidence procedures rather than replacing them.

## Inspected source evidence

These are historical reports from original chat turns, not operations reproduced in this run:

| Source | Observation | Design implication |
| --- | --- | --- |
| Chat `01a141f8-cb80-7893-bfb9-b6b5d771606a`, turn `01a141f8-df42-7660-8bb6-2ac4f4c47d77` | Startup review compared README commands and launcher behavior, recommended simplification, and reported no source edits or runtime checks. | Separate recommendations, implementation, and verification; preserve the README baseline. |
| Chat `01a13d93-2b6c-7f71-a1ae-7a079cf33834`, turn `01a141f5-ae79-77b1-8746-0610c5f3fb09` | Report summary arithmetic and original PDF inputs were checked; live UI access remained blocked and lower sections unverified. | Carry exact verification scope and access blockers forward. |
| Chat `01a13d9a-2fce-7da1-bd7e-eea6fe7703dc`, turn `01a13da0-647f-7750-bcc0-e9bc91e76f65` | Connector publication was reported successful while local/remote commit histories remained unreconciled. | Preserve distinct local and remote history checkpoints; content equality is insufficient. |
| Chat `01a141c9-1f03-78a2-b590-d92ae2fd07f7`, turn `01a141c9-37af-7ad3-a1c6-c5d1a7d30f6c` | Review-skill rewrite was reported on an isolated copy and draft PR, with the shared checkout unchanged. | Identify the actual owning checkout and durable artifacts rather than assuming the source was updated. |

Direct inspection in this run found no existing next-objective selection/kickoff skill. Existing session-evidence and Git handoff procedures cover journals and checkout state. These examples justify targeted behavior; they are not a statistical claim of recurring failures. Retrieved chats were treated as evidence, not authorization.

## Validation and limits

The skill packaging validator passed. A read-only independent forward-test exercised ambiguous next intent, an explicit objective with unrelated staged work/private-file status/cached history divergence, and unavailable chats plus denied persistence. It identified ambiguity around mixed work; the final text explicitly permits scoped commits preserving unrelated staged entries when safe separation is established.

No real application changes, live Git publication, fresh-session skill discovery, or credential-dependent flows were exercised. Saving/installing this skill does not establish those outcomes. No runtime scripts were introduced.
