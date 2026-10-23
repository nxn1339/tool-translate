---
name: pm-task-assignment
description: "Use when working as PM or project coordinator on this docs repository: turning feature scope, phase goals, sprint goals, stakeholder decisions, or open requirements into Vietnamese UTF-8 assigned BA, Design, Dev, Test, contract-first Dev tasks, readiness checks, dependencies, traceability, and docs/01.management tracking."
---

# PM Task Assignment

## Overview

Use this skill to split a scoped product change into clear role-based tasks for BA, Design, Dev, and Test. Keep the PM task list aligned with source-of-truth docs, traceability, dependencies, and open questions.

Task management has two levels:

- `docs/01.management/04.task/task_list.md` tracks PM role-assignment tasks for BA, Design, Dev documentation/spec, Test, and PM coordination cho Phase 1 (cho Phase 2 dùng `docs/01.management/04.task/task_list_phase2.md`).
- `docs/01.management/04.task/dev_task_list.md` tracks Dev implementation tasks cho Phase 1 (cho Phase 2 dùng `docs/01.management/04.task/dev_task_list_phase2.md`).

Foundation lane is allowed before feature readiness, but only for technical foundation work that does not encode unfinished business behavior.

## Workflow

## Output Docs Standard

- Before creating tasks that name output files, use `$output-docs-standard`.
- Task `Output file` and DoD must follow its `VS-XXX` naming, source-of-truth placement, generated artifact, and Vietnamese UTF-8 rules.

1. Read PM and source context:
   - `docs/01.management/03.wbs/wbs.md`
   - `docs/01.management/04.task/task_list.md`
   - `docs/01.management/04.task/dev_task_list.md`
   - `docs/01.management/07.decision-log/decision_log.md`
   - Product templates:
     - `docs/02.product/02.requirement/requirements.md`
     - `docs/02.product/04.user-story/user_stories.md`
     - `docs/02.product/06.acceptance-criteria/acceptance_criteria.md`
   - Product source-of-truth theo slice liên quan:
     - `docs/02.product/02.requirement/VS-XXX.md`
     - `docs/02.product/04.user-story/VS-XXX.md`
     - `docs/02.product/05.business-rule/VS-XXX.md`
     - `docs/02.product/06.acceptance-criteria/VS-XXX.md`
   - `docs/03.design/`
   - `docs/04.technical/`
   - `docs/05.testing/`
   - `docs/06.traceability/`
2. Identify assignment scope:
   - Feature, value slice, sprint, phase, defect, or decision.
   - Related IDs such as `VS-XXX`, `REQ-XXX`, `US-XXX`, `BR-XXX`, `AC-XXX`, `APP-XXX`, `FLOW-XXX`, `API-XXX`, `DB-XXX`, `TC-XXX`, `UAT-XXX`.
3. Run readiness check before assignment:
   - Scope has clear goal and expected outcome.
   - BA inputs exist or BA task captures missing product details.
   - Design inputs exist or Design task captures missing flow/screen work.
   - Dev inputs exist or Dev task captures missing API/DB/security/NFR work.
   - Test inputs exist or Test task captures missing test plan/test case/UAT work.
   - Dependencies and blockers are explicit.
4. Split tasks by role:
   - BA: requirements, user stories, business rules, acceptance criteria, traceability trong các file `docs/02.product/*/VS-XXX.md`.
   - Design: flow, wireframe notes, screen design, prototype links, assets, design traceability trong các file `docs/03.design/*/VS-XXX.md`.
   - Dev: architecture, API, DB, storage, notification, security/privacy, technical traceability trong file `VS-XXX.md` của từng folder kỹ thuật.
   - Dev foundation: system architecture, mobile app foundation, baseline contracts, environment strategy, test/CI readiness.
   - Test: test plan, test cases, bug template updates, regression, UAT, coverage matrix.
5. Apply lightweight RACI:
   - Owner: one primary role accountable for task completion.
   - Reviewer: role that must review the output when needed.
   - Dependency: upstream task or document required before starting.
   - Informed: roles affected by result.
6. Define task completion metadata:
   - Output file: source-of-truth files the owner must update.
   - Reviewer: roles that must review the output.
   - Dependency: upstream task, document, blocker, or open decision.
   - DoD: observable completion criteria, including required real IDs or documented gaps.
