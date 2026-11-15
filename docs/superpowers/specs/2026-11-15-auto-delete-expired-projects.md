# Đặc Tả Kỹ Thuật: Tự Động Xóa Dự Án Quá Hạn 1 Tuần (Auto Delete Expired Projects)

## 1. Mục Tiêu & Bối Cảnh
- **Mục tiêu**: Tự động rà soát và xóa vĩnh viễn các thư mục dự án trong `app/projects/` khi đã đủ thời hạn 1 tuần (7 ngày = 168 giờ).
- **Bối cảnh**: Hiện tại hệ thống lưu trữ dự án bền vững trong `PROJECTS_DIR` (`app/projects`), hàm dọn dẹp cũ `cleanup_old_tasks` chỉ dọn file tạm trong `TEMP_DIR` sau 24h và ghi rõ *"PROJECTS_DIR is persistent and is never deleted automatically"*. Để giải phóng dung lượng ổ cứng (video thô, audio TTS, clip xuất bản), cần một cơ chế tự động dọn dẹp các dự án cũ sau 7 ngày.

---

## 2. Tiêu Chuẩn Xác Định Thời Gian Quá Hạn (Age Criteria)
- **Thời hạn ngưỡng**: 7 ngày (`max_age_days = 7` tương đương `7 * 24 * 3600 = 604,800` giây).
- **Quy tắc xác định tuổi thọ**:
  1. **Dự án có `project.json` hợp lệ**:
     - Lấy mốc thời gian từ trường `updated_at` (nếu không có thì lấy `created_at`).
     - *Lý do chọn `updated_at`*: Tránh việc người dùng tạo dự án từ 7 ngày trước nhưng hôm qua vẫn đang làm việc tiếp mà lại bị hệ thống xóa mất dữ liệu. Nếu không có thao tác gì trong 7 ngày liên tiếp thì mới xóa.
  2. **Thư mục hỏng / rác không có `project.json`**:
     - Lấy thời gian sửa đổi gần nhất của thư mục trên hệ điều hành (`os.path.getmtime(dir_path)`).
  3. **Thời điểm quá hạn**: Khi `(thời điểm hiện tại - mốc thời gian) > 7 ngày`.

---

## 3. Kiến Trúc & Cơ Chế Thực Thi

### 3.1. Hàm Xử Lý Lõi (`app/main.py`)
- Khai báo hàm: `cleanup_expired_projects(max_age_days: int = 7) -> List[str]`
  - Quét tất cả thư mục con trong `PROJECTS_DIR`.
  - Đọc `project.json` hoặc `os.path.getmtime`.
  - Nếu tuổi thọ > 7 ngày:
    - Xóa toàn bộ thư mục bằng `shutil.rmtree(item_path, ignore_errors=True)`.
    - Dọn dẹp cache trong RAM: xóa `project_id` khỏi `projects_db` nếu tồn tại.
    - Ghi log hệ thống mức `INFO`: `logger.info(f"Đã tự động xóa dự án quá hạn 1 tuần: {project_id}")`.
  - Trả về danh sách các `project_id` đã được xóa.

### 3.2. Ba Điểm Kích Hoạt Tự Động (Triggers)
1. **Khi khởi động Server (`startup_event`)**:
   - Chạy `cleanup_expired_projects(max_age_days=7)` song song cùng `cleanup_old_tasks()`.
2. **Khi người dùng truy cập danh sách dự án (`GET /api/projects`)**:
   - Gọi `cleanup_expired_projects(max_age_days=7)` trước khi load danh sách, đảm bảo UI Home Hub không bao giờ hiển thị dự án đã hết hạn.
3. **Vòng lặp nền định kỳ (Periodic Background Worker)**:
   - Một background task bất đồng bộ (`asyncio.create_task`) chạy định kỳ mỗi 12 giờ một lần khi server đang chạy liên tục, tự động quét và xóa mà không cần khởi động lại.

### 3.3. Endpoint API Hỗ Trợ
- `POST /api/projects/cleanup`
  - Tham số: `max_age_days: Optional[int] = 7`
  - Mục đích: Cho phép kích hoạt dọn dẹp thủ công, kiểm tra hoặc chạy tự động qua cron/unittest.
  - Phản hồi: `{"status": "ok", "deleted_count": n, "deleted_projects": [...]}`

---

## 4. Tác Động & Rủi Ro Cần Lưu Ý
- **Cảnh báo mất dữ liệu**: Xóa dự án sẽ xóa sạch video nguồn, audio đã ghép, phụ đề SRT và kịch bản. Việc xóa là vĩnh viễn (`shutil.rmtree`).
- **Dự án đang render/download**: Nếu dự án có trạng thái `status in ("downloading", "processing", "rendering")` hoặc có tác vụ nền đang chạy trong `projects_db`, bỏ qua không xóa để tránh xung đột file đang mở.

