---
name: design-workflow
description: Use when working as Designer/UX on this docs repository: converting Vietnamese requirements, product flows, BA notes, or prototype ideas into Vietnamese UTF-8 design system notes, user flows, wireframes, screen design, prototype links, asset guidelines, and screen-function traceability under docs/03.design and docs/06.traceability.
---

# Design Workflow

## Workflow

## Output Docs Standard

- Before creating, updating, or renaming output files, use `$output-docs-standard`.
- Apply its `VS-XXX` naming, source-of-truth placement, generated artifact, and Vietnamese UTF-8 rules.

## External Skill Gate

- Read `docs/00.process/10.skill-catalog/recommended_skills.md` when external Design support may improve prototype HTML, slides, animation, visualization, design review, or visual exploration.
- Relevant external skills for this workflow:
  - `huashu-design` for prototype HTML, slides, animation, visualization, or design review.
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
   - Product template files nếu cần format:
     - `docs/02.product/02.requirement/requirements.md`
     - `docs/02.product/04.user-story/user_stories.md`
     - `docs/02.product/06.acceptance-criteria/acceptance_criteria.md`
   - Product source-of-truth theo slice đang làm:
     - `docs/02.product/02.requirement/VS-XXX.md`
     - `docs/02.product/04.user-story/VS-XXX.md`
     - `docs/02.product/06.acceptance-criteria/VS-XXX.md`
   - `docs/03.design/`
2. Define or update UX source-of-truth files theo slice:
   - Design system in `docs/03.design/01.design-system/VS-XXX.md`
   - User flow in `docs/03.design/02.user-flow/VS-XXX.md`
   - Wireframe notes in `docs/03.design/03.wireframe/VS-XXX.md`
   - Screen design in `docs/03.design/04.screen/VS-XXX.md`
   - Prototype links in `docs/03.design/05.prototype/VS-XXX.md`
   - Asset guidelines in `docs/03.design/06.asset/VS-XXX.md`
   - Use aggregate files such as `screen_design.md`, `prototype_links.md`, and `design_system.md` only as templates or indexes.
   - Khi mở rộng slice, giữ nguyên màn hình và flow Phase 1; nối `# VS-XXX <Document Title> - Phase N Extension` ở cuối từng file theo `$output-docs-standard`.
   - Dưới heading Phase mới, dùng các mục `##` phù hợp cho màn hình delta, user flow mới (ví dụ linking, trạng thái trùng email) và asset bổ sung.
3. Update screen mapping:
   - `docs/06.traceability/screen_function_api_matrix.md`
   - `docs/06.traceability/requirement_traceability.md`
4. If assets or design tokens change, update the matching slice files and keep aggregate template/index files aligned only when their guidance changes.

## Rules

- Sinh mọi file/tài liệu bằng tiếng Việt có dấu và lưu UTF-8.
- Không dùng tiếng Việt không dấu hoặc nội dung mojibake.
- Giữ nguyên code identifiers, IDs, file paths, API names, DB table names và error strings theo định dạng gốc.
- Khi làm một slice, đọc BA context thật từ `VS-XXX.md`; không lấy nội dung chi tiết từ các file template tổng.
- Khi viết design output cho một slice, ghi nội dung thật vào `docs/03.design/*/VS-XXX.md`; không chỉ ghi vào file tổng.
- Khi mở rộng thiết kế, nội dung Phase mới chỉ nằm sau heading `# VS-XXX <Document Title> - Phase N Extension` ở cuối file; không chèn vào màn hình baseline Phase 1.
- Screen IDs use `APP-XXX`.
- Function IDs use `FUNC-XXX`.
- Every screen action that reads/writes server data must map to an API placeholder or existing API ID.
- If using external design skills such as Huashu Design, record final links/decisions in `docs/03.design/05.prototype/prototype_links.md`.
- Do not let prototype output become source of truth until reflected into `docs/03.design/`.

## Output Summary

When done, report:

- Screens added/changed
- User flows added/changed
- Prototype/design links added
- Traceability rows updated
- Open questions for BA/Dev/Test
