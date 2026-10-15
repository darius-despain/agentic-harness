# Review contract

A finding must describe a specific defect introduced by the change, a realistic triggering condition, and a meaningful consequence. Support it with code paths, a reproducible example, a failing focused check, or an explicit violated contract. Verify against the base revision to distinguish existing defects. Cite a minimal relevant changed line range; for a deletion identify the old-side path and lines. Do not cite an unrelated changed line to attach a pre-existing issue.

Severity reflects impact and likelihood:

| Priority | Meaning |
| --- | --- |
| P0 | Unconditional critical failure requiring immediate attention, such as unavoidable broad data loss. |
| P1 | High-impact defect in a realistic supported path; fix before merge. |
| P2 | Material defect under specific supported conditions; normal fix priority. |
| P3 | Demonstrated minor defect with limited impact. |

Do not report style preferences, generic hardening, broad refactors, missing tests alone, or hypothetical risks as defects. Do not infer requirements without evidence. Explain the affected scenario in the finding; avoid unstated assumptions and unsupported certainty. Deduplicate multiple symptoms of the same root cause. Ask a focused question when intent is essential and unknown.

Keep findings concise and actionable. Include what triggers the bug, why the changed code fails, and what breaks. Suggest the correction direction without implementing it. Separate observed behavior, static reasoning, and unverified hypotheses. Report incomplete coverage even when no findings remain.
