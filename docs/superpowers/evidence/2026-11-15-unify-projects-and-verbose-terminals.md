# Bằng Chứng Nghiệm Thu (Evidence): Đồng Bộ Lưu Project & Terminal Verbose Cho Toàn Bộ Ứng Dụng

**Ngày thực hiện:** 15/11/2026  
**Mục tiêu:** Thống nhất hệ thống Quản lý Project (Lưu / Mở / Đổi tên) và Terminal hiển thị tiến trình (Progress % + Real-time Verbose Logs) cho toàn bộ 3 phân hệ ứng dụng: Dịch Phim & Lồng Tiếng (`dubber`), Đọc Truyện TTS (`story_tts`), và Video Ngắn Threads/FB (`social_video`).

---

## 1. Tóm Tắt Các Thành Phần Đã Triển Khai

### 1.1 Backend FastAPI
- [app/main.py](file:///c:/project/tool-translate/app/main.py):
  - Chuẩn hóa cấu trúc `project.json` hỗ trợ trường `type: "dubber" | "story_tts" | "social_video"`.
  - Cập nhật `GET /api/projects` nhận query parameter `type` (`all`, `dubber`, `story_tts`, `social_video`) trả về thông tin tóm tắt (`preview_text`, `voice_name`, `author_name`, v.v.).
  - Cập nhật `POST /api/projects` tự động khởi tạo dữ liệu mẫu chuẩn theo từng phân hệ.
  - Cung cấp endpoint lưu trạng thái toàn diện: `POST /api/projects/{project_id}/save`.
  - Nâng cấp `POST /api/story-tts/synthesize` chạy nền qua `BackgroundTasks`, nhận `project_id`.
  - Cung cấp endpoint theo dõi tiến trình truyện: `GET /api/story-tts/status/{task_id}` trả về `progress`, `status`, `message`, `logs`.
  - Tăng độ chi tiết verbose logging cho tiến trình Dubber (`_progress_cb` log từng câu, OCR log mốc 20%).

- [app/story_tts.py](file:///c:/project/tool-translate/app/story_tts.py):
  - Thêm quản lý trạng thái tác vụ qua `story_tasks` và `append_story_log`.
  - Cải tiến `synthesize_story_session`: Tính % tiến độ động theo từng câu thoại (10% -> 90%), log chi tiết nội dung preview (tối đa 38 ký tự), log FFmpeg ghép nối câu thoại, xuất phụ đề SRT cue và lưu tự động vào thư mục `app/projects/{project_id}/`.

- [app/social_router.py](file:///c:/project/tool-translate/app/social_router.py):
  - Thêm `append_social_log` ghi song song vào RAM và `project_logs.json`.
  - Nâng cấp `_run_video_generation_task`: % tiến độ mịn (10% -> 35% -> 65% -> 72% -> 95% -> 100%), in chi tiết render ảnh thẻ bài viết, từng comment, TTS từng voice, tiến trình ghép nối timeline và FFmpeg render video dọc 9:16.
  - Tự động đồng bộ hóa kết quả và metadata vào `project.json` của dự án.

### 1.2 Giao Diện (HTML & CSS)
- [app/static/index.html](file:///c:/project/tool-translate/app/static/index.html):
  - **Trang Chủ (`#home-view`)**: Thêm thanh lọc danh mục tab `home-projects-filter-bar` (Tất Cả, Dịch Phim, Đọc Truyện TTS, Video Threads/FB).
  - **Phân hệ Đọc Truyện (`#story-tts-view`)**: Thêm thanh Project Bar (Đổi tên dự án tại chỗ, trạng thái tự động lưu, nút Mở/Dự Án Mới/Lưu Ngay), thêm % tiến độ vào `#story-progress-box`, và bổ sung Terminal Console toàn chiều rộng (`#story-terminal-box`).
  - **Phân hệ Video Threads/FB (`#social-video-view`)**: Thêm thanh Project Bar đầy đủ, và bổ sung Terminal Console (`#social-terminal-box`) vào Bước 4.
  - **Modal Quản Lý Dự Án (`#modal-projects`)**: Bổ sung bộ lọc tab danh mục `#modal-projects-filters`.

- [app/static/style.css](file:///c:/project/tool-translate/app/static/style.css):
  - Thêm style cho thanh lọc dự án trang chủ `.home-projects-filter-bar`, badge phân loại dự án (`.type-story_tts`, `.type-social_video`, `.badge-source-type`).

### 1.3 JavaScript Logic Controller
- [app/static/app.js](file:///c:/project/tool-translate/app/static/app.js):
  - Xây dựng factory controller `createTerminalManager` cho phép dùng chung logic điều khiển Terminal Console (Copy logs, Xóa màn hình, Thu gọn/Mở rộng, Auto-scroll) cho cả 3 phân hệ: `dubberTerminal`, `storyTerminal`, `socialTerminal`.
  - Cập nhật modal dự án và trang chủ hỗ trợ lọc tab, hiển thị nhãn màu theo loại dự án, và click mở phục hồi đúng phân hệ (`openProject`, `loadStoryProject`, `loadSocialProject`).
  - Cập nhật phân hệ Đọc Truyện TTS: Gửi kèm `project_id`, polling real-time qua `/api/story-tts/status/{taskId}`, cập nhật thanh % và stream log ra `storyTerminal`.
  - Cập nhật phân hệ Video Threads/FB: Gửi kèm `project_id`, polling real-time qua `/api/social/status/{taskId}`, cập nhật thanh % và stream log ra `socialTerminal`.

---

## 2. Kết Quả Kiểm Thử Tự Động (Automated Test Suite)

Tệp kiểm thử tích hợp mới: [tests/test_unified_projects_and_terminals.py](file:///c:/project/tool-translate/tests/test_unified_projects_and_terminals.py)
- `test_create_and_filter_projects`: **PASSED** (Kiểm tra tạo project `story_tts` và `social_video`, lọc query `/api/projects?type=...`).
- `test_save_and_load_full_project`: **PASSED** (Kiểm tra lưu toàn diện trạng thái qua `/api/projects/{id}/save` và tải lại đầy đủ metadata qua `/api/projects/{id}`).
- `test_story_tts_status_polling`: **PASSED** (Kiểm tra endpoint `/api/story-tts/status/{id}` trả về `running`, progress %, và logs chi tiết).
- `test_social_video_status_polling`: **PASSED** (Kiểm tra endpoint `/api/social/status/{id}` trả về trạng thái `rendering`, progress %, và logs chi tiết).

Tệp kiểm thử regression: [tests/test_story_tts.py](file:///c:/project/tool-translate/tests/test_story_tts.py)
- **6/6 tests PASSED** (Bao gồm CapCut TTS client, E2E synthesis, chunk split, TikTok voices check).

