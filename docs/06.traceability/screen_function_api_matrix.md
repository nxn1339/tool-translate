# Screen - Function - API Matrix

Ma trận ánh xạ tương tác giao diện người dùng đến các hàm xử lý frontend và endpoint API backend.

| Màn hình | Tên màn hình | Action / Function ID | Tương tác người dùng | API ID | Method | Endpoint URL | Xử lý Backend |
|---|---|---|---|---|---|---|---|
| `APP-001` | Main Dashboard | `FUNC-001` | Nhấn nút "Bắt đầu dịch & lồng tiếng" | `API-001` | `POST` | `/api/translate` | `start_translation` -> `process_video_pipeline` |
| `APP-001` | Main Dashboard | `FUNC-002` | Trình duyệt tự động poll tiến độ mỗi 2s | `API-002` | `GET` | `/api/status/{task_id}` | `get_task_status` (đọc `tasks_db`) |
| `APP-001` | Main Dashboard | `FUNC-003` | Nhấn nút "Tải video hoàn thành" | `API-003` | `GET` | `/api/download/{task_id}` | `download_video` (FileResponse) |
| `APP-001` | Main Dashboard | `FUNC-004` | Kéo thanh trượt âm lượng gốc/TTS | Client-only | N/A | N/A | Gửi kèm trong payload `API-001` |
| `APP-001` | Main Dashboard | `FUNC-005` | Nhập cookie SESSDATA thủ công | Client-only | N/A | N/A | Gửi kèm trong payload `API-001` |
