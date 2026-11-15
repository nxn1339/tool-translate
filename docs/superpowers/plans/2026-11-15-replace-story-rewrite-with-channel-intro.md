# Kế Hoạch Triển Khai: Đổi Tính Năng Xào Nấu Thành Thêm Đoạn Giới Thiệu Kênh

## 1. Mục Tiêu
Thay thế tính năng "Xào Nấu AI" trong Studio Đọc Truyện bằng tính năng "Thêm Đoạn Giới Thiệu Kênh" với bộ template mẫu chuyên nghiệp, khả năng AI tạo lời dẫn hook mở đầu, và nút 1-click chèn vào đầu kịch bản.

---

## 2. Các Bước Triển Khai Chi Tiết

### Bước 1: Cập Nhật Backend (`app/story_tts.py` & `app/main.py`)
- Viết hàm `generate_channel_intro(channel_name: str, story_text: str, style: str)` trong `app/story_tts.py`:
  - Sử dụng Groq (Llama-3.3-70b-versatile) hoặc fallback Gemini.
  - Tối ưu hóa prompt để tạo 1-2 câu hook mở đầu ấn tượng, tròn vành rõ chữ, tối ưu cho giọng đọc AI TikTok.
- Khai báo model `StoryIntroRequest` và endpoint `POST /api/story-tts/generate-intro` trong `app/main.py`.
- Dọn dẹp/giữ tương thích endpoint cũ nếu cần.

### Bước 2: Cập Nhật Giao Diện (`app/static/index.html` & `app/static/style.css`)
- Trong `#story-tts-view` của `app/static/index.html`:
  - Gỡ bỏ khối `.story-rewrite-toolbar`.
  - Thêm khối `.story-intro-toolbar`:
    - Input Tên kênh (`#story-channel-name`)
    - Select Chọn mẫu giới thiệu (`#story-intro-style`)
    - Input / Textarea nội dung intro (`#story-intro-text`)
    - Nút "✨ AI Viết Lời Dẫn Hook" (`#btn-story-ai-intro`)
    - Nút chính "➕ Chèn Vào Đầu Kịch Bản" (`#btn-story-insert-intro`)
- Cập nhật mô tả thẻ Studio Đọc Truyện tại `#home-view`.
- Thêm stylesheet hỗ trợ trong `app/static/style.css`.

### Bước 3: Cập Nhật Logic JavaScript (`app/static/app.js`)
- Trong `initStoryTtsStudio()`:
  - Khởi tạo giá trị tên kênh từ `localStorage` (mặc định `Hạt Tiêu Vietsub`).
  - Lắng nghe thay đổi select mẫu giới thiệu -> tự động cập nhật `#story-intro-text`.
  - Sự kiện click nút AI tạo lời dẫn -> gọi `POST /api/story-tts/generate-intro` -> điền kết quả vào `#story-intro-text`.
  - Sự kiện click nút chèn -> chèn đoạn intro lên đầu `#story-raw-text`, cập nhật thống kê từ/thời lượng (`updateStoryStats()`).

### Bước 4: Kiểm Thử & Nghiệm Thu
- Cập nhật `tests/test_story_tts.py` để kiểm thử sinh đoạn intro và tổng hợp kịch bản có intro.
- Chạy `python -m unittest tests/test_story_tts.py`.
- Ghi nhận bằng chứng tại `docs/superpowers/evidence/2026-11-15-replace-story-rewrite-with-channel-intro.md`.