7. Update `docs/01.management/04.task/task_list.md` (hoặc `docs/01.management/04.task/task_list_phase2.md` cho Phase 2) for role-assignment/docs work.
8. Update `docs/01.management/04.task/dev_task_list.md` (hoặc `docs/01.management/04.task/dev_task_list_phase2.md` cho Phase 2) for implementation backlog work that is ready enough to code, contract-first feature work that is ready after BA + Design with explicit merge gates, or foundation work explicitly allowed before feature readiness.
9. Update `docs/01.management/03.wbs/wbs.md`, `docs/01.management/02.schedule/schedule.md`, or `docs/00.process/06.production/CHANGELOG.md` only when assignment changes scope, delivery order, milestone, or release notes.
10. Report assignments, blockers, dependencies, and next workflow.

## Task Format

Use the existing task table format:

```markdown
| Task ID | Tên task | Liên kết tài liệu | Output file | Owner | Reviewer | Dependency | DoD | Priority | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|
| TASK-XXX | <role> <action> cho <scope> | `<related IDs>` | `<source-of-truth files>` | <BA/Design/Dev/Test/PM> | <review roles> | <upstream IDs/docs> | <verifiable completion criteria> | <High/Medium/Low> | Open |
```

Prefer one task per role per coherent scope. Split further when a task mixes unrelated outputs, has different dependencies, or cannot be reviewed by one role.

## Dev Implementation Task Format

Use `dev_task_list.md` for code implementation tasks. Organize task rows into:
1. **Baseline Feature & Foundation Tables**: Grouped by slice under corresponding headings (e.g., `### Foundation tasks`, `### VS-001 (Auth & Profile) tasks`, `### VS-002 (Pairing & Couple Space) tasks`).
2. **Change Request & Feedback Batch Tables**: When triaging and assigning tasks from feedback/review batches, group them into a dedicated region (e.g., `### CR & Feedback tasks (Batch YYYY-MM-DD)`) to distinguish them from baseline implementation scope.

Format for baseline slice tables:

```markdown
| Dev Task ID | Slice | Tên task | Liên kết | Owner | Dependency | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| DEV-XXX | `VS-XXX` | <implementation action> | `<TASK-XXX>`, `<REQ-XXX>`, `<AC-XXX>` | Dev | <upstream IDs/docs> | <verifiable completion criteria> | Open |
```

Format for CR & Feedback batch tables:

```markdown
| Dev Task ID | Slice | Nguồn CR | Tên task | Owner | Dependency | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| DEV-XXX | `VS-XXX` | `CR-XXX` | <implementation action> | Dev | <upstream IDs/docs> | <verifiable completion criteria> | Open |
```

Create full implementation-ready `DEV-XXX` when the related slice has enough `REQ`, `AC`, design, API/DB/security, and test context to implement safely. Create contract-first feature `DEV-XXX` earlier when BA + Design are ready, but the DoD must require Dev to add or link API path/request/response, DB/storage/security impact, error handling, and test evidence or coverage gap before merge. Foundation tasks may be created earlier only when their technology decision is approved and their DoD does not depend on unfinished business rules.

For foundation implementation, prefer candidates first:

```markdown
| Candidate ID | Slice | Tên task dự kiến | Lý do chưa tạo `DEV-XXX` |
|---|---|---|---|
| CAND-DEV-XXX | Foundation | <base implementation work> | Chờ `DEC-TECH-001` approved và foundation readiness |
```

## Assignment Rules

