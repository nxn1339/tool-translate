# Kế Hoạch Triển Khai: Studio Đọc Truyện & Tạo Audio (Story TTS Studio)

## Kế Hoạch Từng Bước Triển Khai (Implementation Steps)

### Bước 1: Chuẩn Hóa Toàn Bộ Giọng TikTok & Gỡ Giọng Microsoft (`app/capcut_tts.py` & `app/tts.py`)
- **Gỡ bỏ hoàn toàn**: 2 giọng Microsoft Edge-TTS (`female_hoaimy` và `male_namminh`) khỏi `VOICE_PRESETS` và `app/tts.py`.
- **Cập nhật `CAPCUT_VOICES`**: Bổ sung toàn bộ các giọng TikTok từ `Voice.json`, phân nhóm rõ ràng:
  - Nhóm TikTok Nữ (15 giọng): Cô Gái Hoạt Ngôn, Nhỏ Ngọt Ngào, Ban Mai, Mai, Giọng Nữ Phổ Thông, Review Phim Mới, Review Phim 2/3/4, Bản Tin Nữ, Bản Tin 1, Sunny Idol, Giọng Gái Mới Lớn, Giọng Bé, Quên Tên Tự Test.
  - Nhóm TikTok Nam (5 giọng): Thanh Niên Tự Tin, Giọng Nam Trầm, Alex Đại Đế, Kenny Đại Đế, Robot VN.
- **Đồng bộ hóa**: Cập nhật endpoint `/api/voices` trong `app/main.py` để cả công cụ **Dịch Phim & Lồng Tiếng** lẫn **Studio Đọc Truyện** đều dùng chung danh mục giọng TikTok này.

### Bước 2: Xây Dựng Backend Engine Mới (`app/story_tts.py`)
1. **Trích xuất transcript từ YouTube (`extract_youtube_transcript`)**:
   - Dùng `yt-dlp` lấy danh sách phụ đề có sẵn (ưu tiên `vi`, `auto-vi`, `en`, v.v.).
2. **Module Xào Nấu AI (`rewrite_story_content`)**:
   - Tích hợp với Groq API (`llama-3.3-70b-versatile`) hoặc Google Gemini API đã có sẵn key trong dự án.
   - Prompt lọc sạch câu rác video (chào hỏi, xin like/sub), viết lại câu từ trôi chảy, giàu hình ảnh, nhịp điệu kể chuyện cuốn hút.
3. **Phân đoạn kịch bản (`split_story_sentences`)**:
   - Chia văn bản theo câu tự nhiên, tránh ngắt giữa chừng.
4. **Sinh audio & Ghép nối (`batch_generate_and_stitch`)**:
   - Gọi CapCut TTS theo giọng nữ đã chọn cho từng câu.
   - Dùng FFmpeg ghép các file câu với khoảng lặng (silence gap: 300ms giữa câu, 700ms giữa đoạn).
   - Đo thời lượng chính xác bằng `ffprobe` và xuất file `.srt` đồng bộ.

### Bước 3: Đăng Ký Các API Endpoints Vào Backend (`app/main.py`)
- `GET /api/story-tts/voices`: Trả về danh sách giọng TikTok phân nhóm.
- `POST /api/story-tts/extract-youtube`: Nhận URL YouTube, trả về transcript gốc.
- `POST /api/story-tts/rewrite`: Nhận văn bản thô + phong cách xào nấu, gọi Groq/Gemini trả về kịch bản đã viết lại.
- `POST /api/story-tts/synthesize`: Nhận văn bản kịch bản + giọng đọc + tùy chọn khoảng nghỉ, tiến hành sinh audio và ghép nối.
- `GET /api/story-tts/download/{task_id}/audio`: Tải file MP3 thành phẩm.
- `GET /api/story-tts/download/{task_id}/srt`: Tải file SRT đồng bộ.

### Bước 4: Cập Nhật Giao Diện (`app/static/index.html` & `app/static/style.css`)
- **Đồng bộ bên Dịch Phim**:
  - Xóa bỏ optgroup "Giọng Chuẩn Edge-TTS" ở `<select id="voice-select-step3">` và `<select id="shared-voice-select">`.
  - Thay bằng danh mục giọng TikTok đầy đủ được phân nhóm (Nữ Hot TikTok, Review Phim, Nam Kể Chuyện).
- **Tại Trang Chủ (`#home-view`)**:
  - Mở khóa Thẻ số 4: Badge xanh `Sẵn Sàng Sử Dụng`, nút `Mở Studio Đọc Truyện`.
- **Thanh Header**: Thêm Tab navigation `Đọc Truyện TTS` (`#btn-nav-story-tts`).
- **Giao diện chính (`#story-tts-view`)**:
  - Khối nguồn vào: Dán kịch bản / tải file `.txt` HOẶC Nhập URL YouTube -> Bóc tách.
  - Khối kịch bản & Xào nấu: Textarea + Bộ nút chọn phong cách và nút "✨ Xào Nấu Kịch Bản".
  - Khối cấu hình giọng: Dropdown chọn giọng TikTok Nữ + Slider ngắt nghỉ câu + Nút "🎧 Tạo Audio Đọc Truyện (MP3 + SRT)".
  - Khối kết quả: Progress bar, Player nghe thử toàn bài, Nút Tải MP3, Nút Tải SRT.

### Bước 5: Xử Lý Tương Tác Frontend (`app/static/app.js`)
- Mở rộng hàm `switchView(viewName)` để hỗ trợ `#story-tts`.
- Xử lý các sự kiện click:
  - Bóc tách YouTube URL -> Điền kết quả vào textarea.
  - Bấm Xào Nấu AI -> Cập nhật kịch bản mới vào textarea.
  - Chọn giọng TikTok Nữ và bấm Tạo Audio.
  - Hiển thị tiến trình và kích hoạt audio player + các nút download khi xong.

### Bước 6: Kiểm Thử Độc Lập & Lưu Bằng Chứng (`evidence`)
- Tạo file kiểm thử `tests/test_story_tts.py`:
  - Test bóc tách nội dung từ YouTube URL.
  - Test prompt xào nấu với Groq/Gemini.
  - Test sinh audio với các giọng TikTok nữ và ghép file MP3 kèm SRT.
  - Test đồng bộ giọng mới bên Studio Dịch Phim (Step 4).
- Kiểm thử toàn diện giao diện trên trình duyệt.
- Lưu bằng chứng vào `docs/superpowers/evidence/2026-11-09-story-tts-studio.md`.
