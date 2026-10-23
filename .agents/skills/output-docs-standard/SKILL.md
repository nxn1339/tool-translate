---
name: output-docs-standard
description: Use when creating, updating, naming, renaming, or reviewing documentation output files in this docs repository, especially vertical slice files, templates, source-of-truth docs, generated artifacts, role workflow outputs, or Vietnamese UTF-8 consistency.
---

# Output Docs Standard

## Purpose

Use this skill as the shared output contract for all repo-level skills. It keeps file naming, source-of-truth placement, and language rules consistent across BA, Design, Dev, Test, PM, and review work.

## Naming Rules

| Case | Pattern | Example |
|---|---|---|
| Vertical slice ID | `VS-XXX` | `VS-001` |
| Slice doc in a folder that already names the document type | `VS-XXX.md` | `docs/02.product/05.business-rule/VS-001.md` |
| Generated non-source artifact | `VS-XXX-<artifact-summary>.<ext>` | `docs/03.design/05.prototype/VS-002-visual-directions.html` |
| Review report | `review_consistency_YYYYMMDD.md` | `docs/00.process/05.review/review_consistency_20260810.md` |

Rules:

- Use uppercase `VS`, hyphen, and three digits: `VS-001`, not `VS_001`.
- Do not add a summary slug when the parent folder already identifies the doc type. Use `docs/02.product/05.business-rule/VS-001.md`, not `VS-001_business_rule_<summary>.md`.
- The same rule applies to Dev outputs. Use `docs/04.technical/03.api/VS-001.md`, not `VS-001_api_design.md`.
- Add a short English kebab-case summary only for generated artifacts or one-off supporting files where humans need to distinguish variants.
- Use `business-rule`, not `bussiness-rule`.
- Keep existing file names stable unless the user asks for a migration; when migrating, update all references in skills, workflow docs, task lists, traceability, plans, and specs.

## Multi-Phase Slice Structure

Khi một Vertical Slice (`VS-XXX`) được mở rộng hoặc nâng cấp qua nhiều Phase (ví dụ Phase 1 baseline có thêm tính năng mở rộng ở Phase 2, Phase 3):

- **Giữ nguyên tắc Single File**: Duy trì duy nhất một file `VS-XXX.md` cho mỗi loại tài liệu (không tạo file phân mảnh như `VS-XXX-Phase2.md` hay `VS-XXX_extension.md`).
- **Ranh giới cấp tài liệu**: Giữ nguyên heading `#` đầu file và toàn bộ nội dung Phase 1 hiện có; mặc định phần này là Phase 1. Không bọc lại Phase 1, đổi cấp heading cũ, đổi trạng thái, sửa bảng hay ID chỉ để thêm phase mới.
- **Phase mới nối cuối file**: Thêm heading `# VS-XXX <Document Title> - Phase N Extension` sau toàn bộ nội dung phase trước. Lấy `VS-XXX` từ tên file và `<Document Title>` từ heading `#` đầu file sau khi bỏ `VS-XXX` nếu đã có; không đổi heading cũ nếu nó chưa chứa ID. Mỗi phase mới dùng một heading `#` riêng, theo thứ tự Phase 2, Phase 3... Không chèn nội dung phase mới vào giữa các mục của phase cũ.
- **Mục con trong phase**: Dùng `##` cho Scope, Requirements/Contracts, Non-functional, Out of Scope, Open Questions và các mục phù hợp với loại tài liệu. Bảng, ID, nguồn `P2-XXX` và task của phase mới nằm hoàn toàn dưới heading `#` của phase đó; không dùng bảng chung cho nhiều phase.
- **Bảo toàn baseline**: Không sửa nội dung, ID hoặc logic Phase 1 để phản ánh Phase 2. Ghi delta, việc chuyển scope và tham chiếu tới nội dung cũ trong Phase 2. Sửa Phase 1 chỉ khi có Change Request riêng.
- **Tương thích ngược**: Phase mở rộng phải đánh giá tác động tới session/token, migration DB và quan hệ dữ liệu trước đó khi liên quan; không ép mục kỹ thuật không liên quan vào mọi loại tài liệu.

Ví dụ cho file requirements đã có Phase 1:

```markdown
# VS-001 Requirements

## Scope
## Functional Requirements
## Out Of Scope

# VS-001 Requirements - Phase 2 Extension

## Scope
## Functional Requirements
## Out Of Scope
## Backward Compatibility
```

Nếu heading cũ là `# API Design` trong `VS-001.md`, giữ nguyên heading đó; heading mới là `# VS-001 API Design - Phase 2 Extension`.

## Source Of Truth

- Product detail lives in slice files under `docs/02.product/*/VS-XXX.md`.
- Design detail lives in slice files under `docs/03.design/*/VS-XXX.md` when that folder already separates artifact type.
- Technical slice contracts live in slice files under `docs/04.technical/*/VS-XXX.md`.
- Test detail lives in slice files under `docs/05.testing/*/VS-XXX.md`.
- Aggregate files such as `requirements.md`, `user_stories.md`, `business_rules.md`, `acceptance_criteria.md`, `screen_design.md`, and `test_cases.md` are templates, indexes, or legacy overview files unless a workflow explicitly says otherwise.
- Generated HTML, images, exports, and external skill outputs are supporting artifacts only until linked or summarized in the relevant source-of-truth Markdown file.

## Language Rules

- Human-readable docs must be Vietnamese with accents and valid UTF-8.
- English is fine for skill names, headings already in English, file paths, IDs, code identifiers, API names, DB table names, error strings, status values, and technology names.
- Mixed Vietnamese and English is acceptable when English terms are stable project terms; avoid half-translated prose that changes meaning.
- Never create mojibake. If existing text displays mojibake, fix encoding before editing content.
- Preserve exact identifiers and paths even when surrounding prose is Vietnamese.

## Output Checklist

Before finishing any docs output:

- [ ] New or changed files follow the naming table.
- [ ] Slice detail was written to the slice source-of-truth file, not only to a template or aggregate file.
- [ ] Mỗi phase mới bắt đầu bằng heading `# VS-XXX <Document Title> - Phase N Extension` ở cuối file; Phase 1 giữ nguyên và không có bảng trộn nhiều phase.
- [ ] Generated artifacts are linked from a source-of-truth Markdown file.
- [ ] Vietnamese text has accents and no mojibake.
- [ ] Traceability files are updated when requirement, design, API, DB, or test coverage changes.
- [ ] Final response lists created/changed files and open questions.

## Common Mistakes

| Mistake | Fix |
|---|---|
| `VS_001_bussiness_rule_<summary>.md` | Use `docs/02.product/05.business-rule/VS-001.md`. |
| `VS-001_api_design.md` | Use `docs/04.technical/03.api/VS-001.md`. |
| Trộn Phase 2 vào bảng Phase 1 hoặc tạo `VS-XXX-Phase2.md` | Giữ Phase 1 nguyên trạng; nối `# VS-XXX <Document Title> - Phase 2 Extension` ở cuối `VS-XXX.md`. |
| Writing real requirements into `requirements.md` only | Move detail into `docs/02.product/02.requirement/VS-XXX.md`. |
| Treating prototype HTML as final design source | Link it from `docs/03.design/05.prototype/VS-XXX.md` and reflect decisions into design docs. |
| Renaming slice files without updating references | Update skills, workflow docs, task lists, traceability, plans, and specs in the same change. |
