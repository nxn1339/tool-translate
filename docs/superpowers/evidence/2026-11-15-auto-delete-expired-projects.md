# Bằng Chứng Nghiệm Thu (Evidence): Tự Động Xóa Dự Án Quá Hạn 1 Tuần (Auto Delete Expired Projects)

**Ngày thực hiện:** 15/11/2026  
**Mục tiêu:** Bổ sung tính năng tự động kiểm tra và xóa vĩnh viễn các dự án lưu trữ trong `app/projects/` khi đã đủ thời hạn 1 tuần (7 ngày = 168 giờ = 604,800 giây) không hoạt động/cập nhật.

---

## 1. Tóm Tắt Các Thành Phần Đã Triển Khai

### 1.1 Backend Core (`app/main.py`)
- **Hàm lõi `cleanup_expired_projects(max_age_days: int = 7) -> List[str]`**:
  - Quét từng thư mục dự án trong `PROJECTS_DIR` (`app/projects/`).
  - Kiểm tra an toàn: Nếu dự án đang ở trạng thái xử lý tích cực (`downloading`, `processing`, `rendering`) trong RAM hoặc metadata, bỏ qua để tránh hỏng file đang ghi.
  - Đọc `updated_at` (ưu tiên) hoặc `created_at` trong `project.json` để tính toán thời gian không hoạt động.
  - Fallback an toàn: Nếu thư mục hỏng hoặc không có `project.json`, sử dụng `os.path.getmtime(item_path)` trên hệ điều hành.
  - Nếu thời gian không hoạt động vượt quá `max_age_days * 86400` giây (7 ngày):
    - Xóa toàn bộ thư mục bằng `shutil.rmtree(item_path, ignore_errors=True)`.
    - Dọn sạch cache `projects_db` trong bộ nhớ RAM.
    - Ghi log hệ thống `INFO: Auto-deleted project expired after {max_age_days} days: {item}`.
    - Trả về danh sách các `project_id` đã được xóa.

- **Vòng lặp ngầm định kỳ `periodic_projects_cleanup_worker()`**:
  - Tác vụ bất đồng bộ chạy nền tự động mỗi 12 giờ một lần khi server hoạt động liên tục.

- **Ba điểm kích hoạt tự động (Triggers)**:
  1. `startup_event()`: Tự động chạy dọn dẹp ngay khi khởi động FastAPI server, đồng thời đăng ký background worker `periodic_projects_cleanup_worker()`.
  2. `GET /api/projects`: Tự động gọi `cleanup_expired_projects(max_age_days=7)` trước khi đọc danh mục dự án, đảm bảo giao diện người dùng không hiển thị dự án quá hạn.
  3. `POST /api/projects/cleanup`: Endpoint hỗ trợ kích hoạt dọn dẹp thủ công và kiểm thử (`max_age_days: int = 7`).

---

## 2. Kết Quả Kiểm Thử Tự Động (Automated Test Suite)

Tệp kiểm thử chuyên biệt: [tests/test_auto_cleanup_projects.py](file:///c:/project/tool-translate/tests/test_auto_cleanup_projects.py)

```
..INFO:app.main:Auto-deleted project expired after 7 days: test_api_cleanup_006
INFO:httpx2:HTTP Request: POST http://testserver/api/projects/cleanup?max_age_days=7 "HTTP/1.1 200 OK"
.INFO:app.main:Auto-deleted project expired after 7 days: test_corrupt_folder_004
.INFO:app.main:Auto-deleted project expired after 7 days: test_expired_project_002
.INFO:app.main:Auto-deleted project expired after 7 days: test_list_trigger_007
INFO:httpx2:HTTP Request: GET http://testserver/api/projects "HTTP/1.1 200 OK"
..
----------------------------------------------------------------------
Ran 7 tests in 0.136s

OK
```

### Chi tiết các test case:
1. `test_active_recent_project_not_deleted`: Dự án mới cập nhật 2 ngày trước -> **PASSED** (Không bị xóa).
2. `test_expired_project_deleted`: Dự án quá hạn 8 ngày (> 7 ngày) -> **PASSED** (Bị xóa hoàn toàn).
3. `test_project_created_long_ago_but_recently_updated`: Dự án tạo từ 10 ngày trước nhưng vừa cập nhật hôm qua -> **PASSED** (Không bị xóa).
4. `test_corrupt_folder_without_json_deleted_by_mtime`: Thư mục rác không có `project.json` có mtime 9 ngày trước -> **PASSED** (Bị xóa theo mtime).
5. `test_active_rendering_project_not_deleted`: Dự án đang render dù thời gian cũ -> **PASSED** (Bỏ qua an toàn, không bị xóa).
6. `test_cleanup_api_endpoint`: Gọi `POST /api/projects/cleanup?max_age_days=7` -> **PASSED** (Dọn dẹp chính xác).
7. `test_list_projects_triggers_cleanup`: Gọi `GET /api/projects` -> **PASSED** (Tự động kích hoạt dọn dẹp và loại bỏ dự án quá hạn).

### Kiểm thử hồi quy (Regression Test):
Tệp kiểm thử [tests/test_unified_projects_and_terminals.py](file:///c:/project/tool-translate/tests/test_unified_projects_and_terminals.py):
- **4/4 tests PASSED** (Tạo dự án đa phân hệ, lưu/tải trạng thái, polling log và terminal).
- **Tổng cộng: 11/11 tests PASSED**.

