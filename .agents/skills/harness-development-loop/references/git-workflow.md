# Git workflow

Use this procedure when work changes branches, commits or publishes code, or prepares a checkout for another session. Keep the user's chosen branch and authorization; do not make a pull request, merge, or push solely because an edit is complete.

## Configured preflight

When `harness-config.json` declares `git_repositories` and `harness/git_preflight.py` is available, run the read-only inventory before Git work:

```bash
python3 harness/git_preflight.py --config harness-config.json
```

Each named entry has a config-relative `path` and optional `origin` identity such as `github.com/owner/repository`. Register separate checkouts and worktrees independently; a standalone clone is not updated by a parent's submodule commands. Keep machine-specific registry paths in the local config. Branches are discovered live, never pinned from a journal. An entry missing from the registry still requires manual inspection.

The inventory reports staged/unstaged/untracked filenames, private configuration names, detached HEADs, cached upstream counts and recursive gitlink drift. It never reads environment-file contents, fetches, switches branches, stages or changes configuration. Exit zero means the configured top-level inspections completed and origins matched; inspect dirty paths and every submodule result before acting. A clean parent, missing upstream, unavailable submodule or cached equality cannot establish a clean, synchronized handoff. The inventory does not detect concurrent chat ownership; check active chats and worktrees separately before mutation.

Remote access is untested by default. Before network Git work in a fresh session, read prior access checkpoints and explicitly invoke one readiness check:

```bash
python3 harness/git_preflight.py --config harness-config.json --repository NAME --readiness
```

Replace NAME with the intended configured checkout. This captures and suppresses raw diagnostics, disables interactive prompts, and independently checks `gh` account/API access and Git repository read access with timeouts. Any required failure returns nonzero. Connector access and push permission remain untested; no refs are fetched. `--probe-remote` is the narrower Git-only alternative, not an additional readiness step. Do not repeat a known failed check until an actual credential or executor-context change; a new turn alone is not such a change. Record terminal success separately from executor results. Inspect active helper/config presence and override names without values, and do not prescribe another login solely because terminal access succeeds while executor access fails. Installing this workflow does not invoke startup checks automatically.

## Establish the repository and preserve work

Run inspection from the requested source directory using an explicit working directory or `git -C`. Check `git rev-parse --show-toplevel`, `git status --short --branch`, `git branch --show-current`, and the intended remote. Do not print credential-bearing remote URLs; report repository identity without embedded credentials. In a parent workspace containing several repositories, identify which repository owns each changed file. A submodule commit and its parent gitlink update are separate changes.

If the source is not a checkout, report that before editing and choose a durable checkout when authorized. A temporary upload repository does not turn the source into a checkout. If staging is necessary, record both paths and which one future sessions should use; retain the original files. Do not initialize over an existing repository or overwrite a populated directory to repair this.

Record existing staged, unstaged, and untracked paths before making changes. When submodules are present, inspect `git submodule status --recursive` and `git submodule foreach --recursive 'git status --short --branch'`. A clean parent status alone is insufficient. Use status and filenames only for restricted `.env` and `.env.*` paths; exclude them from diffs, patches, stashes, staging, and connector payloads.

Before changing a shared checkout's branch, check for another active session using it. Prefer an isolated worktree for independent work where practical; inspect attached worktrees before creating one. Do not copy private configuration into it. For a requested branch, establish whether it already exists locally or remotely before creating a replacement. Fetch when access permits; record when refs are only locally cached. Do not pull, rebase, or reset a dirty checkout to resolve uncertainty.

## Commit only the intended change

For AI-assisted changes, append `Co-authored by: <active agent name> (AI)` to the commit message body and each pull request (PR) or merge request (MR) description. Resolve the name from the current session/runtime identity, not a fixed template value or Git author. Preserve existing attribution and verify the line is present before committing or submitting the PR/MR; do not invent an agent identity or email address.

Run relevant validation and inspect the intended diff with explicit safe paths. Stage explicit paths, then check the entire staged path list for pre-existing staged work before committing. If unrelated work is already staged, use a scoped commit that preserves it, or leave the commit pending with a concrete blocker; do not silently include or unstage it. Do not use broad staging that could capture private configuration, journals, or unrelated changes. Record the resulting local commit and branch.

## Publish and reconcile history

Check connector access and local Git access separately. On failure, inspect credential source and environment override names without exposing values; do not repeat an unchanged failing operation. Use user-run authentication commands when needed. Connector publication is a fallback only when it supports the authorized change without retrieving secrets.

