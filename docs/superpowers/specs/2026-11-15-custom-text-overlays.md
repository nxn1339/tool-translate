# Feature Specification: Custom Text Overlays on Video (Text Tự Do & Watermark Chữ)

- **Feature Name:** Custom Text Overlays on Video (Chèn Text Tự Do & Watermark Chữ trên màn hình video)
- **Status:** Approved / In Progress
- **Created Date:** 2026-11-15
- **Scope:** Full-stack (Backend Pillow graphic generator & FFmpeg overlay integration, FastAPI endpoints & meta sync, Frontend interactive Canvas Drag & Resize, Presets & Controls in Step 5 & Step 6).

---

## 1. Yêu Cầu Nghiệp Vụ (Requirements)

1. **Thêm text tự do trên video:**
   - Cho phép người dùng thêm nhiều dòng chữ tự do (Watermark text, tiêu đề phụ, kêu gọi hành động) hiển thị xuyên suốt video.
   - Hỗ trợ thêm/xóa/sửa từng mục text độc lập.
   - Bật / tắt tính năng Text Overlays hoặc từng text riêng lẻ.

2. **Cấu hình mẫu sẵn (Presets) theo yêu cầu thực tế:**
   - Cung cấp nút 1-click **"Áp dụng mẫu Hạt Tiêu Vietsub"** để tự động khởi tạo 2 text chuẩn như video mẫu:
     - **Text 1 (Kêu gọi đăng ký):**
       - Nội dung: `Đăng ký để không bỏ lỡ video mới`
       - Vị trí: Góc trên-trái (`x: 2%`, `y: 3%`)
       - Kiểu dáng: Khung hộp nền trắng bo góc mềm mại, chữ đen đậm, dễ đọc trên mọi cảnh phim.
     - **Text 2 (Chữ ký thương hiệu):**
       - Nội dung: `Hạt Tiêu Vietsub`
       - Vị trí: Vùng ngực/vai phải nhân vật, phía trên phụ đề (`x: 72%`, `y: 74%`)
       - Kiểu dáng: Chữ trắng in nghiêng (*italic*), không nền, đổ bóng nhẹ để đọc rõ mà không che nội dung.

3. **Tương tác trực quan trên Video Canvas (Preview Overlay):**
   - Hiển thị trực tiếp các khung chữ trên `#canvas-overlay` đồng bộ với kích thước video preview.
   - Cho phép dùng chuột kéo thả (`drag`) trực tiếp từng khung chữ đến bất kỳ tọa độ nào trên video.
   - Thanh điều khiển trực quan:
     - Ô nhập nội dung chữ tiếng Việt (UTF-8).
     - Slider tọa độ X (%) và Y (%).
     - Cỡ chữ (Font size).
     - Bật/tắt khung nền, màu nền, độ mờ nền, bo góc (radius).
     - Màu chữ, in đậm (bold), in nghiêng (italic), đổ bóng (shadow).
   - Tự động lưu trạng thái vào `project.json` để giữ cấu hình khi mở lại dự án.

4. **Xử lý Render Video Backend (Pillow + FFmpeg):**
   - Sinh ảnh PNG trong suốt độ phân giải gốc của video bằng Pillow.
   - Dùng phông chữ chuẩn `Nunito` hỗ trợ tiếng Việt có dấu 100%, không bị lỗi font trên Windows.
   - Ghép ảnh PNG vào video qua filter `overlay=0:0` trong FFmpeg `merge_audio_segments_to_video()`.

---

## 2. API Contract & Data Model

### Data Model: `TextOverlayItem`
```python
{
    "id": str,                 # e.g. "text_sub_1", "text_sub_2"
    "enabled": bool,            # True / False
    "text": str,                # e.g. "Đăng ký để không bỏ lỡ video mới"
    "x": float,                 # Tọa độ X tính theo % chiều rộng video (0.0 -> 100.0)
    "y": float,                 # Tọa độ Y tính theo % chiều cao video (0.0 -> 100.0)
    "font_size": int,           # Kích thước cơ sở (mặc định 20 - 24)
    "color": str,               # Mã màu hex chữ (e.g. "#000000", "#FFFFFF")
    "bold": bool,               # In đậm
    "italic": bool,             # In nghiêng
    "shadow": bool,             # Đổ bóng chữ
    "bg_enabled": bool,         # Có vẽ hộp nền hay không
    "bg_color": str,            # Mã màu hex nền (e.g. "#FFFFFF")
    "bg_opacity": float,        # Độ mờ nền (0.0 -> 1.0)
    "bg_radius": int,           # Bán kính bo góc (pixels tại chuẩn 720p)
    "padding_x": int,           # Khoảng đệm ngang
    "padding_y": int            # Khoảng đệm dọc
}
```

### Request Models (`app/main.py`)
- Cập nhật `ProjectRenderRequest` thêm:
  `text_overlays: Optional[List[Dict[str, Any]]] = None`
- Lưu `text_overlays` trong metadata của project (`save_project_meta`).

