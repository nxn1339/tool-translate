---
name: dev-workflow
description: "Use when working as Developer/Tech Lead on this docs repository: converting requirements, design, or contract-first Dev tasks into Vietnamese UTF-8 architecture, mobile app design, API design, database design, push notification design, media storage design, security/privacy notes, and technical traceability under docs/04.technical and docs/06.traceability."
---

# Dev Workflow

## Output Docs Standard

- Before creating, updating, or renaming output files, use `$output-docs-standard`.
- Apply its `VS-XXX` naming, source-of-truth placement, and Vietnamese UTF-8 rules.

## Coding Convention Gate

- Before any implementation planning, code review, bug fix, refactor, or technical docs update that references app code, read `docs/04.technical/00.convention/api-mobile-coding-conventions.md`.
- If the work belongs to a slice refactor, read the matching brief as well, for example `docs/04.technical/09.refactor/VS-001-auth-refactor-solution-brief.md`.
- Treat the coding convention as the implementation rule source. If code and convention conflict, stop and record the decision needed instead of silently inventing a new pattern.

## Bug And Refactor Control

- When a bug or refactor need is discovered while coding, classify it before changing code:
  - `bug-blocker`: build/test/runtime/core flow failure. Fix in the current gate, with a regression test or explicit command evidence.
  - `refactor-needed`: maintainability or consistency issue. Fix only if inside the current slice and gate scope; otherwise log or create a dev task.
  - `docs-gap`: source-of-truth does not match implementation. Update docs or assign owner.
  - `tech-debt`: known risk that does not block the gate. Log it with owner and revisit condition.
- Record non-trivial findings in `docs/00.process/05.review/engineering_change_log.md`.
- Use `docs/05.testing/03.bug-report/bug_report_template.md` only when QA needs a full bug report, reproduction steps, severity, and expected/actual behavior.
- Do not mix unrelated refactors into a gate just because they are nearby. Gate scope and slice ownership win.

## External Skill Gate

- Read `docs/00.process/10.skill-catalog/recommended_skills.md` when external Dev support may improve SRS/FRS, interface contracts, data contracts, NFR, readiness, TDD, debugging, or verification.
- Relevant external skills for this workflow:
  - `common-software-requirements` for SRS/FRS, interface contracts, data contracts, NFR thresholds, verification mapping.
  - `implementation-readiness` for go/no-go before implementation or task breakdown.
  - `superpowers:test-driven-development` for feature, bugfix, refactor, or behavior change.
  - `superpowers:systematic-debugging` for bug, test failure, build failure, or unexpected behavior.
  - `superpowers:verification-before-completion` before claiming technical work is complete.
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

## Workflow

1. Read source context:
   - Product requirement template if format is needed: `docs/02.product/02.requirement/requirements.md`
   - Product requirement source-of-truth for the slice: `docs/02.product/02.requirement/VS-XXX.md`
   - Acceptance criteria source-of-truth for the slice: `docs/02.product/06.acceptance-criteria/VS-XXX.md`
   - Design source-of-truth for the slice: `docs/03.design/04.screen/VS-XXX.md`
   - `docs/06.traceability/screen_function_api_matrix.md`
2. Read app coding convention:
   - `docs/04.technical/00.convention/api-mobile-coding-conventions.md`
   - Matching refactor brief when applicable, for example `docs/04.technical/09.refactor/VS-001-auth-refactor-solution-brief.md`
3. Update technical source of truth:
   - `docs/04.technical/01.architecture/system_architecture.md`
   - `docs/04.technical/02.mobile-app/mobile_app_design.md`
   - `docs/04.technical/03.api/VS-XXX.md`
   - `docs/04.technical/04.database/VS-XXX.md`
   - `docs/04.technical/05.notification/push_notification_design.md`
   - `docs/04.technical/06.storage/VS-XXX.md`
   - `docs/04.technical/07.security/VS-XXX.md`
   - Use aggregate or foundation files only for cross-slice guidance, not as the only place for slice contracts.
   - Khi mở rộng slice kỹ thuật, giữ nguyên contracts API và schema DB Phase 1; nối `# VS-XXX <Document Title> - Phase N Extension` ở cuối từng file theo `$output-docs-standard`.
   - Dưới heading Phase mới, dùng các mục `##` phù hợp cho endpoint API mới, DB delta/migration và Backward Compatibility. Đánh giá session JWT cũ và tính toàn vẹn `userId` khi liên quan.
