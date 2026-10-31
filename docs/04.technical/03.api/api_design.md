# API Design - Đặc tả toàn bộ giao diện lập trình (Enterprise Source-of-Truth)

Owner: TechLead  
Status: Approved  

## 1. Danh sách API Endpoints Toàn Hệ Thống

| API ID | Method | Endpoint | Slice | Mô tả | Mã phản hồi |
|---|---|---|---|---|---|
| `API-001` | `POST` | `/api/projects` | `VS-005` | Khởi tạo dự án dựng video mới | 200 |
| `API-002` | `GET` | `/api/projects` | `VS-005` | Danh sách tất cả các dự án đã lưu | 200 |
| `API-003` | `GET` | `/api/projects/{id}` | `VS-005` | Lấy chi tiết thông tin dự án & phụ đề | 200, 404 |
| `API-004` | `PATCH` | `/api/projects/{id}` | `VS-005` | Cập nhật metadata, cấu hình hộp box, sub styling | 200, 404 |
| `API-005` | `DELETE`| `/api/projects/{id}` | `VS-005` | Xóa vĩnh viễn dự án và thư mục tạm | 200, 404 |
| `API-006` | `POST` | `/api/project/download` | `VS-001` | Tải video từ link Bilibili/YouTube vào dự án | 200, 400 |
| `API-007` | `GET` | `/api/project/{id}/status` | `VS-002` | Polling tiến độ xử lý tác vụ nền | 200, 404 |
| `API-008` | `GET` | `/api/project/{id}/video-raw` | `VS-005` | Stream video gốc phục vụ căn chỉnh Bounding Box | 200, 404 |
| `API-009` | `POST` | `/api/project/{id}/transcribe` | `VS-005` | Khởi động trích xuất OCR tiếng Trung hoặc Whisper | 200, 400 |
| `API-010` | `GET` | `/api/project/{id}/segments` | `VS-005` | Lấy danh sách câu phụ đề kèm mốc thời gian | 200, 404 |
| `API-011` | `PUT` | `/api/project/{id}/segments` | `VS-005` | Cập nhật nội dung dịch và mốc thời gian phụ đề | 200, 404 |
| `API-012` | `POST` | `/api/project/{id}/preview-audio` | `VS-004` | Tổng hợp nhanh file âm thanh lồng tiếng nghe thử | 200, 400 |
| `API-013` | `POST` | `/api/project/{id}/render` | `VS-005` | Xuất video cuối (Ghép sub, lồng tiếng, mask, logo) | 200, 400 |
| `API-014` | `GET` | `/api/project/{id}/video-dubbed`| `VS-002` | Stream video thành phẩm hoàn chỉnh | 200, 404 |
| `API-015` | `GET` | `/api/project/{id}/download` | `VS-001` | Tải về file video MP4 hoàn chỉnh | 200, 404 |
| `API-016` | `GET` | `/api/project/{id}/download-audio`| `VS-004` | Tải về file âm thanh giọng lồng tiếng MP3 | 200, 404 |
| `API-017` | `GET` | `/api/project/{id}/subtitles` | `VS-005` | Xuất file phụ đề .SRT (tiếng Trung, tiếng Việt hoặc Song ngữ) | 200, 404 |
| `API-018` | `POST` | `/api/project/{id}/import-srt`| `VS-005` | Gắn tệp phụ đề .SRT tiếng Việt bên ngoài vào dự án | 200, 400 |
| `API-019` | `POST` | `/api/project/{id}/logo` | `VS-006` | Tải lên file ảnh Logo/Watermark vào dự án | 200, 400 |
| `API-020` | `GET` | `/api/project/{id}/logo` | `VS-006` | Stream file ảnh Logo của dự án | 200, 404 |
| `API-021` | `GET` | `/api/rvc-models` | `VS-007` | Quét danh sách mô hình giọng RVC (.pth, .index) | 200 |
| `API-022` | `POST` | `/api/tts-free` | `VS-004` | Tiện ích chuyển văn bản thành âm thanh đọc thử | 200, 400 |

---

## 2. Chi tiết Endpoints Quan Trọng

### 2.1 Quản lý Logo / Watermark (`API-019`, `API-020`)
- **Tải Logo:** `POST /api/project/{id}/logo` (multipart/form-data, file ảnh PNG/JPG/WebP/SVG <= 10MB).
- **Lấy Logo:** `GET /api/project/{id}/logo` (trả về Content-Type ảnh tương ứng).

### 2.2 Xuất video tổng thể (`API-013`)
- **Payload:** Hỗ trợ đầy đủ `voice`, `rvc_model`, `rvc_pitch`, `bg_volume`, `tts_volume`, `mask_box`, `sub_box`, `sub_styling`, `logo_box`, `auto_extend_video`.
