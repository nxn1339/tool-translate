---
name: test-workflow
description: "Use when working as QA/Test on this docs repository: converting Vietnamese requirements, acceptance criteria, screen designs, API specs, contract-first Dev tasks, bug reports, or release scope into Vietnamese UTF-8 test plans, test cases, regression checklists, UAT checklists, bug templates, and coverage traceability under docs/05.testing and docs/06.traceability."
---

# Test Workflow

## Workflow

## Output Docs Standard

- Before creating, updating, or renaming output files, use `$output-docs-standard`.
- Apply its `VS-XXX` naming, source-of-truth placement, generated artifact, and Vietnamese UTF-8 rules.

## External Skill Gate

- Read `docs/00.process/10.skill-catalog/recommended_skills.md` when external QA support may improve QA strategy, AC decomposition, evidence-based pass status, security checks, regression design, or verification.
- Relevant external skills for this workflow:
  - `qa-expert` for QA strategy, severity P0-P4, bug process, metrics, OWASP/security checklist.
  - `quality-engineering-business-analysis` for atomic AC decomposition, permission/role scenarios, and edge-case derivation.
  - `superpowers:verification-before-completion` before claiming test pass, coverage completion, or release readiness.
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
- Do not copy `qa-tester` as a general workflow because it is project-specific to another repo; only reuse its evidence principle when useful.

1. Read source context:
   - Acceptance criteria template nếu cần format: `docs/02.product/06.acceptance-criteria/acceptance_criteria.md`
   - Acceptance criteria source-of-truth theo slice đang test: `docs/02.product/06.acceptance-criteria/VS-XXX.md`
   - Requirement source-of-truth theo slice đang test: `docs/02.product/02.requirement/VS-XXX.md`
   - Screen design source-of-truth theo slice đang test: `docs/03.design/04.screen/VS-XXX.md`
   - API source-of-truth theo slice đang test: `docs/04.technical/03.api/VS-XXX.md`
   - `docs/01.management/04.task/dev_task_list.md` nếu slice đang dùng Dev task `contract-first`
   - `docs/06.traceability/requirement_traceability.md`
2. Update testing source-of-truth files theo slice:
   - `docs/05.testing/01.test-plan/VS-XXX.md`
   - `docs/05.testing/02.test-case/VS-XXX.md`
   - `docs/05.testing/04.regression/VS-XXX.md`
   - `docs/05.testing/05.uat/VS-XXX.md`
   - Use aggregate files such as `test_plan.md`, `test_cases.md`, `regression_checklist.md`, and `uat_checklist.md` only as templates or indexes.
   - Khi mở rộng slice, giữ nguyên test cases và regression checklist Phase 1; nối `# VS-XXX <Document Title> - Phase N Extension` ở cuối từng file theo `$output-docs-standard`.
   - Dưới heading Phase mới, dùng các mục `##` phù hợp cho Test Cases mới (`TC-XXX`), edge cases, bảo mật, tương thích ngược và regression bổ sung. Regression Suite Phase 1 vẫn phải pass 100% trước mỗi release.
3. Update coverage:
   - `docs/06.traceability/test_coverage_matrix.md`
4. If a defect process changes, update:
   - `docs/05.testing/03.bug-report/bug_report_template.md`

## Quality Checks

- Test cases should cover normal, empty, error, permission, negative, security/privacy, and regression paths.
- Test task mở rộng ở phase mới phải bao phủ cả Test Cases mới và Regression Checklist của Phase 1.
- Every acceptance criterion should map to a test case, manual verification, or documented coverage gap.
- For contract-first Dev tasks, Test may start from AC + Design before API details are final, but must mark API/DB/security-dependent cases as coverage gaps until Dev contract exists.
- A pass claim should cite current-session evidence from an executed command or explicit manual verification note.
- Bug reports should include severity P0-P4, reproducible steps, expected result, actual result, environment, and evidence.
- Mark unclear expected behavior as a blocker or open question before inventing test expectations.

## Rules

- Sinh mọi file/tài liệu bằng tiếng Việt có dấu và lưu UTF-8.
- Không dùng tiếng Việt không dấu hoặc nội dung mojibake.
- Giữ nguyên code identifiers, IDs, file paths, API names, DB table names và error strings theo định dạng gốc.
- Khi viết test cho một slice, đọc AC thật từ `VS-XXX.md`; không dùng file template tổng làm scope kiểm thử.
- Khi viết test output cho một slice, ghi nội dung thật vào `docs/05.testing/*/VS-XXX.md`; không chỉ ghi vào file tổng.
- Khi mở rộng test, chỉ ghi test mới sau heading `# VS-XXX <Document Title> - Phase N Extension` ở cuối file; không chèn vào hoặc ghi đè test cases Phase 1.
- Test case IDs use `TC-XXX`.
- Every acceptance criterion must have at least one test case or a clear coverage gap.
- If Dev contract is not final, use `coverage gap` instead of inventing API, DB, or security expected behavior.
- Cover normal, empty, error, permission, and regression cases for each high-priority feature.
- Do not change requirements directly unless fixing traceability references.
- Mark unclear expected behavior as an open question for BA/Design/Dev.

## Output Summary

When done, report:

- Test cases added/changed
- Regression/UAT checklist updates
- Coverage gaps
- Open questions or blockers
