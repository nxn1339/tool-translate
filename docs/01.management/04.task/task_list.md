# Task List - Quản lý công việc dự án (PM Role)

| Task ID | Tên task | Liên kết tài liệu | Output file | Owner | Reviewer | Dependency | DoD | Priority | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|
| `TASK-001` | Thiết lập bộ tài liệu Source-of-Truth theo chuẩn Enterprise | `REQ-001` -> `REQ-010` | `docs/**` | PM/All | TechLead | Không có | Cấu trúc docs hoàn chỉnh, đủ 8 phân vùng | High | Done |
| `TASK-002` | Phân tích giải pháp fix lỗi lệch thư mục binary FFmpeg | `REQ-010` | `docs/04.technical/09.refactor/ffmpeg-path-fix-solution-brief.md` | TechLead | PM | `TASK-001` | Solution brief được phê duyệt | High | Done |
| `TASK-003` | Triển khai fix đường dẫn FFmpeg và chuyển mã README sang UTF-8 | `DEV-001`, `DEV-002` | `run.py`, `app/downloader.py`, `README.md` | Dev | QA | `TASK-002` | Chạy tool nhận FFmpeg local không cần tải lại | High | Open |
| `TASK-004` | Xây dựng cơ chế Auto-cleanup thư mục tạm `app/temp` | `REQ-011` | `app/main.py` | Dev | TechLead | `TASK-003` | Xóa temp sau khi download hoặc sau 1 giờ | Medium | Open |
| `TASK-005` | Nghiên cứu tính năng Subtitle Preview & Editor trước khi render TTS | `REQ-012` | `docs/02.product/02.requirement/VS-002.md` | BA | TechLead | `TASK-001` | Bản đặc tả tính năng sửa phụ đề | Medium | Open |
