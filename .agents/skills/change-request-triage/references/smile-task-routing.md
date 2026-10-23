# Smile Wishlist Task Routing

Use this reference only when triaging Smile Wishlist change requests into draft task proposals.

## Source Files

- PM/docs task list: `docs/01.management/04.task/task_list.md`
- Dev implementation task list: `docs/01.management/04.task/dev_task_list.md`
- Feedback feed: `docs/01.management/06.feedback/YYYY-MM-DD-<topic>.md` and index `docs/01.management/06.feedback/README.md`

## Routing Principles

- `TASK-XXX` means PM/docs/BA/Design/Dev spec/Test coordination work.
- `DEV-XXX` means code implementation work.
- Do not create or modify task list rows during triage.
- Proposal rows must keep `Approval: Draft`.
- If a CR needs both documentation and code, propose documentation/readiness first and DEV second with dependency.
- If a CR lacks expected behavior or acceptance criteria, do not propose DEV as ready.

## PM/TASK Proposal Lane

Use this lane when the request needs:

- Requirement update: owner `BA`, output `docs/02.product/02.requirement/<slice>.md`.
- User story update: owner `BA`, output `docs/02.product/04.user-story/<slice>.md`.
- Business rule update: owner `BA`, output `docs/02.product/05.business-rule/<slice>.md`.
- Acceptance criteria update: owner `BA`, output `docs/02.product/06.acceptance-criteria/<slice>.md`.
- User flow/screen/wireframe/prototype update: owner `Design`, output under `docs/03.design/`.
- API/DB/storage/security spec update: owner `Dev`, output under `docs/04.technical/`.
- Test plan/test case/regression/UAT update: owner `Test`, output under `docs/05.testing/`.
- Traceability/readiness update: owner `PM`, output under `docs/06.traceability/` or task list.

Default DoD pattern:

`Source CR is reflected in the named output file, reviewer is named, acceptance/readiness impact is explicit, and remaining gaps are listed.`

## Bug Fix Proposal Lane

Use this lane when:

- Type is `Bug`.
- Current behavior violates expected behavior.
- User-visible error, crash, broken flow, wrong state, security flaw, data issue, or regression is described.

Fields:

- `Needs diagnosis`: `Yes` if root cause is not proven.
- `Test impact`: name expected test update, regression check, or manual evidence.
- `Owner`: `Dev` for code bugs, `Test` for pure test documentation, `Design` for visual bug needing design decision first.
- `DoD`: include fixed behavior, test evidence, and regression scope.

Bug DoD examples:

- `Login wrong-password message is clear, auth error mapping test updated, login regression checked.`
- `Profile date-of-birth field behavior is specified, UI state documented, affected validation tests identified.`

## DEV Proposal Lane

Use this lane only when code work is likely and readiness is clear enough for a draft implementation task.

Required fields:

- `Source CR`
- `Proposed dev task`
- `Owner`
- `Dependency`
- `DoD`
- `Gate`
- `Approval`

Gate values:

- `PM/Tech Lead approval required`
- `Not ready for DEV: missing AC`
- `Not ready for DEV: missing design`
- `Not ready for DEV: missing API/DB/security impact`
- `Not ready for DEV: missing test impact`

DEV proposal DoD must mention:

- File/module or feature area.
- Expected behavior.
- Test evidence.
- Regression/manual evidence if user-facing.

## Type Mapping

| Type | Primary lane | Secondary lane | Gate |
|---|---|---|---|
| Bug | Bug Fix | DEV if ready | Diagnosis and test impact required |
| Change | PM/TASK | DEV proposal after docs readiness | PM approval required |
| Improvement | PM/TASK | DEV if behavior clear | Impact check required |
| UX/UI | PM/TASK Design | Test if flow affected | Design approval required |
| Performance | PM/TASK Dev spec | DEV proposal | Tech Lead review required |
| Security | PM/TASK Dev spec | DEV proposal | Tech Lead/security review required |
| Data | PM/TASK Dev spec | DEV proposal | Migration/rollback assessment required |
| Other | PM/TASK clarification | None until clarified | PM clarification required |

## Output Style

- Keep Markdown tables narrow enough to review.
- Put long detail in CR blocks, not proposal table cells.
- Use exact source CR IDs.
- Keep Vietnamese user-facing descriptions when source is Vietnamese.
- Keep code symbols, paths, API names, and IDs unchanged.

