# Thiết Kế Chi Tiết: Sửa Lỗi 405 Method Not Allowed Cho Endpoint Nghe Thử Giọng `/api/tts-preview`

## 1. Vấn Đề
- Khi nhấn nút "Nghe thử giọng" trong Studio Đọc Truyện, frontend gửi request `POST /api/tts-preview`.
- Backend `app/main.py` chưa khai báo route này nên request rơi vào middleware `StaticFiles`.
- Middleware `StaticFiles` chỉ chấp nhận `GET` và `HEAD`, do đó phản hồi lỗi `405 Method Not Allowed`.

## 2. Giải Pháp Kỹ Thuật
1. **Thêm Pydantic Request Model trong `app/main.py`:**
   ```python
   class TTSPreviewRequest(BaseModel):
       voice: Optional[str] = "capcut_cogaithoatngon"
       text: Optional[str] = None
   ```
2. **Khai báo Endpoint Đa Phương Thức (`POST` & `GET`):**
   - Đăng ký `@app.post("/api/tts-preview")` và `@app.get("/api/tts-preview")`.
   - Lấy text mẫu tương ứng hoặc dùng text gửi lên từ frontend.
   - Hỗ trợ toàn bộ kho giọng TikTok/CapCut (qua `VOICE_PRESETS` và `LEGACY_VOICE_MAP`).
   - Cache file âm thanh mẫu trong `temp/previews/` theo định dạng `preview_{voice}_{hash}.mp3`.
   - Trả về `FileResponse` với MIME `audio/mpeg`.
3. **Cải tiến UX Frontend (`app/static/app.js`):**
   - Hỗ trợ bật/tắt (Toggle Play/Stop) khi đang phát.
   - Hiển thị spinner khi đang tải audio mẫu.
   - Tự động reset nút về trạng thái ban đầu khi phát xong (`onended`).

