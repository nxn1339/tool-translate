# Verification Evidence: Phát hiện & Đánh dấu Câu sót Tiếng Trung và Tinh chỉnh Hán-Việt

- **Date:** 2026-11-05
- **Spec Reference:** `docs/superpowers/specs/2026-11-05-detect-untranslated-chinese-and-fix.md`
- **Plan Reference:** `docs/superpowers/plans/2026-11-05-detect-untranslated-chinese-and-fix.md`
- **Model:** Gemini 4 Argon (Medium)

---

## 1. Kiểm Chứng Biên Dịch & Cú Pháp (Syntax Verification)
- Chạy `python -m py_compile` với các module đã chỉnh sửa (`app/hanviet_builder.py`, `app/hanviet.py`, `app/translator.py`, `app/groq_translator.py`, `app/main.py`):
  - **Kết quả:** `All Python modules compiled cleanly!` (Exit code 0).

## 2. Kiểm Chứng Nhận Diện Tên & Chặn Động Từ (`app/hanviet.py`)
- Input test:
  - `'沈毅转走'` -> `[{'zh': '沈毅', 'hanviet': 'Thẩm Nghị', 'pinyin': 'shen yi'}]`
  - `'沈毅移走'` -> `[{'zh': '沈毅', 'hanviet': 'Thẩm Nghị', 'pinyin': 'shen yi'}]`
  - `'沈毅离开'` -> `[{'zh': '沈毅', 'hanviet': 'Thẩm Nghị', 'pinyin': 'shen yi'}]`
- Tiền xử lý `preprocess_chinese_segments`:
  - `['沈毅转走', '沈毅移走', '沈毅离开']` -> `['Thẩm Nghị 转走', 'Thẩm Nghị 移走', 'Thẩm Nghị 离开']` (không còn nuốt động từ `转`, `移` hay để sót chữ `毅`).

## 3. Kiểm Chứng Trên 21 Câu Sót Chữ Hán Thực Tế Của Project Hiện Tại
- Quét trên `app/projects/3553adb1-1c86-411e-8db3-4fbd345ad464/segments.json` phát hiện đúng 21 câu bị sót chữ Hán (`Thẩm毅` và `Triệu睿`):
  - Line 130: `Muốn đuổi Thẩm毅 đi` ===> `Muốn đuổi Thẩm Nghị đi`
  - Line 249: `Thẩm毅 chuyển đi` ===> `Thẩm Nghị chuyển đi`
  - Line 536: `Lục Vũ và Triệu睿 cùng đi` ===> `Lục Vũ và Triệu Duệ cùng đi`
  - Line 580: `Đừng nghe Triệu睿 giục` ===> `Đừng nghe Triệu Duệ giục`
  - Tất cả 21/21 câu đều được `detect_untranslated_foreign_chars` phát hiện chính xác và `refine_vietnamese_dub_line` xử lý sạch 100%.

## 4. Kiểm Chứng Giao Diện Cảnh Báo & Bộ Lọc (`app/static/index.html` & `app/static/app.js`)
- Dòng phụ đề có chứa chữ Trung Quốc / ký tự ngoại ngữ được gắn nhãn cảnh báo màu cam `Sót chữ Hán: 毅` (hoặc `睿`), ô input được tô viền cam nổi bật.
- Thanh công cụ Bảng Phụ Đề tự động hiện nút `Sót tiếng Trung (21)` cho phép bật/tắt lọc chỉ xem những câu bị sót chữ Hán để sửa nhanh, hoặc bấm `Dịch lại câu lỗi` để dịch lại tự động.

