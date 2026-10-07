# Harness Template — Portable Across Projects

Copy this directory into any project to enable:
- Auto-save chat audits (conversations/)
- Daily workflow-improvement agent (harness/daily-audit.py)
- Cross-session audit references

Steps:
1. Copy `harness-template/` into your project root.
2. Update `harness-config.json` `project` and `workspace_root`.
3. Create `conversations/` directory.
4. Optionally symlink `conversations/` to a shared audit directory if you want project-spanning reads.

Audit policy (from harness-config):
Every chat writes an append-only `.jsonl` entry to `conversations/`. Any session can read all entries to detect patterns and propose skills/docs/agents.
