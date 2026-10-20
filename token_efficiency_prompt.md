# Prompt for Token Efficiency Refactor

You are an expert agentic software engineer. This repository (an agentic harness) contains many verbose Markdown files (`README.md`, `AGENTS.md`, `.agents/skills/**/*.md`, etc.) that consume too many tokens in agent sessions. Your objective is to refactor the harness documentation and instructions to be highly token-efficient without losing essential operational rules.

## Execution Plan

1. **Analyze and Audit:**
   - Scan `README.md`, `AGENTS.md`, and the files in `.agents/skills/`.
   - Identify wordy explanations, redundant rules, and historical context that do not serve as actionable instructions.

2. **Refactor Shared Instructions (`AGENTS.md` & `README.md`):**
   - Condense `AGENTS.md` and `README.md` into concise, bulleted lists.
   - Remove conversational filler and repetitive warnings.
   - Move detailed historical context and non-essential rationales into the `docs/` directory.

3. **Streamline Skill Files (`.agents/skills/**/*.md`):**
   - Refactor `SKILL.md` files to contain only the essential triggering conditions, steps, and expected outputs.
   - Keep Git and PR review instructions short and exact.

4. **Review and Verify:**
   - Ensure no critical guardrails, credential handling rules, or Git constraints have been lost.
   - Validate that the updated files maintain their original Markdown structure but with significantly reduced word counts.
   - Run the existing test suite (`python3 -m unittest discover -s tests -v`) to ensure nothing in the tooling was broken by the refactor.

Please execute this plan to dramatically reduce the token footprint of our harness!
