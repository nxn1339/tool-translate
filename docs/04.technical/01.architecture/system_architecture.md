# System Architecture - Kiến trúc hệ thống tool-translate

## 1. Tổng quan kiến trúc

Hệ thống được thiết kế theo mô hình Monolith tinh gọn, kết hợp FastAPI backend phục vụ cả API lẫn static frontend, cùng các background worker pipeline điều khiển công cụ AI xử lý đa phương tiện.

```text
[ Browser Client (HTML/CSS/JS) ]
             |
             | HTTP REST / Polling (Port 8080)
             v
   [ FastAPI Application (app/main.py) ]
       |-- Static File Mount (app/static)
       |-- In-memory Task DB (tasks_db)
       |-- BackgroundTasks Worker
             |
             +---> [ 1. Downloader (yt-dlp) ] --------> Bilibili CDN
             |
             +---> [ 2. Speech-to-Text (Whisper base) ] -> Local GPU/CPU
             |
             +---> [ 3. Translator (deep-translator) ] -> Google Translate API
             |
             +---> [ 4. TTS Generator (edge-tts) ] ------> Microsoft Edge Neural TTS
             |
             +---> [ 5. Media Mixer (FFmpeg) ] ---------> Local Binary -> Output MP4
```

## 2. Các tầng thành phần (Layer Breakdown)

### 2.1. Presentation Layer (app/static/)
- Giao diện người dùng đơn trang (SPA) xây dựng bằng HTML5 semantic, Vanilla CSS3 với phong cách hiện đại và JavaScript thuần.
- Chức năng: Nhập URL video, chọn giọng đọc, tinh chỉnh âm lượng nhạc nền/lồng tiếng, nhập Cookie/SESSDATA và theo dõi trạng thái tiến độ thời gian thực.

### 2.2. API & Routing Layer (app/main.py)
- Framework: FastAPI (Uvicorn ASGI server).
- Cung cấp REST endpoints:
  - `POST /api/translate`: Nhận request và đưa tác vụ vào hàng đợi `BackgroundTasks`.
  - `GET /api/status/{task_id}`: Trả về trạng thái tiến độ (0% - 100%) và thông điệp xử lý hiện tại.
  - `GET /api/download/{task_id}`: Cung cấp luồng stream file video đã lồng tiếng hoàn tất.

### 2.3. Pipeline & Worker Layer
- **Downloader (`app/downloader.py`):** Bọc thư viện `yt-dlp`, tự động phân tích và tạo cookie Netscape với `buvid3/buvid4` chống lỗi HTTP 412.
- **Transcriber & Translator (`app/translator.py`):**
  - Chạy mô hình Whisper `base` cục bộ để nhận dạng giọng nói, xuất các segments kèm `start` và `end` timestamp.
  - Dùng `deep-translator` dịch từng câu sang tiếng Việt.
- **TTS Synthesizer (`app/tts.py`):**
  - Giao tiếp bất đồng bộ qua `edge-tts` với các Neural Voice tiếng Việt (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`).
  - Có cơ chế lọc ký tự ẩn, sanitize text và retry 3 lần kèm fallback đoạn âm thanh im lặng (anullsrc).
- **Media Mixer (`app/merger.py`):**
  - Sử dụng FFmpeg filter_complex: dùng `adelay` để đặt từng phân đoạn lồng tiếng vào đúng mốc thời gian, dùng `amix` với `normalize=0` để ghép các voice segments, sau đó hòa trộn với âm thanh nền của video gốc theo tỷ lệ âm lượng cấu hình.

## 3. Quản lý lưu trữ tạm thời (Storage Strategy)
- Thư mục làm việc: `app/temp/{task_id}/`
- Mỗi tác vụ tạo một thư mục con riêng biệt chứa:
  - `input_video.mp4`: Video gốc.
  - `input_audio.wav`: Audio tách từ video gốc.
  - `cookies_temp.txt`: Cookie tạm dùng cho yt-dlp.
  - `segment_*.mp3`: Các file audio TTS từng phân đoạn.
  - `output_dubbed.mp4`: Video thành phẩm hoàn thiện.
