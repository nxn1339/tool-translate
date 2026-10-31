# Dev Task List - Danh sách tác vụ lập trình (Code Implementation)

### 1. Refactor & Bugfix (Current Sprint)

| Dev Task ID | Slice | Tên task | Liên kết | Owner | Dependency | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| `DEV-001` | `VS-001` | Cập nhật logic tìm kiếm `ffmpeg/ffmpeg.exe` trong `app/downloader.py` và `run.py` | `TASK-003`, `REQ-010` | Dev | `TASK-002` | Nhận diện thành công `ffmpeg.exe` trong thư mục `ffmpeg/` mà không tải lại | Done |
| `DEV-002` | Foundation | Chuyển đổi file `README.md` từ UTF-16LE sang UTF-8 tiêu chuẩn | `TASK-003` | Dev | Không có | File hiển thị đúng tiếng Việt trên mọi editor, mime-type là `text/markdown` | Done |
| `DEV-003` | `VS-001` | Dọn dẹp file zip thừa `ffmpeg_20260624145236.zip` ở thư mục gốc | `TASK-003` | Dev | `DEV-001` | Giải phóng ~75MB dung lượng đĩa của repo | Open |

### 2. Feature Implementation (Completed & Backlog)

| Dev Task ID | Slice | Tên task | Liên kết | Owner | Dependency | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| `DEV-004` | `VS-005` | Thêm background scheduler định kỳ xóa thư mục `app/temp/{task_id}` quá hạn | `TASK-004` | Dev | `DEV-001` | Thư mục temp cũ được dọn sạch không làm tràn ổ đĩa | Open |
| `DEV-005` | `VS-002` | Bổ sung API endpoint chỉnh sửa phụ đề trong danh sách câu thoại | `TASK-005` | Dev | `DEV-004` | Người dùng có thể chỉnh sửa lời dịch trước khi sinh giọng đọc | Done |
| `DEV-006` | `VS-005` | Dựng giao diện Studio 4 Bước, Canvas kéo thả Bounding Box | `TASK-006`, `REQ-013`..`015` | Dev | Không có | Giao diện 4 bước mượt mà, kéo thả 2 box chuẩn tọa độ % | Done |
| `DEV-007` | `VS-005` | Triển khai module `app/ocr_detector.py` (Paddle/RapidOCR frame sampling & gom timeline) | `TASK-007`, `REQ-016` | Dev | `DEV-006` | Trích xuất chữ tiếng Trung & timestamp câu chuẩn | Done |
| `DEV-008` | `VS-005` | Nâng cấp `app/merger.py` (FFmpeg Masking che sub cũ & Hardsub burning ASS) | `TASK-008`, `REQ-017` | Dev | `DEV-007` | Video xuất ra che sạch sub cũ, in sub mới đúng tọa độ | Done |
| `DEV-009` | `VS-005` | Bổ sung endpoint xuất tệp phụ đề `.srt` (`/api/project/{id}/subtitles.srt`) | `TASK-008`, `REQ-018` | Dev | `DEV-008` | Trả về file .srt chuẩn SubRip format tải về được | Done |
| `DEV-010` | `VS-005` | Bổ sung endpoint `/api/tts-free` và lưu cấu hình LocalStorage / Project | `TASK-009`, `REQ-019` | Dev | `DEV-006` | Đọc text tự do thành MP3 và lưu cấu hình liên phiên | Done |
| `DEV-011` | `VS-006` | Bổ sung API Upload và Get thông tin Logo dự án (`/api/project/{id}/logo`) | `TASK-010`, `REQ-020`, `REQ-021` | Dev | `DEV-010` | Upload file ảnh logo, lưu vào thư mục project và trả về URL ảnh | Done |
| `DEV-012` | `VS-006` | Tích hợp FFmpeg Video Filter cho Watermark/Logo Overlay (`app/merger.py`) | `TASK-010`, `REQ-022`, `REQ-023` | Dev | `DEV-011` | Ghép logo đúng kích thước, vị trí tọa độ %, độ mờ opacity trên luồng video | Done |
| `DEV-013` | `VS-006` | Xây dựng giao diện Logo Overlay Toolbar & Canvas Transform Box (`app.js`, `index.html`) | `TASK-010`, `REQ-024`, `REQ-025` | Dev | `DEV-012` | Kéo thả, co giãn 8 anchor points, phím tắt xóa/reset, đồng bộ Step 3 & Step 4 | Done |
| `DEV-014` | `VS-004` | Tích hợp CapCut Neural TTS (`app/capcut_tts.py`) và RVC Voice Conversion (`app/rvc_client.py`) | `TASK-011`, `REQ-005` | Dev | `DEV-007` | Hỗ trợ giọng CapCut đa dạng và chuyển đổi âm sắc qua mô hình RVC | Done |
