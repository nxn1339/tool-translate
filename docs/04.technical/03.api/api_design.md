# API Design - Đặc tả giao diện lập trình

## Danh sách API Endpoints

| API ID | Method | Endpoint | Mô tả | Tham số chính | Response code |
|---|---|---|---|---|---|
| `API-001` | `POST` | `/api/translate` | Khởi tạo tác vụ dịch và lồng tiếng | `url`, `voice`, `source_lang`, `bg_volume`, `tts_volume`, `bilibili_cookie` | 200, 400 |
| `API-002` | `GET` | `/api/status/{task_id}` | Lấy trạng thái và tiến độ xử lý | `task_id` (path) | 200, 404 |
| `API-003` | `GET` | `/api/download/{task_id}` | Tải video thành phẩm mp4 | `task_id` (path) | 200, 404 |

## Chi tiết Endpoint

### 1. `POST /api/translate` (`API-001`)
- **Request Body (JSON):**
```json
{
  "url": "https://www.bilibili.com/video/BV1xx411c7mD",
  "voice": "tiktok_girl",
  "source_lang": "Chinese",
  "bg_volume": 0.15,
  "tts_volume": 1.0,
  "bilibili_cookie": "SESSDATA=xxxx..."
}
```
- **Response (200 OK):**
```json
{
  "task_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "status": "pending"
}
```

### 2. `GET /api/status/{task_id}` (`API-002`)
- **Response (200 OK):**
```json
{
  "status": "downloading" | "translating" | "tts" | "merging" | "completed" | "failed",
  "progress": 45,
  "message": "Đang nhận dạng giọng nói tiếng Trung và dịch sang tiếng Việt...",
  "video_url": "/api/download/c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "error": null
}
```

### 3. `GET /api/download/{task_id}` (`API-003`)
- **Response (200 OK):**
  - Content-Type: `video/mp4`
  - Content-Disposition: `attachment; filename="translated_c9bf9e57.mp4"`
