# Decision Log - Nhật ký quyết định kiến trúc & kỹ thuật

| Decision ID | Tiêu đề quyết định | Người quyết định | Ngày | Lý do / Đánh giá giải pháp | Trạng thái |
|---|---|---|---|---|---|
| `DEC-001` | Chạy Whisper STT cục bộ thay vì gọi Cloud API | TechLead | 2026-08-01 | Miễn phí, không phụ thuộc quota/API key, đảm bảo quyền riêng tư dữ liệu | Approved |
| `DEC-002` | Dùng Microsoft Edge TTS thay vì Google Translate TTS | TechLead | 2026-08-05 | Giọng đọc Neural tiếng Việt (Hoài My, Nam Minh) tự nhiên, truyền cảm, hỗ trợ chỉnh rate/pitch | Approved |
| `DEC-003` | Lưu trạng thái tác vụ trong RAM (`tasks_db` dict) | TechLead | 2026-08-10 | Phù hợp công cụ cá nhân / local running, không cần cài đặt Redis/PostgreSQL phức tạp | Approved |
| `DEC-004` | Bổ sung cơ chế tự sinh `buvid3/buvid4` cookie | TechLead | 2026-08-15 | Bilibili chặn tải video với lỗi HTTP 412 nếu thiếu thông số anti-bot thiết bị | Approved |
| `DEC-005` | Áp dụng cấu trúc tài liệu Enterprise Source-of-Truth | PM / TechLead | 2026-10-24 | Chuẩn hóa quy trình quản lý, tăng tính minh bạch và hỗ trợ phối hợp giữa các AI Agents | Approved |
