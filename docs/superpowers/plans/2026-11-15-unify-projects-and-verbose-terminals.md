# Kế Hoạch Triển Khai: Đồng Bộ Quản Lý Dự Án & Terminal Tiến Trình Toàn App

## 1. Mục Tiêu Triển Khai
Thực hiện nâng cấp toàn diện hệ thống:
1. Đồng bộ Quản lý Dự Án (Lưu, Mở, Tự động lưu, Home Hub) cho cả 3 phân hệ: Dịch Phim, Đọc Truyện TTS, Video Threads/FB.
2. Tích hợp Terminal Tiến Trình và hiển thị % chi tiết (Verbose logs) cho cả Đọc Truyện và Threads/FB.
3. Làm giàu thông tin log (Verbose) cho cả 3 phân hệ để người dùng nắm bắt chi tiết từng phân đoạn.

---

## 2. Các Bước Triển Khai Chi Tiết

### Bước 1: Chuẩn Hóa Backend Core Cho Quản Lý Dự Án Đa Phân Hệ (`app/main.py`)
- Cập nhật hàm `load_project_meta`, `save_project_meta`, `list_projects`:
  - Bổ sung trường `type` (`dubber`, `story_tts`, `social_video`) mặc định và khi lưu.
  - Cho phép lọc dự án theo `type` qua query param: `GET /api/projects?type=all|dubber|story_tts|social_video`.
  - Hỗ trợ lưu cấu hình riêng của từng phân hệ vào `project.json`.
- Thêm/chuẩn hóa các endpoint:
  - `POST /api/projects`: Tạo dự án mới theo `type`.
  - `GET /api/projects/{project_id}`: Trả về metadata và dữ liệu trạng thái tương ứng theo `type`.
  - `PUT /api/projects/{project_id}` hoặc `POST /api/projects/{project_id}/save`: Lưu cập nhật dữ liệu của dự án.
  - `DELETE /api/projects/{project_id}`: Xóa dự án và thư mục liên quan.

### Bước 2: Nâng Cấp Background Task, Progress % & Verbose Logs Cho Đọc Truyện (`app/story_tts.py` & `app/main.py`)
- Chuyển tác vụ tổng hợp audio kịch bản `synthesize_story_session` sang chạy dạng background job có lưu trạng thái trong `story_tasks[task_id]` hoặc gắn trực tiếp với `project_id`.
- Thêm cơ chế log chi tiết từng câu:
  - Bóc tách YouTube -> Ghi log chi tiết.
  - Phân tích câu -> Ghi log danh sách câu và thời lượng ước tính.
  - Vòng lặp từng câu -> Cập nhật progress % theo công thức: `(câu hiện tại / tổng câu) * 85% + 10%`.
  - Ghép nối FFmpeg & xuất SRT -> Cập nhật 90% - 100%.
- Cung cấp endpoint:
  - `POST /api/story-tts/synthesize`: Trả về `task_id` ngay lập tức.
  - `GET /api/story-tts/status/{task_id}`: Trả về `{ status, progress, message, logs, result }`.
  - `GET /api/story-tts/project/{project_id}`: Tải project đọc truyện đã lưu.
  - `POST /api/story-tts/project/{project_id}/save`: Lưu trạng thái kịch bản và cấu hình giọng đọc vào project.

### Bước 3: Nâng Cấp Background Task, Progress % & Verbose Logs Cho Threads/FB (`app/social_router.py`)
- Cải thiện hàm `_run_video_generation_task`:
  - Thay vì 4 mốc % cứng (20%, 50%, 75%, 100%), tính % mịn theo số lượng comment và các bước nhỏ:
    + Cào dữ liệu: 5% - 15% (kèm log phân tích cấu trúc bài viết, số lượng bình luận).
    + Render ảnh thẻ bài viết & từng bình luận: 15% - 40% (log từng thẻ ảnh hoàn thành).
    + Sinh TTS cho bài viết & từng bình luận: 40% - 70% (log thời lượng audio từng voice).
    + Ghép Timeline: 70% - 80% (log start/end của từng thẻ hiển thị).
    + Build video FFmpeg 9:16: 80% - 100% (log tiến trình dựng video).
  - Tích hợp ghi log chuẩn `append_social_log(task_id, message, level)` và lưu vào file log.
