# Review modes

Read the relevant mode; combine modes when the user's request calls for it.

## Initial or adversarial review

Review the full allowed diff and relevant callers, not just the author's explanation. Give an approve/request-changes recommendation with evidence. Adversarial means challenging assumptions and exercising realistic counterexamples; it does not set a rejection quota. Evaluate unknown, missing, conflicting, and legacy inputs when the changed contract makes them relevant. A test's existence is not proof it covers the failure path.

## Re-review after edits

Resolve the latest head rather than reusing the earlier patch. Recover previous findings, their reviewed SHA, and the author's claimed fixes from supplied context or relevant discussion. For each finding report resolved, unresolved, partially resolved, or unverifiable and cite current evidence. Compare the intervening changes and review remaining relevant behavior for additional defects. Distinguish newly found bugs from regressions introduced by the fix. If earlier context cannot be recovered, disclose that this is a fresh review and cannot certify resolution of all prior findings.

When the user asks for tests-only follow-up, that authorizes test changes within the requested scope. Keep production fixes out of that change. Establish the target revision; verify the patch applies there and, where execution is possible, demonstrates the reported failure. Report static checks or direct reproducers separately from running the test suite. Preparation of a regression case during review does not itself authorize editing or publishing tests.

## Related PR or pasted finding

Verify the cited head and current head for each PR independently. Trace the data from producer through normalization and persistence to consumers; inspect duplicated implementations where relevant. Determine whether the claimed fix changes the actual failing path, and whether the new issue is the original defect, a separate related defect, or unsupported. Attribute findings to the PR that introduces them and distinguish pre-existing issues. A downstream fix does not establish an upstream classifier is fixed, or vice versa.

If evidence changes an earlier recommendation, qualify it explicitly with the affected revision and reason. Do not carry a recommendation across repositories or commit revisions without checking them.

## Concise author comment

Use the review already verified in this conversation; if asked whether it is still valid, recheck the current head first. Return a short paste-ready paragraph: recommendation, concrete failure, requested correction and regression case. Include a revision link when useful. Omit repeated chronology and workflow narration. Drafting is separate from posting; post only with explicit authorization.
