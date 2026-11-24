# Antigravity profile

- Use the workspace's `.agent/rules/harness.md` bootstrap and current Antigravity editor/terminal/browser capabilities when available. If that rule is not loaded, explicitly read `AGENTS.md`.
- Read the relevant `.agents/skills/<workflow>/SKILL.md` as portable instructions. Native skill support varies by version; no Codex discovery path, `$skill` command, or OpenAI metadata is required.
- Before finishing non-trivial work, follow the shared `audit.py log` close-out in `CORE.md` whenever the project journal is configured and writable, including when no skill was loaded.
- Keep Antigravity's selected model, planning/fast mode and native review settings. Do not force Codex models, reasoning names, subagent APIs or configuration paths.
- Run the ordinary single-agent implement/verify loop. Create plans or native artifacts only when useful to the task or requested. Browser availability does not by itself verify a user flow.
- If delegation is explicitly requested, first establish available native controls and agree on a supported workflow; the existing Codex orchestration protocol is not a portable dispatch API. A self-review must never be described as independent.
- Keep subscription, account and MCP configuration in the tool's own private settings, outside shared harness files.

## Session-start model guidance

Antigravity splits quota across **two independent rolling pools**: all Gemini 4 models and `Orchestrator` modes share **one cost-weighted Gemini pool**, while `Claude Sonnet 5.5` and `Claude Opus 5.5` draw from a **separate non-Gemini pool**. Optimize total weighted tokens to first-try green and use cross-pool switching when one pool runs low. Avoid `Leaving Soon` / `Notice` models (`Gemini 3.8 Flash`, `Gemini 4 Argon`, `GPT-OSS 120B`) as defaults or fallbacks.

- **Tier 0 — Fast-path (`< 50` lines, `<= 2` files, docs/config)**: `Gemini 4 Hydrogen (Low)` (or `Medium` for nuanced prose/templates) in a single-agent pass without subagents; use `Claude Sonnet 5.5 (Low)` when conserving the Gemini pool.
- **Tier 1 — Repeatable everyday workhorse (default)**: `Gemini 4 Hydrogen (Medium)` (Gemini pool) or `Claude Sonnet 5.5 (Medium)` (separate Claude pool; strong coding value with zero Gemini burn) in the single-agent implement/verify loop for routine dev, TDD, bug fixes, and well-scoped tasks. Step up to `Gemini 4 Hydrogen (High)` only for localized complexity; prefer promoting to `Neon` over looping `Hydrogen (XHigh)` on multi-file refactors.
- **Tier 2 — Default orchestrator / mid-heavy (`3+` files / multi-step)**: Prefer `Orchestrator (Neon)` for structured multi-file features, cross-module refactors, and multi-step verify loops so Neon owns planning/review turns (`exit_plan_mode`) while a cheaper execution model applies edits. Use `Gemini 4 Neon (Medium/High)` (or `Claude Sonnet 5.5 (High)` in the Claude pool) for rapid interactive debugging, non-trivial PR reviews, exploration where plan-review gates add friction, and 1st-line escalation from `Hydrogen`.
- **Tier 3 — Heavy reserve / deep orchestrator**: Use `Claude Opus 5.5 (Medium/High)` (Claude pool—ideal for zero-context architecture, complex trade-off recommendations, stubborn conceptual bugs, or cross-family second opinions when Gemini stalls) or `Orchestrator (Carbon)` for large multi-step Gemini builds without monolithic Carbon burn. Reserve raw `Gemini 4 Carbon (High)` or `Gemini 4 Neon (XHigh)` for single-pass deep audits, proofs, concurrency/security invariants, or 2nd-line escalation after `Neon`.

## Opt-in orchestrator modes and thoroughness

Single-agent execution stays the default; use orchestrator mode only when delegation is explicitly requested:

