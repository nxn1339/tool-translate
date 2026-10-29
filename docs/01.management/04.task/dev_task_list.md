# Dev Task List - Danh sách tác vụ lập trình (Code Implementation)

### 1. Refactor & Bugfix (Current Sprint)

| Dev Task ID | Slice | Tên task | Liên kết | Owner | Dependency | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| `DEV-001` | `VS-001` | Cập nhật logic tìm kiếm `ffmpeg/ffmpeg.exe` trong `app/downloader.py` và `run.py` | `TASK-003`, `REQ-010` | Dev | `TASK-002` | Nhận diện thành công `ffmpeg.exe` trong thư mục `ffmpeg/` mà không tải lại | Open |
| `DEV-002` | Foundation | Chuyển đổi file `README.md` từ UTF-16LE sang UTF-8 tiêu chuẩn | `TASK-003` | Dev | Không có | File hiển thị đúng tiếng Việt trên mọi editor, mime-type là `text/markdown` | Open |
| `DEV-003` | `VS-001` | Dọn dẹp file zip thừa `ffmpeg_20260624145236.zip` ở thư mục gốc | `TASK-003` | Dev | `DEV-001` | Giải phóng ~75MB dung lượng đĩa của repo | Open |

### 2. Feature Extension (Backlog)

| Dev Task ID | Slice | Tên task | Liên kết | Owner | Dependency | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| `DEV-004` | `VS-005` | Thêm background scheduler định kỳ xóa thư mục `app/temp/{task_id}` quá hạn | `TASK-004` | Dev | `DEV-001` | Thư mục temp cũ được dọn sạch không làm tràn ổ đĩa | Open |
| `DEV-005` | `VS-002` | Bổ sung API endpoint `/api/segments/{task_id}` cho phép frontend chỉnh sửa text | `TASK-005` | Dev | `DEV-004` | Người dùng có thể chỉnh sửa lời dịch trước khi sinh giọng đọc | Open |
| `DEV-006` | `VS-005` | Dựng giao diện 3 Tab, Canvas kéo thả 2 Bounding Box và Tab 3 Cài đặt | `TASK-006`, `REQ-013`..`015` | Dev | Không có | Giao diện 3 tab mượt mà, kéo thả 2 box chuẩn tọa độ % | Implemented |
| `DEV-007` | `VS-005` | Triển khai module `app/ocr.py` (RapidOCR frame sampling & gom timeline) | `TASK-007`, `REQ-016` | Dev | `DEV-006` | Trích xuất chữ tiếng Trung & timestamp câu chuẩn | Implemented |
| `DEV-008` | `VS-005` | Nâng cấp `app/merger.py` (FFmpeg Masking che sub cũ & Hardsub burning) | `TASK-008`, `REQ-017` | Dev | `DEV-007` | Video xuất ra che sạch sub cũ, in sub mới đúng tọa độ | Implemented |
| `DEV-009` | `VS-005` | Bổ sung endpoint xuất tệp phụ đề `.srt` (`/api/subtitles/{task_id}`) | `TASK-008`, `REQ-018` | Dev | `DEV-008` | Trả về file .srt chuẩn SubRip format tải về được | Implemented |
| `DEV-010` | `VS-005` | Bổ sung endpoint `/api/tts-free` và lưu cấu hình LocalStorage | `TASK-009`, `REQ-019` | Dev | `DEV-006` | Đọc text tự do thành MP3 và lưu cấu hình liên tab | Implemented |


