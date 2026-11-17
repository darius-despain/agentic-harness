# Antigravity profile

- Use the workspace's `.agent/rules/harness.md` bootstrap and current Antigravity editor/terminal/browser capabilities when available. If that rule is not loaded, explicitly read `AGENTS.md`.
- Read the relevant `.agents/skills/<workflow>/SKILL.md` as portable instructions. Native skill support varies by version; no Codex discovery path, `$skill` command, or OpenAI metadata is required.
- Before finishing non-trivial work, follow the shared `audit.py log` close-out in `CORE.md` whenever the project journal is configured and writable, including when no skill was loaded.
- Keep Antigravity's selected model, planning/fast mode and native review settings. Do not force Codex models, reasoning names, subagent APIs or configuration paths.
- Run the ordinary single-agent implement/verify loop. Create plans or native artifacts only when useful to the task or requested. Browser availability does not by itself verify a user flow.
- If delegation is explicitly requested, first establish available native controls and agree on a supported workflow; the existing Codex orchestration protocol is not a portable dispatch API. A self-review must never be described as independent.
- Keep subscription, account and MCP configuration in the tool's own private settings, outside shared harness files.

## Session-start model guidance

- **Everyday workhorse / normal development / TDD / bug fixes (default)**: `Gemini 4 Hydrogen (Medium)` or `Claude Sonnet 5.5 (Medium)`. `Gemini 4 Hydrogen` shares the fast-replenishing daily Gemini quota pool; step up to `Gemini 4 Hydrogen (High)`/`(XHigh)` or `Claude Sonnet 5.5 (High)` before touching weekly Argon quota.
- **Heavy orchestration / architecture / escalation (reserve)**: `Orchestrator (Argon)`, `Gemini 4 Argon (Medium/High)`, or `Claude Opus 5.5 (Medium/High)`. `Gemini 4 Argon` and `Orchestrator (Argon)` draw from a weekly reset pool; prefer `Orchestrator (Argon)` for multi-step orchestrated work so Argon handles planning/review turns (`exit_plan_mode`) while a cheaper execution model runs the edits, and reserve raw `Gemini 4 Argon` or `Claude Opus 5.5` for zero-context architecture or stubborn conceptual bugs.
- **Fast-path / docs / minor edits (< 50 lines, <= 2 files)**: `Gemini 3.8 Flash (Medium)` (or `Low`) in a single-agent pass without subagents. `GPT-OSS 120B (Medium)` is an optional fallback when conserving primary Gemini/Claude pools.

## Native subagent delegation and budget tiers

Default to the single-agent loop; when delegation is explicitly requested, use `invoke_subagent` instead of Codex APIs and always set `Model` explicitly (`inherit` is the default and will copy a heavy `Argon`/`Opus` parent if omitted):

- **Tier 1 (Mechanical / Verifier / Scanner / Investigator / Browser)**: `Model="flash_lite"` for high-volume or trivial read-only searches, file/symbol scans, test runs, and log triage; `Model="flash"` for independent diff/verification checks, bounded `research` investigations, and all `browser` subagent tasks. Enforce bounded scope and immediate exit via prompt.
- **Tier 2 (Implementer / Complex Sub-Track)**: `Model="inherit"` when the parent is on an everyday workhorse (`Gemini 4 Hydrogen (Medium)` or `Claude Sonnet 5.5 (Medium)`), or `Model="pro"` when delegating an isolated nontrivial implementation sub-track from a Flash parent or avoiding inheriting an `Argon`/`Opus` parent.
- **Tier 3 (Advisory Escalation)**: On the 2nd consecutive failure on the same test/spec or zero-context design, `Model="pro"` with prompt-enforced single-turn, read-only/no-command blueprint mode (or an `Orchestrator (Argon)` / `Gemini 4 Argon` / `Claude Opus 5.5` planning turn); the driver reclaims control to apply and verify.

## Compatibility notes

- Never pass Codex model IDs (`gpt-6-*`), `temperature`, or `reasoning_effort` strings to `invoke_subagent` (`Model` accepts only `flash_lite`, `flash`, `inherit`, `pro`).
- Keep `harness/session.py`, `harness/profiles/codex.md`, and `harness/model_routing.py` untouched so switching back to `codex` remains seamless.
- Subagents report via `send_message` reactively without polling; self-review is never independent verification.
