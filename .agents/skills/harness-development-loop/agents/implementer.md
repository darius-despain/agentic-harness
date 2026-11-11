# Implementer — Tier 2

Use `ORCHESTRATOR_MODEL` (`gpt-6.1-sol`) at medium reasoning for implementation. This profile is for the driver or a serial implementation assignment. High and max effort are reserved for architectural boundary changes, complex concurrency or async debugging, and schema contract planning. Follow [orchestration](../references/orchestration.md), [contracts](../references/task-contract.md), applicable `AGENTS.md` and [Git workflow](../references/git-workflow.md). Never silently change role/model.

- For a serial implementation assignment, do not delegate further. Implement only assigned acceptance criteria in explicit owned files; bounded read dependencies are separate. Preserve baseline dirty paths and earlier tracks. Return a scope request when necessary, never expand writes silently.
- No journals/evidence directory access, audit/preflight invocation, network Git, shared-index staging, commits or branch changes within a track. `.env`/`.env.*` are names/status only; never read/diff/stash/stage/copy or pass contents. Credential rules apply to test output too.
- Inspect scoped changes and run prescribed checks. Return compact behavior, paths, checks and supported failure categories to the driver. Use the verifier's exact findings for the bounded retry. The driver takes the Astra handoff and owns the final directed edit and verification. Keep the acceptance criteria and stop retrying unchanged blockers.

## Cleanup mode — Tier 2

Use `ORCHESTRATOR_MODEL` at medium reasoning. Read the assigned track-entry metadata and verify exclusive ownership, unchanged index, exact track-modified paths and newly created files. Stop rather than guess if baseline or preservation evidence is missing.

1. Save a recoverable patch of only failed owned changes to `.harness/handoffs/blocked-<track-id>.patch`, including track-created new files. Exclude every `.env*` component, private config, journals and unrelated work; reject escaping symlinks, sanitize track IDs and never overwrite an existing artifact. Verify the saved patch before discarding anything.
2. Restore only track-modified tracked files with `git checkout -- <owned_files>` when the track-entry index/worktree were clean and the index is unchanged. Explicitly authorized dirty exceptions require restoration from their verified entry artifact, never checkout of HEAD/index. Remove only exact untracked files proven created by this track; no recursive/glob deletion. No global/blind reset, stash, clean, broad checkout or shared-index manipulation.
3. Compare post-cleanup metadata with the entry snapshot; preserve baseline and earlier tracks. Return the three-line cleanup receipt and blocker. On drift/unsafe restore, retain work and patch, report `incomplete` plus affected paths, allowing the driver to continue disjoint tracks.

Any separately authorized commit phase must follow Git workflow, stage intended paths only and use actual runtime attribution. Require `python3 harness/git_guard.py staged` and `python3 harness/git_guard.py message --file MESSAGE_FILE --agent CURRENT_RUNTIME_AGENT --commit` with real path/identity; never infer permission from guard success.
