# Task List - Quản lý công việc dự án (PM Role)

| Task ID | Tên task | Liên kết tài liệu | Output file | Owner | Reviewer | Dependency | DoD | Priority | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|
| `TASK-001` | Thiết lập bộ tài liệu Source-of-Truth theo chuẩn Enterprise | `REQ-001` -> `REQ-010` | `docs/**` | PM/All | TechLead | Không có | Cấu trúc docs hoàn chỉnh, đủ 8 phân vùng | High | Done |
| `TASK-002` | Phân tích giải pháp fix lỗi lệch thư mục binary FFmpeg | `REQ-010` | `docs/04.technical/09.refactor/ffmpeg-path-fix-solution-brief.md` | TechLead | PM | `TASK-001` | Solution brief được phê duyệt | High | Done |
| `TASK-003` | Triển khai fix đường dẫn FFmpeg và chuyển mã README sang UTF-8 | `DEV-001`, `DEV-002` | `run.py`, `app/downloader.py`, `README.md` | Dev | QA | `TASK-002` | Chạy tool nhận FFmpeg local không cần tải lại | High | Done |
| `TASK-004` | Xây dựng cơ chế Auto-cleanup thư mục tạm `app/temp` | `REQ-011` | `app/main.py` | Dev | TechLead | `TASK-003` | Xóa temp sau khi download hoặc sau 1 giờ | Medium | Open |
| `TASK-005` | Nghiên cứu tính năng Subtitle Preview & Editor trước khi render TTS | `REQ-012` | `docs/02.product/02.requirement/VS-002.md` | BA | TechLead | `TASK-001` | Bản đặc tả tính năng sửa phụ đề | Medium | Done |
| `TASK-006` | Thiết kế giao diện Studio 4 Bước & Canvas Bounding Box kéo thả | `REQ-013` -> `REQ-015` | `app/static/index.html`, `app/static/app.js` | UI/Dev | TechLead | `TASK-001` | Giao diện 4 bước mượt mà, kéo thả 2 box chuẩn tọa độ % | High | Done |
| `TASK-007` | Triển khai module Video OCR (Paddle/RapidOCR) trích xuất timeline | `REQ-016` | `app/ocr_detector.py`, `app/main.py` | Dev | TechLead | `TASK-006` | Quét frame vùng box ra text tiếng Trung & timestamp chuẩn | High | Done |
| `TASK-008` | Triển khai FFmpeg Subtitle Masking, Hardsub ASS & Export .srt | `REQ-017`, `REQ-018` | `app/merger.py` | Dev | QA | `TASK-007` | Video xuất ra che sạch sub cũ, in sub mới và tải được .srt | High | Done |
| `TASK-009` | Tích hợp đồng bộ Cài đặt & Quản lý Dự án nhiều phiên | `REQ-019` | `app/static/app.js`, `app/main.py` | Dev | PM | `TASK-006` | Cấu hình lưu trữ và nạp lại chính xác qua các Step/Project | Medium | Done |
| `TASK-010` | Triển khai tính năng Ghép Logo / Watermark co giãn tùy ý vào video | `REQ-020` -> `REQ-025`, `VS-006` | `app/main.py`, `app/merger.py`, `app/static/*` | Dev | QA | `TASK-008` | Tải ảnh logo, kéo thả 8 điểm co giãn trên Canvas, FFmpeg render chuẩn tỷ lệ và vị trí | High | Done |
| `TASK-011` | Tích hợp giọng đọc CapCut Neural TTS & chuyển đổi giọng RVC | `REQ-005`, `VS-004` | `app/capcut_tts.py`, `app/rvc_client.py` | Dev | TechLead | `TASK-007` | Lồng tiếng mượt mà qua CapCut API, clone giọng qua RVC server | High | Done |
