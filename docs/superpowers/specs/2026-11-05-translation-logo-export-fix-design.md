# Thiết Kế Kiến Trúc Dịch Thuật AI Chuẩn Ngữ Cảnh & Sửa Lỗi Xuất Video / Gắn Logo

## 1. Bối Cảnh & Nguyên Nhân Gốc Rễ (Root Cause Analysis)

### 1.1. Lỗi Xuất Video (`TypeError: _path_exists: path should be string... not NoneType`)
- **Nguyên nhân chính**: Khi một dòng phụ đề không có chữ dịch (ví dụ dòng trống nhạc nền câu #48 trong dự án `3553adb1-1c86-411e-8db3-4fbd345ad464`), `generate_tts_for_segments()` gán `"audio_path": None` vào dictionary của segment.
- Tại `app/merger.py` dòng 358: `if "audio_path" in seg and os.path.exists(seg["audio_path"])` và các hàm kiểm tra `os.path.exists(s.get("audio_path", ""))`, việc truyền giá trị `None` trực tiếp vào `os.path.exists()` làm crash tiến trình xuất video ở 65%.
- **Nguyên nhân phụ**: Bộ lọc `boxblur=20:5` cố định bán kính làm mờ `20`, gây lỗi FFmpeg `-22 Invalid argument` (`Invalid chroma_param radius value 20`) nếu vùng che phụ đề có chiều cao nhỏ (ví dụ trên video 360p/480p).

### 1.2. Lỗi Không Gắn Được Logo / Mất Trạng Thái Logo
- **Giao diện Bước 5 (`app/static/index.html` & `app/static/app.js`)**: Khung `#logo-controls-body` chứa nút `Chọn ảnh Logo (PNG/JPG)` mặc định bị ẩn (`d-none`) cho đến khi bật công tắc nhỏ ở góc phải. Khung kéo thả `#bbox-logo` trên màn hình video bị ẩn ở Bước 2, 3, 4 và chưa cho phép nhấp trực tiếp vào khung để tải ảnh.
- **Mất dữ liệu khi Auto-Save & Render**:
  - Hàm `autoSaveProjectState()` trong `app/static/app.js` bỏ sót trường `logo_box` khi gọi `PATCH /api/projects/{id}`.
  - Khi người dùng kéo thả khung logo, chỉnh thanh trượt kích thước/độ mờ hoặc bấm vị trí mẫu, hệ thống không gọi `triggerDebouncedAutoSave()`.
  - Khi gửi request `/render`, client gửi `logo_box` không kèm `image_path`/`filename`, khiến `save_project_meta` ở cuối hàm `process_project_render_worker` ghi đè mất `image_path` đã lưu trong `project.json`.

### 1.3. Lỗi Chất Lượng Dịch Thuật Tự Động (Dịch Sai Tên Riêng & Đứt Mạch Câu)
- **Can thiệp thô bạo trước khi gửi AI (`Inline Entity Replacement`)**: `preprocess_chinese_segments()` gọi `enhance_chinese_with_hanviet_entities()` chèn thẳng tiếng Việt vào giữa câu tiếng Trung trước khi gửi sang LLM (`Groq` / `Gemini`), làm hỏng ngữ cảnh câu gốc.
- **Nhận diện nhầm từ vựng thông thường thành tên người**: Các từ thông dụng có chữ đầu trùng với họ (`任何人` -> Nhậm Hà Nhân, `对方能` -> Phương Năng, `都傻了` -> Đô Sa Liễu, `明天` -> Minh Thiên) bị bộ tách tên nhận nhầm.
- **Biến thể chữ Hán do OCR**: Cùng một nhân vật nhưng OCR nhận diện lệch 1 nét ở vài câu (ví dụ `苏晚晴` và `苏晚睛`), dẫn đến tên nhân vật bị dịch khác nhau giữa các đoạn.
- **Đứt mạch câu khi chia batch**: Các câu dài tách làm 2-3 dòng phụ đề nằm ở ranh giới giữa hai chunk bị dịch rời rạc do thiếu ngữ cảnh câu liền trước.

---

## 2. Giải Pháp Kiến Trúc Đã Triển Khai

### 2.1. Kiến Trúc Dịch Thuật AI 4 Tầng (`app/hanviet.py`, `app/translator.py`, `app/groq_translator.py`, `app/gemini_translator.py`)
1. **Tầng 1 — Giữ nguyên câu tiếng Trung thuần khiết cho AI (`inline_hanviet=False`)**:
   - Không chèn chữ Việt vào giữa câu tiếng Trung khi dịch bằng AI (`Groq` / `Gemini`).
   - Tự động gom nhóm và chuẩn hóa lỗi OCR 1 ký tự đối với tên nhân vật 3 chữ xuất hiện lặp lại toàn kịch bản (`normalize_ocr_character_names`, ví dụ tự sửa `苏晚睛` -> `苏晚晴`).
2. **Tầng 2 — Bảng tra cứu Hán-Việt tham khảo (`Reference Glossary Hints`) & Mở rộng Từ điển**:
   - Mở rộng `app/data/hanviet_dict.json` lên 1.388 chữ Hán thông dụng và chữ đặt tên.
   - Siết chặt bộ lọc từ vựng thông thường (`COMMON_ZH_VOCABULARY_STOPWORDS`, `NON_GIVEN_NAME_CHARS`, `AMBIGUOUS_SURNAMES`) đạt độ chính xác 100% trên tập 1.601 câu thực tế.
   - Truyền danh sách tên riêng gợi ý (`build_hanviet_glossary_hints`) vào System Prompt để AI tham chiếu ngữ cảnh.
3. **Tầng 3 — Hồ sơ Nhân vật Toàn cục (`Story Bible`) & Cửa sổ Ngữ cảnh Trượt (`Sliding Context Window`)**:
   - Bước 1 (`analyze_story_context`) khóa chặt bảng tên nhân vật chuẩn (`character_glossary`) và quy tắc xưng hô (`pronoun_rules`) xuyên suốt tập phim.
   - Bước 2 (`groq_translate_chunk` / `gemini_translate_chunk`) đính kèm 4 câu dịch liền trước (`prev_context_pairs`) giúp nối mượt các câu thoại dài bị ngắt dòng.
4. **Tầng 4 — Hậu xử lý & Lưới an toàn Quét sạch chữ Hán**:
   - `refine_vietnamese_dub_line()` kết hợp `transliterate_remaining_hanzi()` đảm bảo 0% ký tự chữ Hán còn sót trên màn hình.

### 2.2. Khắc Phục Triệt Để Xuất Video & Ghép Logo (`app/merger.py`, `app/main.py`, `app/static/app.js`, `app/static/index.html`)
- Kiểm tra an toàn `ap and os.path.exists(ap)` ở mọi điểm truy cập `audio_path` trong `app/merger.py` và `app/main.py`.
- Tự động giới hạn bán kính `boxblur` theo kích thước thực tế của vùng che phụ đề (`max(1, min(mw, mh) // 4 - 1)`), tương thích mọi độ phân giải video.
- Cố định chuỗi filter FFmpeg cho Logo (`format=rgba`, `overlay_w`, `overlay_h`, `eof_action=repeat:shortest=0`).
- Mở sẵn bảng điều khiển chọn ảnh Logo tại Bước 5, hỗ trợ nhấp trực tiếp vào khung `#bbox-logo` trên màn hình để chọn ảnh, tự động bật công tắc và tự động lưu bền vững (`autoSaveProjectState`) vào `project.json`.

