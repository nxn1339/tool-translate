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