4. Update traceability:
   - `docs/06.traceability/screen_function_api_matrix.md`
   - `docs/06.traceability/requirement_traceability.md`
5. If work creates implementation tasks, update:
   - `docs/01.management/03.wbs/wbs.md`
   - `docs/01.management/04.task/dev_task_list.md` (hoặc `dev_task_list_phase2.md` cho Phase 2)
6. If work reveals bug/refactor/docs-gap/tech-debt, update:
   - `docs/00.process/05.review/engineering_change_log.md`
   - `docs/05.testing/03.bug-report/bug_report_template.md` only for full QA bug reports

## Foundation Lane

Foundation work may happen before feature readiness when it only covers technical base:

- System architecture, mobile app structure, environment strategy, package/layer boundaries, baseline security/privacy, test hooks, lint/test/CI skeleton.
- Candidate implementation tasks stay as `CAND-DEV-XXX` until stack approval and foundation readiness review.
- After approval, create `DEV-XXX` only for base work that does not depend on unfinished business rules.
- Do not implement feature behavior such as login/register/profile/wishlist/couple/diary/notification as foundation work.
- Feature behavior may start only from a slice `DEV-XXX` task. If the task is `contract-first`, update or link API/DB/security/test evidence before merge.

## Quality Checks

- API, DB, storage, notification, security/privacy, migration, failure mode, and NFR impacts should be explicit when touched.
- Technical spec cho extension ở phase mới phải chứng minh không làm vỡ contracts của Phase 1, bảo lưu session cũ và không làm đứt gãy quan hệ dữ liệu liên slice.
- Every technical behavior should map back to requirement IDs and screen/function/API traceability when applicable.
- Persistent API changes should name affected DB tables and data ownership/privacy impact.
- Failure behavior should cover validation errors, permission errors, missing data, retries, and external service failure when relevant.
- Mark unresolved technology choices, environment dependencies, or implementation blockers as risks or decisions needed.
- Every non-trivial bug/refactor decision discovered during implementation should be either fixed with evidence or logged in `engineering_change_log.md`.

## Rules

- Sinh mọi file/tài liệu bằng tiếng Việt có dấu và lưu UTF-8.
- Không dùng tiếng Việt không dấu hoặc nội dung mojibake.
- Giữ nguyên code identifiers, IDs, file paths, API names, DB table names và error strings theo định dạng gốc.
- Khi làm technical spec cho một slice, đọc `REQ` và `AC` thật từ `VS-XXX.md`; file tổng trong `docs/02.product/` chỉ là template/index/legacy overview.
- Khi viết technical output cho một slice, ghi API/DB/storage/security vào file `VS-XXX.md` trong đúng folder kỹ thuật tương ứng; không chỉ ghi vào file tổng.
- Khi mở rộng slice kỹ thuật, chỉ ghi delta sau heading `# VS-XXX <Document Title> - Phase N Extension` ở cuối `VS-XXX.md`; không chèn vào hoặc ghi đè contracts Phase 1.
- Keep technical design framework-neutral until the project chooses React Native, Flutter, or native.
- API IDs use `API-XXX`.
- DB tables use clear English plurals, for example `Couples`, `Memories`, `WishlistItems`.
- Every API that persists data must map to DB tables.
- Every private data flow must mention security/privacy impact.
- Do not invent finalized technology choices; mark them as options if not decided.
- Use `dev_task_list.md` (hoặc `dev_task_list_phase2.md` cho Phase 2) for code implementation tasks. Keep `task_list.md` (hoặc `task_list_phase2.md` cho Phase 2) for PM role-assignment/docs tasks.
- Full feature implementation tasks require concrete `REQ`, `AC`, design, API/DB/security, and test context.
- Contract-first feature tasks may exist after BA + Design readiness when their DoD explicitly requires API/DB/security/test evidence or coverage gaps before merge.
- Foundation implementation tasks may exist earlier only when their technology decision is approved.
- Foundation implementation tasks must link to `DEC-TECH-001` and foundation readiness task/review.

## Output Summary

When done, report:

- Coding convention files read/updated
- Technical docs changed
- Engineering change log rows added/changed
- Dev implementation tasks added/changed, if any
- API/DB/storage/notification/security impacts
- Traceability rows updated
- Risks or decisions needed from PM/BA/Design/Test