Persist an access checkpoint in the session record: transport (Git HTTPS/SSH, `gh`, connector), repository identity, observed success/failure, credential source presence or override names, and the next required change. Read that checkpoint before retrying an unchanged failure in another turn or chat. Do not log credential values or raw diagnostics. User reports of terminal access and agent-executor access are distinct evidence.

For GitHub HTTPS recovery, give the user commands for their own terminal; authenticate `gh` and configure the Git helper separately. Do not retrieve or paste tokens into chat:

```bash
cd /absolute/path/to/the/checkout
gh auth login --hostname github.com --git-protocol https --web &&
    gh auth setup-git --hostname github.com &&
    git ls-remote --exit-code origin HEAD >/dev/null
```

Substitute the observed checkout path in the delivered command. The final command should succeed without printing credentials. Ask for success/failure only, then recheck once in the agent executor. Browser/device-login prompts must remain in the user's terminal. See the official [login](https://cli.github.com/manual/gh_auth_login) and [Git helper](https://cli.github.com/manual/gh_auth_setup-git) documentation. Keep an existing working SSH transport unless the user asks to change it; HTTPS helper setup does not repair SSH access.

Before publication, establish the current remote branch tip and intended base. If another session advanced it, inspect those commits before proceeding; do not overwrite them or force-push to make history match. Push the explicit intended branch through Git when it works, then verify the remote branch points to the intended commit. If verification fails, report publication as unverified rather than retrying blindly.

For connector publication, preserve remote parent history and submit only intended files. Use an expected-head check or equivalent conflict protection if supported. If the tool cannot protect against concurrent updates, recheck the tip immediately before mutation and verify afterward; stop on conflicting changes. Compare the remote result with the intended paths and content, and ensure unrelated remote changes survived.

Matching file content or tree hashes does not prove matching commit history. Record the local commit, remote commit, and whether Git has fetched the remote commit. If they differ, report that publication succeeded but local history remains unreconciled. When Git access is restored, fetch and inspect the graph and unpublished local commits before choosing a merge, rebase, or replacement. Do not automatically reset or replay an already published change. Preserve the local commit until reconciliation is verified.

After connector publication with divergent history, persist a `git_handoff` object in the session record with checkout path, branch, local commit, remote commit, remote parent, intended paths, remote commit fetched (true/false), reconciliation status, and next action. Include the PR URL when applicable. This is a checkpoint, not authorization to reset, rebase or republish. Before later publication on that branch, inspect this checkpoint and the current heads so an already published change is not submitted again as a new commit. Use normal Git fetch/graph inspection for reconciliation once access works; matching blobs or hand-built commit objects are not a general repair strategy.

For submodule updates, decide explicitly between restoring the parent's recorded gitlinks and advancing child repos to newer remote commits. `git submodule update --init --recursive` restores the recorded revision by default; `--remote` selects a remote-tracking revision and can dirty the parent gitlink. Verify every child's dirty paths and unpublished commits before either operation. Do not run bootstrap snippets that switch the parent to main, create branches in all children or hide errors with `|| true` in an active development checkout. Use the owning checkout from the registry and preserve its current branch. See [Git's submodule documentation](https://git-scm.com/docs/git-submodule).

## Prepare a handoff

A request to leave a PR open and return to main does not authorize discarding other work. Inventory remaining changes and unpublished commits before switching. Preserve useful nonsecret work in a durable branch or patch and report its location. Restore or discard only changes covered by the user's authorization.

Submodule pointers can differ from the parent commit while their files are clean. Before restoring recorded pointers, check each affected submodule for dirty files and local commits absent from known remote refs; disclose when refs are stale. Update only the authorized submodules, without `--force`. Recheck recursively afterward.

If private configuration blocks cleanup, complete independent safe steps, then provide copy-and-paste commands for the user's own terminal to back up the exact affected files privately and perform the authorized restore. Do not read or copy those files through agent tools, and do not request their contents. Explain that a clean checkout may need local configuration restored before the app runs.

Verify the final parent branch, staged/unstaged/untracked status, submodule status, and relation to remote history. When restricted files make agent status unreliable, ask for status-only verification from the user's terminal. State whether main matches a freshly fetched remote or only cached refs. A handoff should identify checkout path, branch, local/remote commits when relevant, PR state, preserved work, and any pending reconciliation or configuration step. Never report a clean or synchronized checkout from a parent-only status or content-only comparison.
