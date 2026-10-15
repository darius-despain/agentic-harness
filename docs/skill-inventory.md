# Captured skills — 2026-10-06

The original template contained no SKILL.md files. The inspected project and shared-conversations directories also contained no existing skill packages; the personal Codex skills directory contained only system-managed skills. The workspace SKILL.md search excluded dependency caches and third-party node_modules. Bundled/plugin skills are supplied by their owners and are not copied into this harness.

## Packaged workflows

| Package | Origin | Status |
| --- | --- | --- |
| harness-development-loop | User request in this chat to preserve an implement/test/fix/verify development loop; recent setup and Git sessions informed failure handling. | New reusable skill, ready for later use; no development run started. |
| harness-improvement-loop | Garmin project harness/automation-prompt.md and the matching automation-project copy. | Captured and adapted: config-relative paths, independent evidence, separate reports, no assumed scheduler or callback. |
| harness-pr-review | Explicit user request on 2026-10-15; existing sanitized Git and validation notes informed scope safeguards. | Portable skill plus dedicated reviewer prompt; launches through runtime delegation, with an explicit fallback. |
| harness-session-evidence | Original template audit_policy, Garmin conversations/AUDIT-README.md, and the implemented harness/audit.py. | Captured as a focused skill for persistence and handoff. |

The automation prompt's essential read/analyze/decide/change/record cycle is retained. Obsolete machine paths, the truncated curl prompt, and assumed OpenHands runtime calls are deliberately not execution instructions in the new skill. Original local files remain untouched.

## Mentioned but not implemented previously

Legacy daily-audit-log.jsonl mentions automated Garmin analytics/docs skills. Those entries propose creating skills, but no corresponding artifact or concrete reusable procedure was found. They remain candidate ideas, not missing skills to reconstruct from invented details. Generic “Generate skill/doc for” report strings are likewise proposals, not skill definitions.

The MIQA conversation_loop.ipynb is application code in a separate repository, not a harness skill. Project-specific third-party agent instructions are left with their projects.

## Verification and limitations

Skill frontmatter and scaffold checks validate packaging, not behavior. The CLI regression suite covers persistence and audit invariants. These new workflows have not yet been exercised on a real development task; iterate on them after use rather than treating their wording as proven operational behavior.
