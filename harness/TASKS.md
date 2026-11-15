# Markdown task pilot

- Keep one project-local roadmap using [the roadmap template](../templates/roadmap.md). Record the goals, why now, ordered priorities, epics, and rough subtasks. The project owner chooses where planning files live and whether to track them in Git.
- When the owner asks for a new task, present a concise proposal using [the task template](../templates/task.md) before starting implementation. Give it a stable reference and link the relevant roadmap item when one applies. Propose priority or scope changes to the owner. A small task may live inline on the roadmap at a stable anchor if it contains the same information.
- Implementers start with the assigned task reference and this workflow. Get owner approval of the plan, intended behavior, and checks before implementation and testing. Before changing existing code, assess the affected automated tests. Record coverage and gaps, add any needed pin-down tests, and verify the baseline on the existing implementation. Rerun the same checks after the change.
- Update progress and evidence on the task. Propose follow-ups and get owner approval before acting on material tradeoffs, especially irreversible ones.
- Reviewers start from the task, including the rationale, tradeoffs, evidence, and user-runnable check. Use the existing adversarial review workflow before PR submission and task closure. Record the reviewed revision and explicit recommendations. One review can cover both gates on the same unchanged revision if it explicitly approves submission and recommends closure against acceptance criteria. Fix requested changes and re-review.
- Close after owner sign-off on the observed behavior. In the pilot, give an independent implementation session only the task reference and this entry point. Record any missing context or steps that needed clarification for future tooling.

Existing authorization remains valid across turns. Integrating and publishing an
already approved change does not start a new task or require repeating approval.
