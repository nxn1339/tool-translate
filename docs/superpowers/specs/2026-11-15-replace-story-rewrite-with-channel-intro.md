# Thiết Kế: Thay Thế Tính Năng Xào Nấu Bằng Thêm Đoạn Giới Thiệu Kênh (Story Channel Intro)

## 1. Mục Tiêu & Bối Cảnh
- **Vị trí**: Studio Đọc Truyện & Tạo Audio (Story TTS Studio) - Thẻ số 4 trên Home Hub và `#story-tts-view`.
- **Yêu cầu**: Thay thế hoàn toàn thanh công cụ **"Xào Nấu AI"** (rewrite / paraphrase toàn bộ văn bản) thành tính năng **"Thêm Đoạn Giới Thiệu Kênh"** (Channel Intro).
- **Mục đích thực tế**: Khi làm video đọc truyện / podcast / review cho YouTube/TikTok (như Hạt Tiêu Vietsub), người sáng tạo cần một đoạn mở đầu nhận diện thương hiệu kênh (branding intro/hook) chèn vào đầu kịch bản thay vì xào xáo lại toàn bộ nội dung đã chuẩn bị sẵn.

---

## 2. Thiết Kế Tính Năng Chi Tiết

### 2.1. Giao Diện Người Dùng (`#story-intro-toolbar`)
Thay thế khối `.story-rewrite-toolbar` hiện tại bằng `.story-intro-toolbar`:
1. **Ô Nhập Tên Kênh (`#story-channel-name`)**:
   - Mặc định: `Hạt Tiêu Vietsub` (hoặc tên kênh người dùng nhập).
   - Tự động lưu vào `localStorage` (`story_channel_name`) để lần mở sau không cần gõ lại.
2. **Chọn Phong Cách / Mẫu Câu Giới Thiệu (`#story-intro-style`)**:
   - `truyencam`: 📖 Kể Chuyện Truyền Cảm ("Chào mừng các bạn đã quay trở lại với {kênh}. Hãy cùng lắng nghe câu chuyện hôm nay...")
   - `kich_tinh`: ⚡ Kịch Tính / Gay Cấn ("{kênh} xin chào các bạn! Hôm nay chúng ta sẽ cùng bước vào một câu chuyện đầy bất ngờ và kịch tính...")
   - `review`: 🎬 Review / Tóm Tắt ("Xin chào các bạn, đây là {kênh}. Hôm nay mình sẽ gửi tới các bạn bản tóm tắt trọn vẹn...")
   - `ai_hook`: ✨ AI Tự Động Viết Lời Dẫn Hook (Đọc lướt kịch bản và sáng tạo 1-2 câu mở đầu cực hút kèm tên kênh)
   - `custom`: ✍️ Tùy chỉnh (Cho phép người dùng tự gõ nội dung đoạn intro riêng)
3. **Ô Xem Trước & Tùy Chỉnh Nội Dung Intro (`#story-intro-custom-text`)**:
   - Tự động hiển thị câu giới thiệu tương ứng theo phong cách đã chọn.
   - Người dùng có thể chỉnh sửa trực tiếp câu từ theo ý muốn.
4. **Các Nút Thao Tác**:
   - `btn-story-insert-intro`: **"➕ Chèn Đoạn Giới Thiệu Vào Đầu Kịch Bản"**
     - Đưa đoạn giới thiệu lên đầu ô kịch bản `#story-raw-text`, tự ngắt dòng đôi cách câu chuyện.
     - Kiểm tra nếu đầu kịch bản đã chứa đoạn giới thiệu tương tự thì cảnh báo xác nhận tránh chèn lặp.
   - `btn-story-ai-intro`: **"✨ AI Viết Lời Dẫn Hook Mở Đầu"** (hiển thị khi chọn chế độ AI hoặc dưới dạng nút bổ trợ).

### 2.2. Backend API (`app/story_tts.py` & `app/main.py`)
1. **Endpoint mới**: `POST /api/story-tts/generate-intro`
   - Payload:
     ```json
     {
       "channel_name": "Hạt Tiêu Vietsub",
       "story_summary": "Đoạn trích đầu câu chuyện...",
       "style": "storytelling"
     }
     ```
   - Xử lý: Gọi Groq / Gemini với prompt chuyên biệt: Sinh 1-2 câu mở đầu cực kỳ cuốn hút, tự nhiên, mở đầu bằng lời chào kênh và dẫn dắt người nghe vào diễn biến ngay lập tức.
2. **Preset Templates**: Khai báo danh mục các mẫu giới thiệu chuẩn hóa sẵn trong backend và frontend.

---

## 3. Danh Sách Tệp Tác Động
1. `app/static/index.html`: Cập nhật HTML phần `#story-tts-view` (thay thế khối xào nấu bằng khối giới thiệu kênh), cập nhật mô tả thẻ số 4 tại `#home-view`.
2. `app/static/app.js`: Xóa logic gọi API xào nấu, thêm controller quản lý giới thiệu kênh (lưu tên kênh, đổi template, chèn vào kịch bản, gọi AI tạo intro).
3. `app/static/style.css`: Cập nhật CSS cho `.story-intro-toolbar` và các input/button liên quan.
4. `app/story_tts.py`: Thay thế/bổ sung hàm `generate_channel_intro()` phục vụ sinh lời dẫn hook mở đầu.
5. `app/main.py`: Cập nhật endpoint API cho `generate-intro`.
6. `tests/test_story_tts.py`: Cập nhật bộ unit test tương ứng.

