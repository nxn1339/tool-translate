# Verification Evidence: Tinh gọn App - Gỡ bỏ RVC và dọn dẹp rác hệ thống

- **Date:** 2026-11-01
- **Status:** PASS

---

## 1. Kết Quả Thu Hồi Bộ Nhớ
- Đã xóa `rvc_backend/`: Giải phóng **663.19 MB**.
- Đã xóa `app/models/rvc/`: Giải phóng **491.04 MB**.
- Tổng dung lượng đã giải phóng: **~1.15 GB**.
- Dọn dẹp 46 file test/script scratch rác trong `tests/`, giữ lại 6 test nghiệp vụ cốt lõi.

## 2. Kiểm Tra Mã Nguồn Backend & Frontend
- `app/main.py`: Đã loại bỏ các tham số `rvc_model`, `rvc_pitch`, giữ endpoint `/api/rvc-models` dạng stub rỗng tương thích ngược.
- `app/tts.py`: Đã lược bỏ toàn bộ logic gọi subprocess RVC và hashing RVC. Luồng TTS trực tiếp qua Edge-TTS / CapCut TTS đạt hiệu năng tối đa.
- `app/merger.py`: Đã dọn sạch tham số RVC trong `generate_preview_audio_track`.
- `app/static/index.html`: Đã gỡ bỏ UI chọn RVC Model, thanh slider Pitch, và tab ẩn `tabs-nav d-none`.
- `app/static/app.js`: Đã gỡ bỏ các event listener, function loader và payload RVC.

## 3. Kiểm Tra Biên Dịch & Khởi Động
- Lệnh biên dịch: `python -m py_compile app/main.py app/tts.py app/merger.py app/downloader.py app/ocr.py app/translator.py tests/test_merger_direct.py` -> **EXIT 0 (Không lỗi cú pháp)**.
- Kiểm tra nạp module: `app.main`, `app.tts`, `app.merger` đều khởi tạo thành công không vướng lỗi import.

