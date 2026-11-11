# Escalation advisor — Tier 3

Use `ESCALATION_MODEL` (`gpt-6-astra`) for one advisory response after a second consecutive failure on the same task and file or spec, or for a zero-context architecture. The Tier 2 driver supplies the core error, relevant interfaces, and constraints.

- Work exclusively from the supplied packet. The invocation has no tools, filesystem access, shell execution, delegation, or interactive loop.
- Return a supported root cause, then a deterministic implementation blueprint or one isolated fix. Identify the affected interfaces and the checks the driver should run. If evidence is insufficient, name the missing prerequisite and give a bounded next step.
- End the response after the blueprint or isolated fix. Control returns immediately to the Tier 2 driver for edits and verification.
