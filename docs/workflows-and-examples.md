# Workflows & Examples: Getting the Most Out of the Harness

Once you have the harness cloned or installed (see [README.md](../README.md)), this guide walks through **when to use each workflow**, **what to type**, and **real sanitized examples** from our own sessions.

---

## The daily loop at a glance

1. **Build or fix something** → `harness-development-loop`
2. **Get a second pair of eyes before merging** → `harness-pr-review`
3. **Pause, switch tools, or hand off to tomorrow's chat** → `harness-handoff`
4. **Save what worked (or what tripped you up)** → `harness-session-evidence`
5. **Fix recurring workflow friction in the harness** → `harness-improvement-loop`

You don't have to use all five every day. Most teammates start with **development** + **handoff**, then add **PR review** and **session evidence** when working on larger changes.

---

## 1. Everyday coding, bug fixes, and docs (`harness-development-loop`)

**When to use it:**
- Implementing a feature, fixing a bug, refactoring, or updating documentation.
- You want the agent to inspect the repo first, make the smallest coherent change, run real tests/checks, and report what was actually verified vs. blocked.

**How it behaves:**
- **Small / doc edits** (`*.md`, templates, or `<= 2` files / `< 50` lines): runs in a fast single-agent pass with no subagent overhead.
- **Larger tasks:** stays in a focused implement → verify → diagnose → repeat loop using your tool's current model and settings.
- **Optional orchestrated mode:** only activates if you explicitly ask for `orchestrated mode` (and your tool supports it).

**Prompts to try:**
```text
Read AGENTS.md; use the claude-code profile.
Use harness-development-loop to fix the pagination bug in src/api/users.py and add a regression test.
```
```text
Read AGENTS.md; use the generic profile.
Follow .agents/skills/harness-development-loop/SKILL.md to update the setup docs and run git diff --check.
```
*(In tools with `$skill` support like Codex, you can also write `$harness-development-loop fix <behavior>`.)*

---

## 2. Independent PR or branch review (`harness-pr-review`)

**When to use it:**
- Before opening or merging a Pull Request.
- After pushing fixes to re-verify earlier review findings.
- When you want an adversarial check focused on regressions, missing edge cases, or unverified claims.

**What it does:**
- Pins the base/head commits and inspects the `merge-base..head` diff.
- Excludes secret-bearing `.env` / `.env.*` contents.
- Returns **Recommend approve**, **Recommend request changes**, or **Recommendation blocked** with exact file/line evidence and what was/wasn't tested.
- **Safe by default:** it does not post comments, approve, or merge on GitHub unless you explicitly ask it to.

**Prompts to try:**
```text
Use harness-pr-review to review my current branch against main. Focus on edge cases and test coverage.
```
```text
Re-review PR #42 after my latest commit. Check whether the previous findings are resolved.
```

---

## 3. Wrapping up or switching chats (`harness-handoff`)

**When to use it:**
- Your chat context is getting long or noisy and you want a clean fresh session.
- You're switching tools mid-task (for example, moving from Codex to Claude Code or Antigravity).
- You're stopping for the day and want to pick up seamlessly tomorrow.

**What it does:**
- Re-checks actual Git status, branch, and recent checks (doesn't trust stale memory).
- Saves a sanitized private brief under `.harness/handoffs/` (gitignored).
- Gives you a short, copy-pasteable **kickoff prompt** to paste into your next chat.

**Prompts to try:**
```text
Use harness-handoff to wrap up this session. Next session should finish the OAuth callback tests and open a PR.
```
```text
Prepare a handoff brief for the next chat; I'm switching to Antigravity for the UI debugging part.
```

---

## 4. Saving session outcomes & learnings (`harness-session-evidence`)

**When to use it:**
- At the end of a nontrivial session when you want a compact record of what changed, what passed, and any environment gotchas.
- When you want to check for recurring friction across sessions using `audit.py`.

**Real sanitized example (adapted from our own session logs):**
Here is what an actual logged session record looks like after applying the **Output Token Diet** (max 3 items per array, max 120 characters per string, zero secrets or raw transcripts):

```json
{
  "session_id": "6b456187-816a-4db1-a4dd-ceaa061ea4b3",
  "conversation_id": "6b456187-816a-4db1-a4dd-ceaa061ea4b3",
  "workflow_insights": [
    "Subagent delegation defaults Model to inherit; Tier 1 scanners should set flash_lite/flash explicitly.",
    "Sandbox mounts .git read-only and blocks remote proxy; git add/commit/push require terminal outside sandbox."
  ],
  "changes_made": [
    "Committed 1ecfde0 on main updating antigravity.md, orchestration.md, and docs/model-routing.md.",
    "Pushed 05c27b6..1ecfde0 main -> origin/main with Co-authored by: <agent> (AI).",
    "Kept harness/session.py, harness/profiles/codex.md, and harness/model_routing.py untouched."
  ],
  "validation": [
    "git_guard.py staged & message (--commit) passed; preflight readiness passed (git/gh available).",
    "python3 -m unittest discover -s tests -v (106/106 OK) & git diff --check passed prior to commit.",
    "Local HEAD, origin/main, and working tree verified clean after push."
  ],
  "blockers": [],
  "source_references": [
    "harness/profiles/antigravity.md:10-27",
    ".agents/skills/harness-development-loop/references/orchestration.md:3",
    "docs/model-routing.md:6"
  ],
  "kind": "session",
  "project": "agentic-harness"
}
```

**Prompts & commands to use it:**
```text
Use harness-session-evidence to save a sanitized record of what we changed and verified today.
```
Or from your terminal (requires `harness-config.json` in your project root; see [project-setup.md](project-setup.md)):
```bash
python3 harness/audit.py --config harness-config.json check
python3 harness/audit.py --config harness-config.json log --record /tmp/session-record.json
python3 harness/audit.py --config harness-config.json audit
```

---

## 5. Improving the harness from real friction (`harness-improvement-loop`)

**When to use it:**
- You notice the same friction across multiple sessions (for example: an agent keeps running an expensive command, a profile is missing a useful tip, or a check should be a script instead of a prompt rule).
- You want the agent to inspect recent evidence and propose or implement a targeted fix to the harness itself.

**Prompts to try:**
```text
Use harness-improvement-loop to audit our recent session logs and propose a targeted fix for the sandbox git friction we hit.
```

---

## Tips for getting the most out of your harness

- **Keep your first prompt crisp:** Start new sessions with `"Read AGENTS.md; use the <profile> profile. <goal>"`. That prevents the agent from guessing your tool or loading extra files.
- **Put personal preferences in `AGENTS.local.md`:** Copy [AGENTS.local.example.md](../AGENTS.local.example.md) to `AGENTS.local.md` (gitignored) for things like your preferred test runner, formatting style, or concise output preference—so you don't repeat yourself every chat.
- **Use the task pilot for multi-step features:** When starting a larger feature, ask the agent to read [harness/TASKS.md](../harness/TASKS.md) and plan using `templates/roadmap.md` and `templates/task.md`.
- **Keep secrets out of everything:** Never paste `.env` contents into prompts, session logs, or PR descriptions. Let `harness/git_guard.py staged` double-check your staged files before committing if you want extra peace of mind.
- **Share back what works:** If you discover a great prompt pattern or bridge for a new open-source/IDE tool, open a PR via [CONTRIBUTING.md](../CONTRIBUTING.md) so the whole team benefits.
