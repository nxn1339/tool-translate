# Feature Specification: Video Logo / Watermark Overlay

- **Feature Name:** Video Logo / Watermark Overlay (Ghép Logo vào Video tùy biến vị trí và kích thước)
- **Status:** In Progress
- **Created Date:** 2026-10-30
- **Scope:** Full-stack (Backend FFmpeg rendering, FastAPI endpoints, Frontend interactive Canvas Overlay & Controls)

---

## 1. Yêu Cầu Nghiệp Vụ (Requirements)

1. **Upload & Quản lý Logo:**
   - Cho phép người dùng tải lên hình ảnh logo (PNG, JPG, JPEG, WEBP, SVG).
   - Hỗ trợ tốt kênh alpha (transparency) của file PNG/WEBP.
   - Lưu trữ logo gắn liền với từng project: `app/projects/{project_id}/logo.{ext}`.
   - Cho phép xóa hoặc bật/tắt logo mà không cần upload lại.

2. **Tương tác trực quan trên Video Canvas (Preview Overlay):**
   - Hiển thị khung Bounding Box của logo (`bbox-logo`) ngay trên màn hình xem trước video (`canvas-overlay`), đồng bộ với khung đỏ (Masking/OCR) và khung xanh (Phụ đề Việt).
   - Cho phép **kéo thả vị trí tùy ý (Drag & Drop)** trên khung video (tính theo tọa độ phần trăm % để tương thích mọi kích thước video).
   - Cho phép **co giãn tùy ý (Resize)** bằng cách kéo 4 góc (`nw`, `ne`, `sw`, `se`).
   - Cung cấp thanh điều khiển phụ (Toolbar/Sliders) trong Tab Bước 4 (Xuất Video) và Quick Toolbar:
     - Kích thước Width (%)
     - Vị trí X (%) và Y (%)
     - Độ trong suốt / Opacity (10% - 100%)
     - Presets nhanh: Trên-Trái, Trên-Phải, Dưới-Trái, Dưới-Phải, Giữa màn hình.
     - Nút ẩn/hiện khung logo trên preview.

3. **Xử lý ghép vào Video (Backend FFmpeg Processing):**
   - Tích hợp vào hàm `merge_audio_segments_to_video()` trong `app/merger.py`.
   - Nhận cấu hình `logo_box`:
     ```python
     {
         "enabled": bool,
         "image_path": str,    # Đường dẫn file logo hợp lệ
         "x": float,           # Tọa độ X tính theo % chiều rộng video
         "y": float,           # Tọa độ Y tính theo % chiều cao video
         "w": float,           # Chiều rộng logo tính theo % chiều rộng video
         "h": float,           # Chiều cao logo tính theo % chiều cao video (tùy chọn)
         "opacity": float,     # 0.0 -> 1.0 (mặc định 1.0)
         "keep_aspect": bool   # Giữ tỷ lệ khung hình logo (mặc định True)
     }
     ```
   - Xây dựng filter graph:
     - Input logo đưa vào sau cùng để không làm lệch chỉ số index của audio TTS.
     - Filter scale logo theo tỷ lệ video: `scale=w={target_w}:h=-1` (hoặc `force_original_aspect_ratio=decrease`).
     - Filter opacity nếu `< 1.0`: `format=rgba,colorchannelmixer=aa={opacity}`.
     - Overlay vào luồng video: `overlay=x={pos_x}:y={pos_y}`.
   - Hoạt động trơn tru cùng với Mask Blur/Solid và Hardsub Burn-in mà không bị xung đột.

---

## 2. API Contract & Data Model

### API Endpoints
1. `POST /api/project/{project_id}/logo`
   - Payload: `multipart/form-data` with `file: UploadFile`.
   - Response: `{"status": "ok", "logo_url": "/api/project/{project_id}/logo", "filename": str}`.
2. `GET /api/project/{project_id}/logo`
   - Response: Image stream (`FileResponse`).
3. `POST /api/project/{project_id}/render`
   - Thêm trường `logo_box: Optional[Dict[str, Any]] = None` vào `ProjectRenderRequest`.

---

## 3. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
- [x] Có thể tải file logo PNG/JPG lên một project.
- [x] Hiển thị live preview logo trong `bbox-logo` trên canvas xem trước.
- [x] Kéo thả và thay đổi kích thước logo mượt mà trực tiếp trên video.
- [x] Chỉnh sliders và chọn vị trí mẫu (Top-Right, etc.) cập nhật ngay lập tức.
- [x] Khi bấm Render, FFmpeg sinh video thành phẩm có logo đúng vị trí, tỷ lệ và độ mờ đục.
- [x] Không ảnh hưởng đến quá trình tách tiếng, dịch, TTS và burn sub.

