# Git workflow

Use for branches, commits, publication and checkout handoff. Preserve user branch/authorization; completion alone grants no push, PR or merge permission.

## Configured preflight

- With configured `git_repositories` and `harness/git_preflight.py`, run read-only inventory before Git work:

```bash
python3 harness/git_preflight.py --config harness-config.json
```

- Entries use config-relative `path` and optional host/owner/repository `origin`. Register independent checkouts/worktrees separately; manually inspect unregistered targets. Discover branches live; keep machine paths local.
- Inventory reports filenames, private path names, detached heads, cached upstream counts and recursive gitlink drift; never reads environment contents or changes state. Zero means top-level inspection/origin matching, not clean/authenticated/synchronized state. Inspect every submodule and check active chats/worktrees before mutation.
- **Local-First Default:** Do NOT run `git_preflight.py ... --readiness`, `git fetch`, `gh` API probes, or MCP GitHub connector searches unless the user explicitly asks to `fetch`, `pull`, `push`, `sync`, `open a PR`, or `switch branches against remote`.
- For local implementation/documentation tasks, run ONLY fast local checks on the target repository (`git status --short --branch`).
- Before fresh-session network Git, read access checkpoints, then run:

```bash
python3 harness/git_preflight.py --config harness-config.json --repository NAME --readiness
```

- Replace `NAME` with the configured target. Readiness independently checks gh account/API and Git repository reads, suppressing diagnostics/prompts with timeouts. No refs fetched; connector/push permission untested. `--probe-remote` is a narrower alternative, not an extra step.
- Use `git_read_available` and `gh_api_available` independently despite aggregate failure. Local status/commits/metadata/filesystem fetches need no network auth. Failed network checks do not block local work.
- Retry known failure only after actual credential/executor-context change, never merely a new turn. Record user-terminal versus executor access separately. Inspect helper/config presence and override names without values; terminal success does not justify another login. Installation runs no startup check.

## Establish the repository and preserve work

- Use explicit cwd or `git -C`; inspect `rev-parse --show-toplevel`, `status --short --branch`, `branch --show-current` and remote identity without embedded credentials. Identify each file's owning repo; child commits and parent gitlinks are separate.
- If source is not a checkout, report it and choose an authorized durable checkout; staging uploads do not repair source ownership. Record source/staging paths, retain originals; never initialize over a repo or overwrite populated directories.
- Record existing staged/unstaged/untracked paths. **Lazy Submodule Inspection:** Do NOT run recursive submodule history/ancestry comparisons or inspect sibling checkouts unless the user's task explicitly targets a submodule or gitlink update. Private `.env`/`.env.*` paths: status/names only; exclude from reads/diffs/patches/stashes/staging/connector payloads.
- Before branch changes, check active sessions/checkout ownership. Prefer suitable isolated worktrees; inspect attached worktrees first, never copy private config. Check requested branch locally/remotely before creating replacements; fetch when available, label cached refs. Never pull/rebase/reset dirty work to resolve uncertainty.

## Recover from restricted configuration status

- Modified `.env` status alone establishes neither content changes nor a sandbox defect. Record terminal/executor disagreement as unverified. Continue safe edits, explicit staging/commits and checks without private files. Inspect index filenames; pre-staged private paths block ordinary whole-index commits.
- For an authorized switch to a locally available target:

```bash
python3 harness/git_preflight.py --config harness-config.json --repository NAME --target TARGET_REF
```

- Read `private_transition`, not exit zero. HEAD/index/target private names, object IDs and modes are compared without blobs/working files.
- Only `assessment=complete` plus `private_configuration_unchanged=true` permits considering a normal non-force switch with `--no-recurse-submodules`, after unrelated changes, active operations and ownership checks. Verify target still equals `target_commit` immediately before switching; reassess if moved. Preserve Git refusal. This proves neither cleanliness/concurrency safety nor safe rebase intermediate commits.
- If metadata differs/unmerged/unavailable, leave private config intact. Prefer an existing suitable checkout or worktree only at a target with `target_tracks_private_configuration=false`; otherwise creation materializes private files. Assess other submodules separately; use nonsecret test fixtures, disclose pending credential checks.
- Never silence status through assume-unchanged, skip-worktree, index-only untracking, ignores, force switches, auto-stash/reset/clean or permission changes. Ignores do not protect tracked files from target deletion.
- If private modification/rebase is unavoidable, finish independent work and supply exact user-terminal commands for that step. Preserve nonsecret obstructions outside checkout throughout the operation; restoring between rebases may obstruct replay.

## Commit only the intended change

