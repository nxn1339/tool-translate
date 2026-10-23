---
name: docs-consistency-review
description: "Use when reviewing this docs repository for Vietnamese UTF-8 consistency across BA, Design, Dev, Test, PM, release, requirements, screens, API, DB, contract-first Dev tasks, test cases, WBS, tasks, changelog, and traceability matrices before handoff, release, or after major documentation changes."
---

# Docs Consistency Review

## Workflow

## Output Docs Standard

- Before reviewing or creating output files, use `$output-docs-standard`.
- Check `VS-XXX` naming, source-of-truth placement, generated artifact links, and Vietnamese UTF-8 consistency against that standard.

## External Skill Gate

- Read `docs/00.process/10.skill-catalog/recommended_skills.md` when external review support may improve traceability audit, implementation readiness, code review, or feedback handling.
- Relevant external skills for this workflow:
  - `traceability-audit` for requirement-to-implementation-to-test-to-release evidence mapping.
  - `implementation-readiness` for READY/BLOCKED/PARTIAL pre-handoff or pre-implementation checks.
  - `superpowers:requesting-code-review` when review touches implemented code or major feature readiness.
  - `superpowers:receiving-code-review` when actionable review feedback must be evaluated.
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

1. Read core files:
   - Product templates nếu cần format:
     - `docs/02.product/02.requirement/requirements.md`
     - `docs/02.product/04.user-story/user_stories.md`
     - `docs/02.product/05.business-rule/business_rules.md`
     - `docs/02.product/06.acceptance-criteria/acceptance_criteria.md`
   - Product source-of-truth theo slice cần review:
     - `docs/02.product/02.requirement/VS-XXX.md`
     - `docs/02.product/04.user-story/VS-XXX.md`
     - `docs/02.product/05.business-rule/VS-XXX.md`
     - `docs/02.product/06.acceptance-criteria/VS-XXX.md`
   - Design source-of-truth theo slice cần review:
     - `docs/03.design/01.design-system/VS-XXX.md`
     - `docs/03.design/02.user-flow/VS-XXX.md`
     - `docs/03.design/03.wireframe/VS-XXX.md`
     - `docs/03.design/04.screen/VS-XXX.md`
     - `docs/03.design/05.prototype/VS-XXX.md`
     - `docs/03.design/06.asset/VS-XXX.md`
   - Technical source-of-truth theo slice cần review:
     - `docs/04.technical/03.api/VS-XXX.md`
     - `docs/04.technical/04.database/VS-XXX.md`
     - `docs/04.technical/06.storage/VS-XXX.md`
     - `docs/04.technical/07.security/VS-XXX.md`
   - Test source-of-truth theo slice cần review:
     - `docs/05.testing/01.test-plan/VS-XXX.md`
     - `docs/05.testing/02.test-case/VS-XXX.md`
     - `docs/05.testing/04.regression/VS-XXX.md`
     - `docs/05.testing/05.uat/VS-XXX.md`
   - `docs/06.traceability/`
2. Check requirement coverage:
   - Requirement has user story or acceptance criteria.
   - Requirement has screen when user-facing.
   - Requirement has API/DB when server data is used, or a linked contract-first Dev task with merge gate.
   - Requirement has test case or documented gap.
3. Check screen-function-API coverage:
   - Every screen action has function ID.
   - Every server action has API ID.
   - Every API ID exists in `docs/04.technical/03.api/VS-XXX.md` or a linked cross-slice API source.
4. Check API-DB coverage:
   - Every persistent API maps to DB table.
   - Private data has security/privacy notes.
5. Check multi-phase slice consistency:
   - Mỗi file `VS-XXX.md` giữ heading `#` và nội dung Phase 1 cũ; mỗi Phase 2+ bắt đầu bằng `# VS-XXX <Document Title> - Phase N Extension` ở cuối phase trước, đúng thứ tự, theo `$output-docs-standard`.
   - Không có nội dung phase mới chen vào mục/bảng phase cũ; Phase 1 không bị sửa khi thiếu Change Request riêng.
   - Phase mới có nguồn `P2-XXX`, task phân công, đánh giá tương thích ngược khi liên quan và coverage trong ma trận traceability.
6. Create review report:
   - `docs/00.process/05.review/review_consistency_YYYYMMDD.md`

## Gap Classification

- Covered: required docs, traceability, and verification evidence exist.
- Partial: some docs or evidence exist, but mapping or verification is incomplete.
- Missing: required docs, traceability, implementation reference, or test evidence is absent.
- Out of scope: gap is explicitly deferred with owner, reason, and target follow-up.
- Contract-first: BA + Design are ready and Dev task exists, but API/DB/security/test details are expected outputs before merge; classify as Partial until evidence lands.

## Finding Format

Use this format:

```markdown
### GAP-XXX: <title>
- Layer: BA / Design / Dev / Test / Traceability
- Related IDs:
- Issue:
- Impact:
- Suggested fix:
- Owner:
- Next workflow:
```

## Rules

- Sinh mọi file/tài liệu bằng tiếng Việt có dấu và lưu UTF-8.
- Không dùng tiếng Việt không dấu hoặc nội dung mojibake.
- Giữ nguyên code identifiers, IDs, file paths, API names, DB table names và error strings theo định dạng gốc.
- Review coverage theo slice phải kiểm tra file `VS-XXX.md` trong từng folder source-of-truth; file tổng chỉ dùng để kiểm tra template/hướng dẫn.
- Kiểm tra ranh giới heading `#` của từng phase trong cùng `VS-XXX.md`; cấm bảng trộn nhiều phase và file phân mảnh như `VS-XXX-Phase2.md`.
- Findings first, summary after.
- Do not silently fix large scope gaps during review unless user asks.
- Small reference mistakes can be fixed if safe.
- Update `docs/00.process/06.production/CHANGELOG.md` if review creates or changes formal docs.
