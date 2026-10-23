---
name: change-request-triage
description: "Use when triaging Smile Wishlist change requests copied or exported from Google Sheets into batch-specific feedback files under docs/01.management/06.feedback/YYYY-MM-DD-<topic>.md and maintaining the index in docs/01.management/06.feedback/README.md, drafting PM/TASK proposals, bug-fix proposals, and DEV proposals without directly editing task_list.md or dev_task_list.md."
---

# Change Request Triage

Use this repo-level skill when the user brings a Google Sheet change request feed, pasted CR table, TSV/CSV export, or `CR-XXX` feedback and wants PM review before tasks are assigned.

## Core Rules

- Google Sheet is the source of truth.
- Each triage session outputs to a date/batch-specific file under `docs/01.management/06.feedback/YYYY-MM-DD-<topic>.md` (e.g., `2026-08-14-cr-feedback.md`).
- `docs/01.management/06.feedback/README.md` acts as the master index tracking all feedback batches, sync dates, CR counts, and approval statuses.
- One `CR-XXX` becomes one Markdown block.
- Generate draft proposals only.
- Do not edit `docs/01.management/04.task/task_list.md`.
- Do not edit `docs/01.management/04.task/dev_task_list.md`.
- Mark proposal approval as `Draft`.
- Preserve source IDs, code symbols, file paths, API names, DB names, and error strings.
- If scope is unclear, create a clarification proposal instead of inventing missing behavior.
- If DEV readiness is incomplete, write `Gate: Not ready for DEV`.

## Related Workflow

Read `docs/00.process/01.workflow/change-request-triage.md` before updating the feedback file.

Read `references/smile-task-routing.md` when deciding task lane, readiness gate, output file, or DoD.

## Inputs

Accepted input:

- Pasted text copied from Google Sheet.
- TSV export from Google Sheet.
- CSV export from Google Sheet.
- Existing feedback batch files under `docs/01.management/06.feedback/`.

Expected source columns:

`ID`, `Ngày tạo`, `Người đề xuất`, `Loại`, `Feature/Module`, `Màn hình`, `Vấn đề / Mong muốn thay đổi`, `Lý do / Giá trị`, `Mức độ ưu tiên`, `Ảnh hưởng nếu không sửa`, `Link ảnh/video/log`, `Trạng thái`, `Người phụ trách`, `Sprint/Release`, `Ghi chú xử lý`

If headers are mojibake but column order is clear, map by position. If content values are unreadable, ask for a UTF-8/TSV source instead of guessing.

## Output Files

1. **Batch Feedback File**: `docs/01.management/06.feedback/YYYY-MM-DD-<batch-name>.md` (e.g. `2026-08-14-cr-feedback.md`)
2. **Master Index File**: `docs/01.management/06.feedback/README.md` (Update index table)

Keep this structure for the batch feedback file:

1. Title and sync metadata.
2. Triage conventions.
3. Change request blocks.
4. `Task Proposal` section.
5. Clarification list when needed.

## Workflow

1. Read the CR feed.
2. Skip empty rows and rows without meaningful request text.
3. Normalize each usable row into `## CR-XXX - <short title>`.
4. Classify each CR:
   - `Bug`: create `Bug Fix Proposal`.
   - `Change`: create `PM/TASK Proposal` first.
   - `Improvement`: route by impact to Design, BA/Product, Dev spec, Test, or DEV proposal.
   - `UX/UI`: create Design proposal first; add Test proposal if flow/regression impact exists.
   - `Performance`, `Security`, `Data`: require Tech Lead gate before DEV.
   - `Other`: create clarification proposal when scope is unclear.
5. Generate/update `Task Proposal`.
6. Stop after draft proposals and ask PM to approve before task-list updates.

## CR Block Template

```markdown
## CR-001 - Login/Auth error message unclear

- Type: Bug
- Module: Login/Auth
- Screen: Login screen
- Priority: High
- Status: New
- Requested by:
- Created date: 2026-08-14
- Current issue / desired change: Thông báo lỗi chưa rõ khi nhập sai mật khẩu.
- Reason / value: User khó biết cần sửa gì để đăng nhập lại.
- Impact if not fixed: User có thể bỏ flow đăng nhập.
- Evidence: Dán link ảnh/video/log nếu có
- Triage result: Needs bug-fix proposal
- Suggested lane: Bug Fix
- Readiness: Needs diagnosis and test impact check
- Approval: Draft
```

## Task Proposal Template

```markdown
## Task Proposal

### PM/TASK Proposals

| Source CR | Proposed task | Lane | Owner | Output file | DoD | Reason | Approval |
|---|---|---|---|---|---|---|---|

### Bug Fix Proposals

| Source CR | Bug task | Needs diagnosis | Test impact | Owner | DoD | Approval |
|---|---|---|---|---|---|---|

### DEV Proposals

| Source CR | Proposed dev task | Owner | Dependency | DoD | Gate | Approval |
|---|---|---|---|---|---|---|
```

## Bug Handling

For bugs:

- Prefer `Bug Fix Proposals`.
- Set `Needs diagnosis` to `Yes` unless root cause is proven.
- Recommend `diagnosing-bugs` when reproduction/root cause is unknown.
- Recommend relevant Test/QA workflow when expected behavior or regression coverage changes.
- Create a DEV proposal only when expected behavior, affected module, and test impact are clear.

## DEV Gate

Create a DEV proposal only when these are clear:

- Source CR and module.
- Expected behavior after change.
- Dependency on docs/design/test/spec.
- DoD with test evidence.
- PM/Tech Lead approval gate.

If any item is missing, route to `PM/TASK Proposals` or `Bug Fix Proposals` and write `Gate: Not ready for DEV`.

## Completion Response

Report:

- CRs processed.
- PM/TASK proposals.
- Bug Fix proposals.
- DEV proposals.
- Items needing clarification.
- Confirmation that `task_list.md` and `dev_task_list.md` were not modified.