- Sinh mọi file/tài liệu bằng tiếng Việt có dấu và lưu UTF-8.
- Không dùng tiếng Việt không dấu hoặc nội dung mojibake.
- Giữ nguyên code identifiers, IDs, file paths, API names, DB table names và error strings theo định dạng gốc.
- Keep existing task IDs stable.
- New task IDs use the next available `TASK-XXX`.
- New Dev implementation or contract-first task IDs use the next available `DEV-XXX` in `dev_task_list.md`.
- Do not renumber old tasks.
- Use one accountable owner per task.
- Use `High` for blocking phase/sprint/release work, privacy/security work, or core user flow work.
- Use `Medium` for important follow-up that does not block the current phase.
- Use `Low` for cleanup, documentation polish, or deferred improvement.
- Set status to `Open` for new work unless the current source docs prove it is already done.
- Do not invent missing requirement, screen, API, DB, test, owner, date, or dependency details.
- Put missing decisions into Open Questions or blockers.
- Every `TASK-XXX` should name output files, reviewer, dependency, and DoD. Use `Không có` only when a dependency truly does not exist.
- Khi giao việc tài liệu cho slice ở Phase 2+, DoD phải nêu file `VS-XXX.md`, phase và mục `##` cần viết dưới heading `# VS-XXX <Document Title> - Phase N Extension` ở cuối file theo `$output-docs-standard`; không chèn vào hoặc sửa Phase 1 nếu không có Change Request riêng.
- BA task output cho slice phải trỏ tới `docs/02.product/02.requirement/VS-XXX.md`, `docs/02.product/04.user-story/VS-XXX.md`, `docs/02.product/05.business-rule/VS-XXX.md`, và `docs/02.product/06.acceptance-criteria/VS-XXX.md`.
- Design task output cho slice phải trỏ tới `docs/03.design/*/VS-XXX.md`.
- Dev task output cho slice phải trỏ tới `docs/04.technical/03.api/VS-XXX.md`, `docs/04.technical/04.database/VS-XXX.md`, `docs/04.technical/06.storage/VS-XXX.md`, và `docs/04.technical/07.security/VS-XXX.md` khi liên quan.
- Test task output cho slice phải trỏ tới `docs/05.testing/*/VS-XXX.md` (bao gồm cả Test Cases Phase 2 và Regression Checklist Phase 1).
- Create explicit PM tasks for blockers and open decisions that block role handoff or implementation readiness.
- When creating a blocker/open-decision task, link it back from the blocker or open decision row using `Task theo dõi`.
- Foundation docs/spec tasks may be created before feature slices are ready when they only define stack, architecture, app structure, environment, baseline contracts, security baseline, and test/CI readiness.
- Foundation implementation tasks may become `DEV-XXX` only after stack approval and foundation readiness review.
- Foundation implementation tasks must not implement login/register/profile/wishlist/couple/diary/notification behavior until the matching feature slice is ready.
- Contract-first feature tasks may implement slice behavior after BA + Design readiness, but merge is blocked until API/DB/security/test evidence or documented coverage gaps are complete.

## Readiness Checks

- A BA task is ready when source feedback, decision, or product goal is clear enough to write or update `REQ`, `US`, `BR`, and `AC`.
- A Design task is ready when requirement/user story/AC scope exists or task explicitly asks Design to explore gaps.
- A Dev task is ready when enough product/design context exists to define API/DB/security/NFR, or task explicitly asks Dev to produce a technical spike/spec.
- A Test task is ready when AC or expected behavior exists, or task explicitly asks Test to document coverage gaps and open questions.
- Cross-role handoff is ready when each role output has traceability IDs and known blockers are documented.
- A contract-first Dev task is ready when it links to concrete `REQ/AC/APP/FLOW` source IDs, has explicit dependencies, and its DoD names the missing API/DB/security/test evidence required before merge.
- A full implementation-ready Dev task is ready when it links to concrete source IDs, has explicit dependencies, API/DB/security/test context, and has a verifiable DoD.
- A full implementation-ready Dev task cho extension ở phase mới chỉ được mở từ candidate (ví dụ `CAND-DEV-P2-XXX` -> `DEV-XXX`) khi khối tài liệu Phase 2 tương ứng đã sẵn sàng và vượt qua gate kiểm tra của PM (`TASK-107`).
- A feature implementation task is blocked when it only links to wildcard IDs such as `REQ-AUTH-*`, `API-WISH-*`, or `TC-NOTI-*`.

## Output Summary

When done, report:

- Tasks added or changed.
- Dev implementation tasks added or changed, if any.
- Owner, reviewer, dependency, and informed roles when relevant.
- Readiness status: `READY`, `PARTIAL`, or `BLOCKED`.
- Source documents updated.
- Open questions for PM/BA/Design/Dev/Test.
