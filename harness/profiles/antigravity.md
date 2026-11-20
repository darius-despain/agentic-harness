# Antigravity profile

- Use the workspace's `.agent/rules/harness.md` bootstrap and current Antigravity editor/terminal/browser capabilities when available. If that rule is not loaded, explicitly read `AGENTS.md`.
- Read the relevant `.agents/skills/<workflow>/SKILL.md` as portable instructions. Native skill support varies by version; no Codex discovery path, `$skill` command, or OpenAI metadata is required.
- Before finishing non-trivial work, follow the shared `audit.py log` close-out in `CORE.md` whenever the project journal is configured and writable, including when no skill was loaded.
- Keep Antigravity's selected model, planning/fast mode and native review settings. Do not force Codex models, reasoning names, subagent APIs or configuration paths.
- Run the ordinary single-agent implement/verify loop. Create plans or native artifacts only when useful to the task or requested. Browser availability does not by itself verify a user flow.
- If delegation is explicitly requested, first establish available native controls and agree on a supported workflow; the existing Codex orchestration protocol is not a portable dispatch API. A self-review must never be described as independent.
- Keep subscription, account and MCP configuration in the tool's own private settings, outside shared harness files.

## Session-start model guidance

- **Fast-path (`< 50` lines, `<= 2` files, docs/config)**: `Gemini 3.8 Flash (Medium/Low)` in a single-agent pass without subagents (`GPT-OSS 120B (Medium)` optional fallback).
- **Repeatable everyday workhorse (default)**: `Gemini 4 Hydrogen (Medium)` or `Claude Sonnet 5.5 (Medium)` in the single-agent implement/verify loop for routine dev, TDD, bug fixes, and well-scoped tasks. Step up to `Gemini 4 Hydrogen (High)` only for localized complexity; prefer promoting to `Neon` over burning `Hydrogen (XHigh)`.
- **Default orchestrator / mid-heavy**: `Gemini 4 Neon (Medium/High)` (alt: `Claude Sonnet 5.5 (High)`) for multi-file features (`3+` files), cross-module refactors, non-trivial PR reviews, multi-track coordination, and 1st-line escalation from `Hydrogen`.
- **Heavy reserve / deep orchestrator**: `Gemini 4 Argon (Medium/High)` or `Claude Opus 5.5 (Medium/High)` for zero-context architecture, complex trade-off recommendations, concurrency/security invariants, or 2nd-line escalation after `Neon`.

## Opt-in orchestrator modes and thoroughness

Single-agent execution stays the default; use orchestrator mode only when delegation is explicitly requested:

- **Default Orchestrator (`Gemini 4 Neon`)**: Parent owns decomposition, scope, synthesis, and final sign-off; delegates scans/research/verification to `flash_lite`/`flash` and non-trivial implementation sub-tracks to `inherit` (`Neon`) or `pro`. Direct parent edits only for tiny glue (`< 20` lines).
- **Deep Orchestrator (`Gemini 4 Argon` / `Claude Opus 5.5`)**: Strict delegate-only mode for planning, trade-off analysis, recommendations, and final review. Exempt `CORE.md` housekeeping (`git status`, `harness-config.json` reads, `audit.py check/log`); delegate all broad scans, tests, and code edits to `flash_lite`, `flash`, and `pro` (**never** `inherit`).
- **Thoroughness (`fast` | `balanced` | `thorough`)**: Default silently to `balanced` (or infer from user cues / Fast vs Planning mode); ask once only when genuinely ambiguous or high-risk:
  - `fast`: brief plan, `flash` for straightforward edits (`pro`/`inherit` only if needed), 1 `flash_lite` test/diff check, 1 retry cycle.
  - `balanced` *(default)*: concise plan, `flash_lite`/`flash` for scans/research/tests, `pro` (from `Argon`/`Opus`) or `inherit`/`pro` (from `Neon`) for non-trivial tracks, 1 fresh independent `flash` verifier, up to 2 retry cycles.
  - `thorough`: parallel `flash` research + options/trade-offs/recommendation before edits, isolated scoped tracks (`pro` from `Argon`/`Opus`; `inherit`/`pro` from `Neon`), fresh independent `flash` verifier + fresh adversarial `pro` review, up to 2 retry cycles + 1 read-only advisory blueprint before pivoting/escalating.

## Native subagent delegation and budget tiers

`invoke_subagent` accepts only `flash_lite`, `flash`, `pro`, and `inherit` (it cannot target `Hydrogen`/`Neon`/`Argon` by name). Always set `Model` explicitly when delegating so heavy `Argon`/`Opus` parents never silently `inherit`:

- **Tier 1 (Mechanical / Verifier / Research / Browser)**: `Model="flash_lite"` strictly for scans, test runs, and log triage; `Model="flash"` for independent diff/verification checks, bounded `research`, and `browser` subagents. Enforce bounded scope and immediate exit.
- **Tier 2 (Implementer / Sub-Track)**: `Model="inherit"` is safe from `Hydrogen`/`Sonnet` parents (or `Neon` for complex sub-tracks); use `Model="pro"` when delegating non-trivial tracks from `Flash` or to avoid inheriting `Argon`/`Opus`.
- **Tier 3 (Advisory Escalation)**: On the 2nd consecutive failure on the same test/spec or zero-context design, use a fresh `Model="pro"` single-turn read-only/no-command blueprint (or escalate to `Neon`, then `Argon`/`Opus`); the driver reclaims control to apply and verify.

## Compatibility notes

- Never pass Codex model IDs (`gpt-6-*`), `temperature`, or `reasoning_effort` strings to `invoke_subagent` (`Model` accepts only `flash_lite`, `flash`, `inherit`, `pro`).
- Keep `harness/session.py`, `harness/profiles/codex.md`, and `harness/model_routing.py` untouched so switching back to `codex` remains seamless.
- Subagents report via `send_message` reactively without polling; self-review is never independent verification.
