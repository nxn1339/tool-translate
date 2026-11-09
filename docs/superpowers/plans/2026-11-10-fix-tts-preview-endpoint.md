# Kế Hoạch Triển Khai: Khắc Phục Lỗi 405 Cho Endpoint `/api/tts-preview`

## Các Bước Triển Khai

### Bước 1: Khai Báo Model & Route Trong `app/main.py`
- Bổ sung `TTSPreviewRequest`.
- Đăng ký `@app.post("/api/tts-preview")` và `@app.get("/api/tts-preview")`.
- Sinh audio mẫu và trả về `FileResponse`.

### Bước 2: Nâng Cấp Trải Nghiệm Nút Nghe Thử Trong `app/static/app.js`
- Quản lý đối tượng `Audio` để tránh phát đè nhiều âm thanh cùng lúc.
- Thêm hiệu ứng Đang tải (`fa-spinner`) và nút Dừng (`fa-stop`).

### Bước 3: Kiểm Thử Độc Lập
- Chạy request kiểm thử `POST /api/tts-preview` với giọng TikTok mẫu.
- Xác nhận mã phản hồi HTTP `200 OK` kèm dữ liệu nhị phân `audio/mpeg`.

### Bước 4: Lưu Bằng Chứng Nghiệm Thu
- Lưu kết quả vào `docs/superpowers/evidence/2026-11-10-fix-tts-preview-endpoint.md`.

