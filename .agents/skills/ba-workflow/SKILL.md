---
name: ba-workflow
description: Use when working as BA/Product Owner on this docs repository: turning feedback, meeting notes, decisions, product ideas, or stakeholder requests into Vietnamese UTF-8 requirements, user stories, business rules, acceptance criteria, and traceability under docs/02.product and docs/06.traceability.
---

# BA Workflow

## Workflow

## Output Docs Standard

- Before creating, updating, or renaming output files, use `$output-docs-standard`.
- Apply its `VS-XXX` naming, source-of-truth placement, generated artifact, and Vietnamese UTF-8 rules.

## External Skill Gate

- Read `docs/00.process/10.skill-catalog/recommended_skills.md` when external BA support may improve BRD-lite, PRD analysis, acceptance criteria, permission/actor mapping, traceability, or readiness.
- Relevant external skills for this workflow:
  - `common-business-requirements` for BRD-lite, business objective, stakeholder impact, AS-IS/TO-BE.
  - `common-product-requirements` for PRD gap analysis, owner, priority, acceptance criteria, rollout readiness.
  - `quality-engineering-business-analysis` for atomic AC, actor/permission matrix, platform tags, truth-table analysis.
  - `implementation-readiness` for BA readiness before Design/Dev/Test handoff.
- If a recommended skill is installed, ask before using it:

```text
Recommended external skill may help: <skill name> for <purpose>.
Use it for this task? If no, continue with repo-level workflow only.
```

- If a recommended skill is not installed, ask before installing it:

```text
Recommended external skill is not installed: <skill name> for <purpose>.
Install it now? If no, continue with repo-level workflow only.
```

- Never auto-install or auto-use external skills.
- If the user declines or the skill is unavailable, continue with this repo-level workflow.
- Treat external skill output as advisory material only.
- Reflect final decisions and outputs into `docs/` source-of-truth files.

1. Read source context:
   - `docs/README.md`
   - `docs/01.management/05.meeting/`
   - `docs/01.management/06.feedback/`
   - `docs/01.management/07.decision-log/decision_log.md`
   - `docs/02.product/`
2. Extract product changes:
   - New requirement
   - Requirement change
   - Business rule
   - Open question
   - Acceptance criteria
3. Update source-of-truth files theo slice:
   - Xác định slice ID, ví dụ `VS-001`.
   - Với Phase 2+, giữ nguyên toàn bộ phần Phase 1 trong từng `VS-XXX.md`. Nối `# VS-XXX <Document Title> - Phase N Extension` ở cuối file theo `$output-docs-standard`.
   - Trong phần Phase mới, dùng các mục `##` phù hợp: Scope, Functional Requirements (`REQ-XXX` mới kèm nguồn `P2-XXX` và task liên quan), Non-functional, Out of Scope, Open Questions. Ghi việc đưa tính năng từng hoãn vào scope mới tại Phase mới, không sửa bảng Out Of Scope Phase 1 chỉ vì thay đổi này.
   - Slice mới bắt đầu bằng heading `# VS-XXX <Document Title>`; thêm Phase mới theo cùng quy tắc khi có mở rộng.
   - Đọc template tổng nếu cần format:
     - `docs/02.product/02.requirement/requirements.md`
     - `docs/02.product/04.user-story/user_stories.md`
     - `docs/02.product/05.business-rule/business_rules.md`
     - `docs/02.product/06.acceptance-criteria/acceptance_criteria.md`
   - Tạo hoặc cập nhật nội dung thật trong file slice:
     - `docs/02.product/02.requirement/VS-XXX.md`
     - `docs/02.product/04.user-story/VS-XXX.md`
     - `docs/02.product/05.business-rule/VS-XXX.md`
     - `docs/02.product/06.acceptance-criteria/VS-XXX.md`
4. Update traceability:
   - `docs/06.traceability/requirement_traceability.md`
5. If scope or priority changes, update:
   - `docs/01.management/03.wbs/wbs.md`
   - `docs/01.management/04.task/task_list.md` (hoặc `task_list_phase2.md` cho Phase 2)
   - `docs/00.process/06.production/CHANGELOG.md`

## Quality Checks

- Large-scope requirements should name business goal, owner, priority, and success metric.
- Acceptance criteria should be atomic, testable, and traceable to requirement IDs.
- Actor, permission, platform, and state differences should be explicit.
- Multi-condition rules should be split or documented with truth-table style notes when needed.
- Undefined behavior, unclear success metric, missing owner, or cross-role impact should be marked as open questions instead of guessed.

## Rules

- Sinh mọi file/tài liệu bằng tiếng Việt có dấu và lưu UTF-8.
- Không dùng tiếng Việt không dấu hoặc nội dung mojibake.
- Giữ nguyên code identifiers, IDs, file paths, API names, DB table names và error strings theo định dạng gốc.
- Product docs chi tiết phải được viết theo file slice `VS-XXX.md`; các file `requirements.md`, `user_stories.md`, `business_rules.md`, `acceptance_criteria.md` chỉ là template/hướng dẫn.
- Khi mở rộng slice, nối heading `# VS-XXX <Document Title> - Phase N Extension` ở cuối file; không chèn vào hoặc sửa phần Phase 1 nếu không có Change Request riêng.
- Keep existing IDs stable.
- New requirements use `REQ-XXX`.
- New user stories use `US-XXX`.
- New acceptance criteria use `AC-XXX`.
- Mark unclear items as open questions instead of guessing.
- Do not edit design, API, DB, or test files unless needed for traceability.

## Output Summary

When done, report:

- Requirements added/changed
- User stories and acceptance criteria added/changed
- Traceability rows updated
- Open questions for PM/Design/Dev/Test
