# Implementation Plan: Custom Text Overlays on Video

- **Spec Reference:** `docs/superpowers/specs/2026-11-15-custom-text-overlays.md`
- **Execution Date:** 2026-11-15

---

## Các Bước Triển Khai (Phased Tasks)

### Phase 1: Backend Processing (`app/merger.py`)
- [ ] Bổ sung hàm `render_text_overlays_image(text_overlays, video_w, video_h, output_png_path)`:
  - Sử dụng Pillow (PIL) vẽ các text overlays trên ảnh RGBA kích thước `(video_w, video_h)`.
  - Hỗ trợ text tiếng Việt đầy đủ với font Nunito.
  - Hỗ trợ bo góc hộp nền mềm mại (`rounded_rectangle`), padding và opacity.
  - Hỗ trợ italic qua biến đổi affine và shadow viền.
- [ ] Cập nhật `merge_audio_segments_to_video()`:
  - Thêm tham số `text_overlays: Optional[List[Dict[str, Any]]] = None`.
  - Sinh file `text_overlays.png` trong thư mục task nếu có overlay kích hoạt.
  - Thêm file PNG vào danh sách `-i` của FFmpeg.
  - Thêm filter `overlay=0:0` vào video filter graph và đặt cờ `need_video_filter = True`.

### Phase 2: API Endpoints & Request Models (`app/main.py`)
- [ ] Thêm `text_overlays: Optional[List[Dict[str, Any]]] = None` vào `ProjectRenderRequest`.
- [ ] Cập nhật `process_project_render_worker` để truyền `text_overlays` vào `merge_audio_segments_to_video`.
- [ ] Lưu trạng thái `text_overlays` vào `project.json` trong `save_project_meta`.
- [ ] Khởi tạo / nạp `text_overlays` khi mở lại dự án `GET /api/project/{project_id}`.

### Phase 3: Frontend Interactive Canvas & Controls (`index.html`, `style.css`, `app.js`)
- [ ] Mở rộng giao diện Bước 5 (`index.html`):
  - Đổi tiêu đề bước thành "Chèn Logo & Chữ Watermark".
  - Thêm thẻ Card "Chữ Tự Do / Watermark Text" với switch Bật/Tắt chung.
  - Thêm nút preset 1-click: "Áp dụng mẫu Hạt Tiêu Vietsub (Đăng ký + Tên kênh)".
  - Thêm danh sách text overlays, nút thêm text mới, xóa text, và các controls chi tiết cho từng text.
- [ ] Thêm các phần tử `bbox-text-overlay` vào `#canvas-overlay` trong `index.html`.
- [ ] Cập nhật CSS trong `style.css` cho các khung text draggable và panel điều khiển.
- [ ] Cập nhật JavaScript trong `app.js`:
  - Khởi tạo state `textOverlaysState`.
  - Kết nối kéo thả trực quan trên video cho từng khung text bằng `setupDragAndResize`.
  - Đồng bộ hai chiều giữa controls/sliders và khung hiển thị trên video.
  - Gửi `text_overlays` trong payload khi gọi API render video Bước 6.
  - Thêm dòng tổng kết ở Bước 6.

### Phase 4: Unit Testing & Verification Evidence
- [ ] Viết unit test `tests/test_text_overlays.py` kiểm tra sinh ảnh bằng PIL và logic filter FFmpeg.
- [ ] Chạy test và tạo báo cáo `docs/superpowers/evidence/2026-11-15-custom-text-overlays.md`.

