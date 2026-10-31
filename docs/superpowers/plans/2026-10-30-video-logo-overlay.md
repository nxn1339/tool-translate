# Implementation Plan: Video Logo / Watermark Overlay

- **Spec Reference:** `docs/superpowers/specs/2026-10-30-video-logo-overlay.md`
- **Execution Date:** 2026-10-30

---

## Các Bước Triển Khai (Phased Tasks)

### Phase 1: Backend Processing (`app/merger.py`)
- [ ] Bổ sung tham số `logo_box: Optional[Dict[str, Any]] = None` vào `merge_audio_segments_to_video`.
- [ ] Tính toán kích thước pixel và tọa độ `(pos_x, pos_y, target_w, target_h)` dựa trên độ phân giải video gốc.
- [ ] Chèn input logo vào danh sách cmd FFmpeg sau các file audio TTS:
  `logo_input_idx = 1 + len(active_timeline_segments)`.
- [ ] Thêm các filter `scale`, `colorchannelmixer` (cho opacity) và `overlay` vào `filter_parts`.
- [ ] Bật cờ `need_video_filter = True` nếu logo được kích hoạt.

### Phase 2: API Endpoints & Request Models (`app/main.py`)
- [ ] Thêm `UploadFile, File` vào FastAPI import.
- [ ] Thêm `logo_box: Optional[Dict[str, Any]] = None` vào `ProjectRenderRequest`.
- [ ] Viết endpoint `POST /api/project/{project_id}/logo` để lưu file ảnh vào thư mục dự án.
- [ ] Viết endpoint `GET /api/project/{project_id}/logo` để phục vụ xem trước ảnh logo.
- [ ] Cập nhật `process_project_render_worker` để truyền `logo_box` vào `merge_audio_segments_to_video`.
- [ ] Lưu trạng thái `logo_box` vào `project.json` để giữ cấu hình qua các lần mở lại.

### Phase 3: Frontend Interactive Canvas & Controls (`index.html`, `style.css`, `app.js`)
- [ ] Thêm khung `bbox-logo` vào bên trong `#canvas-overlay` trong `app/static/index.html`.
- [ ] Thiết kế style CSS cho `bbox-logo`, icon huy hiệu, ảnh preview co giãn `object-fit: contain`, 4 handles đổi kích thước.
- [ ] Thêm cụm điều khiển Logo trong Bước 4 (Xuất Video) và Quick Toolbar: Upload logo, switch bật/tắt, sliders kích thước / vị trí / opacity, nút preset góc.
- [ ] Trong `app/static/app.js`:
  - Khởi tạo `logoBoxCoords = { x: 80, y: 5, w: 15, h: 10, opacity: 1.0, enabled: false }`.
  - Kết nối `setupDragAndResize` cho `bbox-logo`.
  - Xử lý sự kiện kéo thả file / upload logo và preview tức thì bằng `URL.createObjectURL`.
  - Đồng bộ hai chiều giữa sliders và khung trên video.
  - Gửi `logo_box` trong payload khi gọi API render video.

### Phase 4: Unit Testing & Verification Evidence
- [ ] Viết unit test tự động `tests/test_logo_overlay.py` kiểm tra logic sinh lệnh FFmpeg với `logo_box`.
- [ ] Chạy test và ghi lại kết quả kiểm chứng vào `docs/superpowers/evidence/2026-10-30-video-logo-overlay.md`.

