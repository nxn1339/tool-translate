# Implementation Plan: Phát hiện & Đánh dấu Câu sót Tiếng Trung và Tinh chỉnh Hán-Việt

- **Date:** 2026-11-05
- **Status:** Đã hoàn thành triển khai
- **Spec Reference:** `docs/superpowers/specs/2026-11-05-detect-untranslated-chinese-and-fix.md`
- **Model:** Gemini 4 Argon (Medium)

---

## Các Bước Triển Khai

### Phase 1: Bổ sung Từ Điển & Ngăn Chặn Lai Tạp Hán - Việt
- [x] `app/data/hanviet_dict.json` & `app/hanviet_builder.py`:
  - Thêm `毅:Nghị:yi`, `睿:Duệ:rui`, `屿:Dữ:yu` và bộ ký tự tên riêng thông dụng vào danh mục từ điển Hán - Việt (870 chữ).
  - Chạy `hanviet_builder.py` cập nhật `hanviet_dict.json`.
- [x] `app/hanviet.py`:
  - Trong `extract_chinese_names_in_text`:
    - Thêm kiểm tra nghiêm ngặt: Chỉ nhận diện khi toàn bộ ký tự trong cụm ứng viên đều có trong `char_to_hv`, ngăn chặn tuyệt đối sinh chuỗi lai tạp nửa Hán nửa Việt.
    - Thêm `NON_GIVEN_NAME_CHARS` chặn các động từ/hành động thường gặp sau tên người (`转`, `移`, `走`, `来`, `去`, `跑`, `看`, `说`, `死`, `逃`...) không để lọt vào tên riêng.

### Phase 2: Hậu Xử Lý Dịch Thuật & API Backend
- [x] `app/translator.py` & `app/groq_translator.py`:
  - Trong `refine_vietnamese_dub_line`: Thêm bước fallback `transliterate_remaining_hanzi` tự động chuyển 1-2 chữ Hán còn sót trong câu tiếng Việt sang âm Hán - Việt chuẩn (ví dụ `"Thẩm毅 chuyển đi"` -> `"Thẩm Nghị chuyển đi"`, `"Triệu睿"` -> `"Triệu Duệ"`).
  - Cấm để sót chữ Hán trong prompt của `groq_translator.py`.
- [x] `app/main.py`:
  - Trong `process_project_translate_worker`: Khi `failed_only=True`, target indices bao gồm cả câu có `translation_error`, câu rỗng, và các câu mà bản dịch vẫn còn chứa ký tự ngoại ngữ `detect_untranslated_foreign_chars`.

### Phase 3: Giao Diện Người Dùng (Frontend UI)
- [x] `app/static/index.html`:
  - Thêm nút `btn-filter-chinese` tại header của Bảng Phụ Đề & Bản Dịch:
    - Hiển thị số lượng câu sót tiếng Trung: `Sót tiếng Trung (<span id="count-chinese-warn">0</span>)`.
    - Bật/tắt lọc nhanh chỉ hiển thị các câu còn sót tiếng Trung.
- [x] `app/static/app.js`:
  - Trong `renderSegmentsTable`:
    - Phát hiện ký tự tiếng Trung / ngoại ngữ trong `seg.translation` bằng `FOREIGN_SCRIPT_REGEX`.
    - Thêm badge cảnh báo nổi bật: `Sót chữ Hán: <ký tự>` kèm viền màu cam và nền cảnh báo cho ô input dịch.
    - Cập nhật realtime khi người dùng gõ sửa trực tiếp trên ô input.
    - Tích hợp vào số đếm `failedTransCount` của nút `Dịch lại câu lỗi`.

### Phase 4: Kiểm Thử & Kiểm Chứng (TDD & Verification)
- [x] Chạy test Python với toàn bộ 21 câu bị sót chữ Hán thực tế trong project `3553adb1-1c86-411e-8db3-4fbd345ad464` (`Thẩm毅`, `Triệu睿`) đảm bảo chuyển sạch 100% thành `"Thẩm Nghị"`, `"Triệu Duệ"`.
- [x] Kiểm tra cú pháp Python (`python -m py_compile`).
- [x] Ghi lại bằng chứng nghiệm thu vào `docs/superpowers/evidence/2026-11-05-detect-untranslated-chinese-and-fix.md`.