- **Default Orchestrator (`Orchestrator (Neon)` / `Gemini 4 Neon`)**: Parent owns decomposition, scope, synthesis, and final sign-off (under `Orchestrator (Neon)`, Neon handles planning/review turns while a cheaper executor runs edits); delegates scans/research/verification to `flash_lite`/`flash` and non-trivial implementation sub-tracks to `inherit` (only when parent is `Neon (Medium)`) or `pro`. Direct parent edits only for tiny glue (`< 20` lines) when running standalone `Neon`.
- **Deep Orchestrator (`Orchestrator (Carbon)` / `Gemini 4 Carbon` / `Claude Opus 5.5`)**: Strict delegate-only mode for planning, trade-off analysis, recommendations, and final review (or `exit_plan_mode` handoffs under `Orchestrator (Carbon)`). Exempt `CORE.md` housekeeping (`git status`, `harness-config.json` reads, `audit.py check/log`); delegate all broad scans, tests, and code edits to `flash_lite`, `flash`, and `pro` (**never** `inherit`).
- **Thoroughness (`fast` | `balanced` | `thorough`)**: Default silently to `balanced` (or infer from user cues / Fast vs Planning mode); ask once only when genuinely ambiguous or high-risk:
  - `fast`: brief plan, `flash` for straightforward edits (`pro`/`inherit` only if needed), 1 `flash_lite` test check (use `flash` for semantic diff checks), 1 retry cycle.
  - `balanced` *(default)*: concise plan, `flash_lite`/`flash` for scans/research/tests, `pro` (from `Orchestrator (Carbon)`/`Carbon`/`Opus`) or `inherit`/`pro` (from `Neon (Medium)`) for non-trivial tracks, 1 fresh independent `flash` verifier, up to 2 retry cycles.
  - `thorough`: parallel `flash` research + options/trade-offs/recommendation before edits, isolated scoped tracks (`pro` from `Orchestrator (Carbon)`/`Carbon`/`Opus`; `inherit`/`pro` from `Neon (Medium)`), fresh independent `flash` verifier + fresh adversarial `pro` review, up to 2 retry cycles + 1 read-only advisory blueprint before pivoting/escalating.

## Native subagent delegation and budget tiers

`invoke_subagent` accepts only `flash_lite`, `flash`, `pro`, and `inherit` (it cannot target `Hydrogen`/`Neon`/`Carbon`/`Opus` by name or cross model families directly). **Always set `Model` explicitly** when delegating so `Orchestrator (Neon/Carbon)`, `Neon`, `Carbon`, or `Opus 5.5` parents never silently `inherit` onto mechanical subtasks:

- **Tier 1a (Mechanical / Scanner / Test Runner / Log Triage)**: `Model="flash_lite"` strictly for scans, test runs, and log triage. Do not use `flash_lite` for semantic diff or security review.
- **Tier 1b (Verifier / Research / Browser)**: `Model="flash"` for routine independent diff/verification checks, bounded `research`, and `browser` subagents. Enforce bounded scope and immediate exit.
- **Tier 2 (Implementer / Adversarial Reviewer / Sub-Track)**: `Model="inherit"` **only** when the parent is an everyday workhorse (`Hydrogen (Medium)`, `Sonnet 5.5 (Medium)`, or `Neon (Medium)` for complex sub-tracks); use `Model="pro"` for isolated non-trivial tracks, adversarial diff/PR reviews, delegating up from `Low` fast-path parents, or avoiding inheriting `Orchestrator (Neon/Carbon)`, `Carbon`, or `Opus 5.5`.
- **Tier 3 (Advisory Escalation)**: On the 2nd consecutive failure on the same test/spec or zero-context design, use a fresh `Model="pro"` single-turn read-only/no-command blueprint—or switch the top-level planning turn to the **other quota pool** (`Claude Opus 5.5` ↔ `Gemini 4 Carbon`/`Neon`) for cross-family review; the driver reclaims control to apply and verify.

## Compatibility notes

- Never pass Codex model IDs (`gpt-6-*`), `temperature`, or `reasoning_effort` strings to `invoke_subagent` (`Model` accepts only `flash_lite`, `flash`, `inherit`, `pro`).
- Keep `harness/session.py`, `harness/profiles/codex.md`, and `harness/model_routing.py` untouched so switching back to `codex` remains seamless.
- Subagents report via `send_message` reactively without polling; self-review is never independent verification.
