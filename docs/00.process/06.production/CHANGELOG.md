# CHANGELOG - Lịch sử thay đổi tài liệu và dự án

## [2026-10-31] - Đồng bộ tính năng Ghép Logo / Watermark & Sửa lỗi Layout UI Studio

### Added
- **Tính năng Ghép Logo / Watermark vào Video (`VS-006`):**
  - Hỗ trợ tải lên ảnh Logo độc lập cho từng dự án (`PNG`, `JPG`, `WEBP`, `SVG`) qua API `POST /api/project/{id}/logo` và kiểm tra trạng thái qua `GET /api/project/{id}/logo`.
  - Khung tương tác Canvas Transform Box: cho phép kéo di chuyển tự do và co giãn kích thước bằng 8 anchor points (4 góc, 4 cạnh) trên màn hình xem trước.
  - Hộp công cụ Logo tại Bước 3 (`#step3-logo-toolbar`) và Bước 4 (`#step4-logo-card`), nút truy cập nhanh trên Canvas (`#btnLogoCanvasQuick`).
  - Hỗ trợ 5 nút Preset căn vị trí nhanh (Góc trên Trái/Phải, Góc dưới Trái/Phải, Chính giữa), thanh trượt chỉnh độ mờ Opacity (0% - 100%), checkbox khóa tỷ lệ khung hình.
  - Phím tắt bàn phím: bấm `Delete` hoặc `Backspace` khi đang chọn khung để xóa nhanh logo; `Escape` để bỏ chọn.
  - FFmpeg Filter Complex Engine (`app/merger.py`): tự động quy đổi tọa độ % sang pixel tuyệt đối của video nguồn, áp dụng bộ lọc `colorchannelmixer` chỉnh alpha/opacity và `overlay` ghép logo đè lên video kết hợp hoàn hảo với bộ lọc che sub cũ và in hardsub ASS.
  - Bộ kiểm thử tự động `tests/test_logo_overlay.py` bao phủ trọn vẹn API endpoint và logic FFmpeg filter.
- **Đồng bộ hóa toàn diện Tài liệu Source-of-Truth theo chuẩn Enterprise:**
  - Hoàn thiện lát cắt `VS-006`: `REQ-020` -> `REQ-025`, `US-020` -> `US-023`, `BR-020` -> `BR-023`, `AC-020` -> `AC-024`.
  - Cập nhật tài liệu API chi tiết (`docs/04.technical/03.api/VS-006.md` và `api_design.md` gồm đầy đủ 22 endpoints).
  - Cập nhật Kiến trúc hệ thống (`system_architecture.md`) với sơ đồ Mermaid 4 bước Studio và Storage strategy.
  - Cập nhật Kế hoạch quản lý tác vụ (`task_list.md` bổ sung `TASK-010`, `TASK-011`; `dev_task_list.md` bổ sung `DEV-011` -> `DEV-014`).
  - Lập Kế hoạch kiểm thử và Danh sách kịch bản kiểm thử (`VS-006 Test Plan` & `Test Cases TC-022` -> `TC-026`).
  - Cập nhật đồng bộ 3 ma trận truy vết (`requirement_traceability.md`, `screen_function_api_matrix.md`, `test_coverage_matrix.md`).

### Fixed
- **Sửa lỗi Layout UI Studio (Cột tối bên trái màn hình):** Khắc phục triệt để lỗi thẻ `<head>` trong `app/static/index.html` bị đóng sớm do đoạn mã toolbar logo bị chèn nhầm vị trí. Đã chuyển toàn bộ toolbar về đúng phân vùng Bước 3 (`#content-step-3`).
- **Kiểm tra và vá lỗi DOM / JS Listeners:** Rà soát toàn bộ 238 phần tử DOM và bộ lắng nghe sự kiện trong `app/static/app.js`, bổ sung null-check cho các nút preset/toggle để tránh lỗi Uncaught TypeError khi chuyển bước.

---

## [2026-10-24] - Khởi tạo bộ tài liệu Enterprise Source-of-Truth

### Added
- Thiết lập toàn bộ cấu trúc thư mục tài liệu `docs/` chuẩn hóa theo mô hình Enterprise 8 phân vùng (`00.process` đến `07.release` và `superpowers`).
- Bổ sung hệ thống kỹ năng `.agents/skills/` (output-docs-standard, ba-workflow, dev-workflow, test-workflow, pm-task-assignment, docs-consistency-review, change-request-triage, techlead-pr-review, github-pr-link-generator).
- Thiết lập các ma trận truy vết `06.traceability/` (requirement, screen-function-api, test coverage).
- Ghi nhận `VS-001` đến `VS-004` làm nền tảng Vertical Slices cho dự án.
- Phát hiện và lập hồ sơ kỹ thuật `DEV-001` để khắc phục lệch đường dẫn `ffmpeg/ffmpeg.exe`.
