# Screen - Function - API Matrix

Ma trận ánh xạ tương tác giao diện người dùng đến các hàm xử lý frontend và endpoint API backend.

| Màn hình | Tên màn hình | Action / Function ID | Tương tác người dùng | API ID | Method | Endpoint URL | Xử lý Backend |
|---|---|---|---|---|---|---|---|
| `APP-001` | Main Dashboard | `FUNC-001` | Nhấn nút "Bắt đầu dịch & lồng tiếng" | `API-001` | `POST` | `/api/translate` | `start_translation` -> `process_video_pipeline` |
| `APP-001` | Main Dashboard | `FUNC-002` | Trình duyệt tự động poll tiến độ mỗi 2s | `API-002` | `GET` | `/api/status/{task_id}` | `get_task_status` (đọc `tasks_db`) |
| `APP-001` | Main Dashboard | `FUNC-003` | Nhấn nút "Tải video hoàn thành" | `API-003` | `GET` | `/api/download/{task_id}` | `download_video` (FileResponse) |
| `APP-001` | Main Dashboard | `FUNC-004` | Kéo thanh trượt âm lượng gốc/TTS | Client-only | N/A | N/A | Gửi kèm trong payload `API-001` |
| `APP-001` | Main Dashboard | `FUNC-005` | Nhập cookie SESSDATA thủ công | Client-only | N/A | N/A | Gửi kèm trong payload `API-001` |
| `APP-002` | Multi-Tab Studio | `FUNC-006` | Chuyển đổi giữa 3 Tab (Có Sub / Không Sub / Cài đặt) | Client-only | N/A | N/A | Chuyển đổi hiển thị panel, giữ trạng thái video |
| `APP-002` | Multi-Tab Studio | `FUNC-007` | Kéo thả & co giãn Khung Che Sub cũ (Mask Box) | Client-only | N/A | N/A | Cập nhật tọa độ % `mask_box` trên Canvas |
| `APP-002` | Multi-Tab Studio | `FUNC-008` | Kéo thả & định vị Khung Sub Việt (Subtitle Box) | Client-only | N/A | N/A | Cập nhật tọa độ % `sub_box` trên Canvas |
| `APP-002` | Multi-Tab Studio | `FUNC-009` | Bật/tắt khóa liên kết đồng bộ vị trí 2 khung | Client-only | N/A | N/A | Bám dính hoặc tách rời tọa độ 2 khung |
| `APP-002` | Multi-Tab Studio | `FUNC-010` | Nạp preview video khi dán link/chọn file | `API-007` | `POST` | `/api/video-preview-info` | Bóc metadata & trích frame 00:02 cho canvas |
| `APP-002` | Multi-Tab Studio | `FUNC-011` | Nhấn "Bắt đầu quét & lồng tiếng" (Tab Có Sub) | `API-004` | `POST` | `/api/translate-ocr` | Pipeline OCR + Masking + TTS + Merge Hardsub |
| `APP-002` | Multi-Tab Studio | `FUNC-012` | Nhấn "Bắt đầu dịch & lồng tiếng" (Tab Không Sub)| `API-001` | `POST` | `/api/translate` | Pipeline Whisper + TTS + Merge Hardsub |
| `APP-002` | Multi-Tab Studio | `FUNC-013` | Nhấn nút "Tải phụ đề (.srt)" | `API-005` | `GET` | `/api/subtitles/{task_id}` | Trả về file text/vtt hoặc srt SubRip format |
| `APP-002` | Multi-Tab Studio | `FUNC-014` | Thay đổi cấu hình chung (giọng, volume, sub) | Client-only | N/A | N/A | Đồng bộ tự động vào `localStorage` trình duyệt |
| `APP-002` | Multi-Tab Studio | `FUNC-015` | Đọc văn bản tự do & tải MP3 tại Tab Cài đặt | `API-006` | `POST` | `/api/tts-free` | Sinh file MP3 từ text tự do qua Edge-TTS |

