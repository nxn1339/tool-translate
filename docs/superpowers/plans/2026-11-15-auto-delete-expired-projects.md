# Kế Hoạch Triển Khai: Tự Động Xóa Dự Án Quá Hạn 1 Tuần (Auto Delete Expired Projects)

## 1. Mục Tiêu Triển Khai
Xây dựng cơ chế quét và xóa dự án tự động sau 1 tuần (7 ngày) hoạt động/cập nhật, đảm bảo:
1. Không xóa nhầm dự án mới hoặc đang xử lý.
2. Tự động kích hoạt khi bật server, định kỳ khi server chạy, và khi tải danh sách dự án.
3. Có bộ test tự động kiểm thử đầy đủ các trường hợp: dự án mới tạo (giữ lại), dự án quá hạn 7 ngày (xóa), dự án không có project.json (xóa theo mtime).

---

## 2. Các Bước Triển Khai Chi Tiết

### Bước 1: Xây dựng hàm lõi `cleanup_expired_projects` trong `app/main.py`
- Định nghĩa hàm `cleanup_expired_projects(max_age_days: int = 7) -> List[str]`.
- Logic:
  - Duyệt qua từng thư mục con trong `PROJECTS_DIR`.
  - Phân tích thời gian:
    - Tìm và đọc `project.json` -> lấy `updated_at` hoặc `created_at` (parse bằng `datetime.fromisoformat`).
    - Fallback: dùng `os.path.getmtime(item_path)` nếu không có `project.json` hoặc file lỗi.
  - Kiểm tra điều kiện:
    - Nếu `(now - last_time).total_seconds() > max_age_days * 86400`:
      - Kiểm tra an toàn: nếu dự án đang ở trạng thái `downloading` hoặc `rendering` trong `projects_db` -> bỏ qua.
      - Xóa thư mục: `shutil.rmtree(item_path, ignore_errors=True)`.
      - Dọn RAM: xóa khỏi `projects_db`.
      - Ghi log: `logger.info(f"Auto-deleted expired project: {item}")`.
      - Thêm vào danh sách `deleted_projects`.
- Trả về danh sách `deleted_projects`.

### Bước 2: Tích hợp các điểm kích hoạt tự động trong `app/main.py`
1. **Startup event (`@app.on_event("startup")`)**:
   - Gọi `cleanup_expired_projects(max_age_days=7)`.
   - Khởi tạo background loop định kỳ: `asyncio.create_task(periodic_cleanup_loop())` (chạy mỗi 12 giờ một lần).
2. **List Projects Endpoint (`GET /api/projects`)**:
   - Gọi `cleanup_expired_projects(max_age_days=7)` trước khi đọc danh sách dự án.
3. **Endpoint kích hoạt thủ công / API test (`POST /api/projects/cleanup`)**:
   - Body hoặc query param `max_age_days: int = 7`.
   - Trả về `{ "status": "ok", "deleted_count": len(deleted), "deleted_projects": deleted }`.

### Bước 3: Viết Unit Test Kiểm Thử (`tests/test_auto_cleanup_projects.py`)
- Tạo dự án giả lập ngày tạo/cập nhật mới (0 ngày) -> kiểm tra không bị xóa.
- Tạo dự án giả lập ngày tạo/cập nhật cũ (8 ngày trước) -> chạy cleanup -> kiểm tra đã bị xóa.
- Tạo thư mục hỏng (không có `project.json`) với mtime cũ > 7 ngày -> chạy cleanup -> kiểm tra đã bị xóa.
- Kiểm tra gọi endpoint `POST /api/projects/cleanup`.
- Kiểm tra `GET /api/projects` tự động dọn dẹp các dự án quá hạn.

### Bước 4: Chạy Kiểm Thử Toàn Bộ & Ghi Nhận Evidence
- Chạy `python -m unittest tests/test_auto_cleanup_projects.py`.
- Chạy lại `python -m unittest tests/test_unified_projects_and_terminals.py` để đảm bảo không hồi quy.
- Lưu bằng chứng vào `docs/superpowers/evidence/2026-11-15-auto-delete-expired-projects.md`.