- Bổ sung chức năng Lưu/Mở Project cho Video Threads/FB:
  - Lưu URL, nội dung bài viết, tác giả, danh sách bình luận (kèm voice từng người), video nền, kết quả đã xuất bản.
  - Endpoints:
    + `POST /api/social/project/save`
    + `GET /api/social/project/{project_id}`

### Bước 4: Nâng Cấp Verbose Logs Cho Dịch Phim & Lồng Tiếng (`app/main.py`, `app/downloader.py`, `app/ocr.py`, `app/tts.py`)
- Bổ sung các dòng log chi tiết hơn vào `append_project_log`:
  - Tải video: Log kích thước file, định dạng, độ phân giải video.
  - Bóc tách âm thanh: Log sample rate, thời lượng file wav.
  - OCR / Whisper: Log số segment phát hiện theo từng mốc thời gian.
  - Dịch thuật: Log model LLM được gọi, số câu trong batch, thời gian dịch.
  - Sinh giọng đọc TTS: Log câu đang đọc, voice, thời lượng file âm thanh sinh ra.
  - Render FFmpeg: Log tham số ghép subtitle box, logo, âm lượng nền và âm lượng TTS.

### Bước 5: Cập Nhật Giao Diện Người Dùng (`app/static/index.html` & `app/static/style.css`)
1. **Trang Chủ (`#home-view`)**:
   - Thêm tab bộ lọc danh mục dự án: [Tất cả] [🎬 Dịch Phim] [🎙️ Đọc Truyện] [🧵 Video Threads].
   - Thẻ dự án hiển thị badge phân loại rõ ràng.
   - Thêm nút tạo mới nhanh cho từng phân hệ từ Trang Chủ.
2. **Phân Hệ Đọc Truyện (`#story-tts-view`)**:
   - Thêm thanh Project Bar chuẩn: Tên dự án (có thể sửa), trạng thái tự động lưu, nút Mở dự án, Tạo mới, Lưu ngay.
   - Nâng cấp khối tiến trình: Thanh progress bar hiển thị số % và text động.
   - Bổ sung khối Terminal Console chuẩn hóa (3 nút màu, Copy, Xóa, Thu gọn, Auto-scroll).
3. **Phân Hệ Video Threads (`#social-video-view`)**:
   - Thêm thanh Project Bar chuẩn tương tự.
   - Bổ sung khối Terminal Console chuẩn hóa tại Bước 4.
   - Hiển thị thanh tiến trình % mượt mà và log thời gian thực.
4. **Modal Mở Dự Án Đồng Bộ**:
   - Popup hiển thị danh sách dự án có tìm kiếm theo tên, lọc theo loại, hiển thị ngày cập nhật và nút Xóa.

### Bước 6: Cập Nhật Logic JavaScript (`app/static/app.js`)
- Xây dựng controller quản lý Terminal dùng chung hoặc module hóa để phục vụ cả 3 phân hệ: `TerminalController(containerId)`.
- Xây dựng cơ chế Auto-save draft và Manual Save cho cả Đọc Truyện và Threads.
- Khôi phục đầy đủ form dữ liệu khi người dùng chọn mở một dự án Đọc Truyện hoặc Threads từ Home Hub hoặc từ nút "Mở Dự Án".
- Lắng nghe polling status của Story TTS và Social Video để cập nhật Terminal và % mượt mà.

### Bước 7: Kiểm Thử & Nghiệm Thu
- Viết unit tests kiểm thử save/load metadata cho cả 3 loại dự án.
- Kiểm thử polling status và streaming log của Story TTS và Social Video.
- Chạy toàn bộ test suite để đảm bảo không hồi quy.
- Xuất tài liệu bằng chứng nghiệm thu tại `docs/superpowers/evidence/2026-11-15-unify-projects-and-verbose-terminals.md`.

