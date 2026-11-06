# Kế Hoạch Triển Khai & Bằng Chứng Kiểm Chứng (Verification Report)

## 1. Danh Mục Thay Đổi Theo File
1. **[hanviet.py](file:///c:/project/tool-translate/app/hanviet.py)** & **[hanviet_dict.json](file:///c:/project/tool-translate/app/data/hanviet_dict.json)**:
   - Bổ sung 514 chữ Hán tên riêng và từ thông dụng vào từ điển Hán-Việt (nâng tổng số lên 1.388 chữ).
   - Mở rộng `COMMON_ZH_VOCABULARY_STOPWORDS`, `NON_GIVEN_NAME_CHARS`, `AMBIGUOUS_SURNAMES` chặn đứng hoàn toàn lỗi nhận nhầm từ thông dụng thành tên người.
   - Thêm hàm `normalize_ocr_character_names()` tự động đồng nhất các biến thể OCR 1 ký tự của tên nhân vật 3 chữ.
   - Thêm hàm `build_hanviet_glossary_hints()` tạo bảng gợi ý Hán-Việt sạch cho prompt AI.
2. **[translator.py](file:///c:/project/tool-translate/app/translator.py)**:
   - Cập nhật `preprocess_chinese_segments(texts, inline_hanviet=False)` để giữ nguyên câu tiếng Trung thuần khiết cho AI (`Groq`/`Gemini`), chỉ bật `inline_hanviet=True` khi dùng Google GTX.
   - Mở rộng lưới an toàn `transliterate_remaining_hanzi` trong `refine_vietnamese_dub_line`.
3. **[groq_translator.py](file:///c:/project/tool-translate/app/groq_translator.py)** & **[gemini_translator.py](file:///c:/project/tool-translate/app/gemini_translator.py)**:
   - Tích hợp `build_hanviet_glossary_hints()` và `character_glossary` vào Bước 1 (`analyze_story_context`) và Bước 2 (`groq_translate_chunk` / `gemini_translate_chunk`).
   - Bổ sung `prev_context_pairs` (Sliding Context Window 4 câu liền trước) để dịch mượt các câu bị ngắt qua nhiều dòng phụ đề.
4. **[merger.py](file:///c:/project/tool-translate/app/merger.py)** & **[main.py](file:///c:/project/tool-translate/app/main.py)**:
   - Chặn triệt để lỗi `NoneType` trong `os.path.exists()` khi câu phụ đề không có audio (`audio_path: None`).
   - Tự động tính bán kính `boxblur` an toàn theo chiều rộng/cao của vùng che.
   - Giữ nguyên `image_path` và `filename` của `logo_box` khi cập nhật `PATCH /api/projects/{id}` và sau khi xuất video xong.
5. **[index.html](file:///c:/project/tool-translate/app/static/index.html)** & **[app.js](file:///c:/project/tool-translate/app/static/app.js)**:
   - Hiển thị sẵn vùng tải ảnh Logo tại Bước 5, cho phép nhấp trực tiếp vào khung Logo trên video để tải ảnh, tự động bật Logo và lưu vào dự án qua `autoSaveProjectState()`.

## 2. Kết Quả Kiểm Chứng Thực Tế
- **Test 1 (Chống nhận diện nhầm tên người)**: Kiểm tra trên các câu chứa `任何人`, `都傻了`, `明天`, `对方能`, `胡言乱语`, `明明`, `年纪`, `终于` -> `0` từ bị nhận nhầm.
- **Test 2 (Chuẩn hóa tên nhân vật OCR & Bảng gợi ý Hán-Việt)**: Kiểm tra trên toàn bộ 1.601 câu của dự án `3553adb1-1c86-411e-8db3-4fbd345ad464` -> Trích xuất chính xác 15 thực thể tên riêng/địa danh (`沈毅 = Thẩm Nghị`, `江城 = Giang Thành`, `傅总 = Phó Tổng`, `苏晚晴 = Tô Vãn Tình`, `云栖 = Vân Thê`, `傅萱 = Phó Huyên`, `陆屿 = Lục Dữ`, `赵睿 = Triệu Duệ`...) và tự động sửa lỗi OCR `苏晚睛` -> `苏晚晴`.
- **Test 3 (Xuất video MP4 có segment `audio_path=None` và gắn Logo PNG)**: Chạy `merge_audio_segments_to_video()` với FFmpeg kết xuất thành công file MP4 có hardsub, vùng che mờ và watermark logo.