- Append `Co-authored by: <active agent name> (AI)` to every AI commit and PR/MR body. Resolve current runtime identity, never fixed templates/Git author/invented identity/email; preserve existing attribution and verify before submission.
- When available, run from owning checkout:

```bash
python3 harness/git_guard.py staged
python3 harness/git_guard.py message --file MESSAGE_FILE --agent CURRENT_RUNTIME_AGENT --commit
```

- Substitute real message path/identity; omit `--commit` for PR/MR bodies. Commit mode requires attribution surviving comment/scissors cleanup. Checks are read-only and preserve index on failure.
- [Optional guards](../../../../README.md#optional-local-git-guards) are not installed automatically. Preserve hooks/`core.hooksPath`. Adapter requires supplied `HARNESS_AI_AGENT`; absent permits human commits, empty fails. Hooks cannot detect AI or cover connectors/PRs; check bodies explicitly.
- Run relevant validation; inspect safe explicit-path diff. Stage only intended paths; inspect the entire staged filename list. Preserve unrelated staged work with scoped commits or report blocker; never silently include/unstage it. Avoid broad staging/private config/journals. Record commit/branch.

## Publish and reconcile history

- Check connector and local Git access separately. On failure inspect credential-source presence/override names, never values/raw auth diagnostics; no unchanged retry. Connector fallback must support authorized work without retrieving secrets.
- Journal access checkpoint: transport, repo identity, success/failure, credential-source presence/override names, next required change. Read before later retries; distinguish user-terminal/executor observations.
- Recovery must address demonstrated cause: remove a known-stale override only for one child command (`env -u VARIABLE_NAME ...`), then recheck once. Presence alone proves no fault. Never dump/edit environment files.
- For indicated sandbox network denial use normal escalation; changed executor context does not prove fixed auth. If helper/keyring remains unavailable, stop that route; use authorized connector/user-terminal recovery. Never automatically replace working transport, extract tokens, install credential bridges or change global auth.
- For GitHub HTTPS, supply these in the user's terminal with observed absolute checkout; request success/failure only, then recheck executor once. Keep browser/device prompts there. Preserve working SSH unless user requests change; HTTPS setup does not repair SSH.

```bash
cd /absolute/path/to/the/checkout
gh auth login --hostname github.com --git-protocol https --web &&
    gh auth setup-git --hostname github.com &&
    git ls-remote --exit-code origin HEAD >/dev/null
```

- Before publication establish live remote branch/base; inspect concurrent advances. Never overwrite/force-push to match history. Push explicit intended branch via working Git; verify remote equals intended commit. Failed verification means unverified, not blind retry.
- Connectors: preserve remote parents, submit intended files, use expected-head protection. If unavailable, recheck tip immediately before mutation and afterward; stop on conflicts. Verify paths/content and survival of unrelated changes.
- Equal content/trees do not prove history equality. Record local/remote commits and whether remote is fetched. Divergence means published but unreconciled; preserve local commit. When Git recovers, fetch/inspect graph and unpublished commits before choosing merge/rebase/replacement. No automatic reset/replay of published work; matching blobs/hand-built commits are not general reconciliation.
- After divergent connector publication, journal `git_handoff`: checkout, branch, local/remote commits, remote parent, intended paths, fetched boolean, reconciliation status/next action, PR URL. Before later publication inspect checkpoint/current heads to prevent duplicate submission. Checkpoint grants no reset/rebase/republish authority.
- Submodules: explicitly choose recorded gitlinks (`update --init --recursive`) versus remote advancement (`--remote`, potentially dirtying parent). First inspect each child's changes/unpublished commits. Never bootstrap-switch parent to main, create branches in every child or hide failures via `|| true`; use registered owning checkout/current branch.

## Prepare a handoff

- Returning to main with an open PR grants no discard permission. Inventory changes/unpublished commits; preserve useful nonsecret work in durable branch/patch and report path. Restore/discard only authorized changes.
- Before restoring gitlinks, inspect children for dirty files/local commits absent from known remote refs; label stale refs. Update only authorized children without force; recheck recursively.
- Private cleanup blockers: finish safe work, then give exact user-terminal commands to privately back up affected files and perform authorized restore. Never agent-read/copy/request contents. Explain local config may need restoring before app runs.
- Verify final branch, full status, recursive submodules and remote-history relation. If restricted files make agent status unreliable, request terminal status-only verification. Label freshly fetched versus cached main. Report checkout, branch, relevant local/remote commits, PR state, preserved work, pending reconciliation/config. Parent cleanliness/content equality alone never proves clean synchronized handoff.
