# AGENTS.md - Hướng dẫn cập nhật tài liệu cho AI Agents

Tài liệu trong `docs/` là **Source of Truth** duy nhất của dự án. Mọi thay đổi về code, tính năng hay cấu trúc đều phải được phản ánh tại đây.

## Nguyên tắc cốt lõi

1. **Ngôn ngữ:** Luôn viết bằng tiếng Việt chuẩn có dấu, định dạng UTF-8 không BOM. Tránh mojibake.
2. **Thuật ngữ kỹ thuật:** Giữ nguyên tên biến, hàm, endpoint API, ID (`REQ-XXX`, `VS-XXX`), đường dẫn file và mã lỗi bằng tiếng Anh.
3. **Tính toàn vẹn ID:** Tuyệt đối không tự ý đổi hoặc tái sử dụng ID đã tồn tại.
4. **Tính nhất quán đa tầng (Traceability):**
   - Khi thêm/sửa requirement (`REQ-XXX`), bắt buộc cập nhật `06.traceability/requirement_traceability.md`.
   - Khi thêm/sửa API endpoint (`API-XXX`), bắt buộc cập nhật `06.traceability/screen_function_api_matrix.md`.
   - Khi thêm test case (`TC-XXX`), bắt buộc cập nhật `06.traceability/test_coverage_matrix.md`.
5. **Quy tắc Single-File Multi-Phase:**
   - Mỗi slice tài liệu chỉ dùng 1 file duy nhất `VS-XXX.md`.
   - Khi có giai đoạn mở rộng (Phase 2+), nối heading `# VS-XXX <Title> - Phase N Extension` ở cuối file theo quy chuẩn `$output-docs-standard`; không chia nhỏ thành `VS-XXX-Phase2.md`.
6. **Nhật ký thay đổi:** Mọi thay đổi kiến trúc hoặc tính năng lớn phải ghi nhận tại `00.process/06.production/CHANGELOG.md`.
