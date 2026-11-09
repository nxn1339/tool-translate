# Bằng Chứng Nghiệm Thu: Khắc Phục Lỗi 405 Cho Endpoint `/api/tts-preview`

## 1. Kết Quả Kiểm Thử Độc Lập
Đã thực thi kiểm thử tích hợp trực tiếp thông qua FastAPI `TestClient`:
- **POST `/api/tts-preview`**:
  - Request: `{"voice": "capcut_cogaithoatngon", "text": "Xin chào"}`
  - HTTP Status: **`200 OK`**
  - Content-Type: `audio/mpeg`
  - Kích thước payload: `17,760 bytes`
- **GET `/api/tts-preview`**:
  - Request: `?voice=capcut_cogaithoatngon`
  - HTTP Status: **`200 OK`**
  - Content-Type: `audio/mpeg`
  - Kích thước payload: `95,040 bytes`

## 2. Chi Tiết Thay Đổi
- **`app/main.py`**:
  - Khai báo model `TTSPreviewRequest`.
  - Khai báo route `@app.post("/api/tts-preview")` và `@app.get("/api/tts-preview")`.
  - Tích hợp cache audio mẫu trong `temp/previews/` để phát tức thời khi bấm lại.
  - Thêm `import hashlib` xử lý hash text.
- **`app/static/app.js`**:
  - Nâng cấp `btnStoryPreviewVoice`: hỗ trợ toggle Play/Stop, hiển thị loading spinner `fa-spinner` và tự động khôi phục icon khi kết thúc bài đọc.
- **`app/static/index.html`**:
  - Cập nhật phiên bản script lên `app.js?v=54` để chống cache trình duyệt.

