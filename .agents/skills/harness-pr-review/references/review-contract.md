# Review contract

A finding describes a specific defect introduced by the change, a realistic supported trigger, and a meaningful consequence. Support it with a traced code path, safe reproducer, failing focused check, or violated explicit contract. Compare base behavior. Cite minimal relevant changed lines at the reviewed head, or old-side lines for deletion. Do not attach a pre-existing issue to an unrelated changed line.

| Priority | Meaning |
| --- | --- |
| P0 | Unconditional critical failure, such as unavoidable broad data loss. |
| P1 | High-impact defect on a realistic supported path; fix before merge. |
| P2 | Material defect under specific supported conditions; normal fix priority. |
| P3 | Demonstrated minor defect with limited impact. |

Do not report preferences, broad refactors, generic hardening, missing tests alone, or hypothetical risks as defects. Severity and merge recommendation are separate judgments: explain why a finding should block merge. Deduplicate root causes and state assumptions. If an unknown requirement controls the conclusion, ask a focused question or mark that conclusion blocked.

For each confirmed defect give the trigger, why the changed path fails, consequence, correction direction, and a useful regression case with expected behavior. Separate observed execution, static reasoning, CI evidence, and hypotheses. Do not claim full-suite validation from a direct script, dependency audit, or reviewed test file.

Lead the final response with a recommendation and reviewed SHA, followed by findings, relevant prior-finding dispositions, validation, and material limits. An approve recommendation can accompany no actionable defects in the inspected scope; it never implies exhaustive correctness or submission of a GitHub approval. Request changes requires verified defects that warrant blocking merge. Use blocked when essential evidence is unavailable, identifying the specific missing evidence. For a concise comment request use a paste-ready paragraph with the same evidence standards.
