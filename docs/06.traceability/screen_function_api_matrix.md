# Screen - Function - API Matrix

Ma trận ánh xạ tương tác giao diện người dùng đến các hàm xử lý frontend và endpoint API backend.

| Màn hình | Tên màn hình | Action / Function ID | Tương tác người dùng | API ID | Method | Endpoint URL | Xử lý Backend |
|---|---|---|---|---|---|---|---|
| `APP-001` | Main Dashboard | `FUNC-001` | Nhấn nút "Bắt đầu dịch & lồng tiếng" | `API-001` | `POST` | `/api/translate` | `start_translation` -> `process_video_pipeline` |
| `APP-001` | Main Dashboard | `FUNC-002` | Trình duyệt tự động poll tiến độ mỗi 2s | `API-002` | `GET` | `/api/status/{task_id}` | `get_task_status` (đọc `tasks_db`) |
| `APP-001` | Main Dashboard | `FUNC-003` | Nhấn nút "Tải video hoàn thành" | `API-003` | `GET` | `/api/download/{task_id}` | `download_video` (FileResponse) |
| `APP-001` | Main Dashboard | `FUNC-004` | Kéo thanh trượt âm lượng gốc/TTS | Client-only | N/A | N/A | Gửi kèm trong payload `API-001` |
| `APP-001` | Main Dashboard | `FUNC-005` | Nhập cookie SESSDATA thủ công | Client-only | N/A | N/A | Gửi kèm trong payload `API-001` |
| `APP-002` | Multi-Step Studio | `FUNC-006` | Chuyển đổi giữa 4 Bước quy trình (Nạp -> OCR -> Dịch/Logo -> Xuất) | Client-only | N/A | N/A | Chuyển đổi hiển thị panel, giữ trạng thái dự án |
| `APP-002` | Multi-Step Studio | `FUNC-007` | Kéo thả & co giãn Khung Che Sub cũ (Mask Box) | Client-only | N/A | N/A | Cập nhật tọa độ % `mask_box` trên Canvas |
| `APP-002` | Multi-Step Studio | `FUNC-008` | Kéo thả & định vị Khung Sub Việt (Subtitle Box) | Client-only | N/A | N/A | Cập nhật tọa độ % `sub_box` trên Canvas |
| `APP-002` | Multi-Step Studio | `FUNC-009` | Bật/tắt khóa liên kết đồng bộ vị trí 2 khung | Client-only | N/A | N/A | Bám dính hoặc tách rời tọa độ 2 khung |
| `APP-002` | Multi-Step Studio | `FUNC-010` | Nạp preview video khi dán link/chọn file | `API-007` | `POST` | `/api/video-preview-info` | Bóc metadata & trích frame preview cho canvas |
| `APP-002` | Multi-Step Studio | `FUNC-011` | Nhấn "Bắt đầu quét phụ đề OCR" (Bước 2) | `API-012` | `POST` | `/api/project/{id}/ocr` | Pipeline Paddle/RapidOCR + trích xuất timeline |
| `APP-002` | Multi-Step Studio | `FUNC-012` | Chỉnh sửa lời dịch và nghe thử TTS/RVC (Bước 3) | `API-015` | `POST` | `/api/project/{id}/preview-tts` | Sinh âm thanh nghe thử đoạn thoại |
| `APP-002` | Multi-Step Studio | `FUNC-013` | Nhấn nút "Tải phụ đề (.srt)" | `API-005` | `GET` | `/api/project/{id}/subtitles.srt` | Trả về file text/vtt hoặc srt SubRip format |
| `APP-002` | Multi-Step Studio | `FUNC-014` | Thay đổi cấu hình chung (giọng, volume, sub) | Client-only | N/A | N/A | Đồng bộ tự động vào `localStorage` trình duyệt |
| `APP-002` | Multi-Step Studio | `FUNC-015` | Đọc văn bản tự do & tải MP3 tại Cài đặt | `API-006` | `POST` | `/api/tts-free` | Sinh file MP3 từ text tự do qua Edge-TTS |
| `APP-002` | Multi-Step Studio | `FUNC-016` | Tải lên file ảnh Logo dự án (Bước 3 / Bước 4) | `API-021` | `POST` | `/api/project/{id}/logo` | Lưu file ảnh logo vào thư mục dự án và trả URL |
| `APP-002` | Multi-Step Studio | `FUNC-017` | Lấy thông tin & trạng thái Logo dự án | `API-022` | `GET` | `/api/project/{id}/logo` | Trả về trạng thái `has_logo`, `logo_url`, `config` |
| `APP-002` | Multi-Step Studio | `FUNC-018` | Kéo thả di chuyển, co giãn 8 chốt kích thước Logo | Client-only | N/A | N/A | Cập nhật tọa độ % `logo_box` trên Canvas |
| `APP-002` | Multi-Step Studio | `FUNC-019` | Phím tắt xóa nhanh Delete và chọn Preset vị trí | Client-only | N/A | N/A | Đặt lại tọa độ theo preset hoặc ẩn logo |
| `APP-002` | Multi-Step Studio | `FUNC-020` | Nhấn "Xuất Video Hoàn Chỉnh" (Bước 4) | `API-020` | `POST` | `/api/project/{id}/render` | Render FFmpeg: Masking + Logo Overlay + Hardsub + Audio |
